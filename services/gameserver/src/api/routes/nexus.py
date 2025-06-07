"""Central Nexus management API routes"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from src.auth.dependencies import get_current_user, get_current_player
from src.core.database import get_async_session
from src.models.user import User
from src.models.player import Player
from src.models.sector import Sector
from src.models.port import Port
from src.models.planet import Planet
from src.models.region import Region
from src.services.nexus_generation_service import nexus_generation_service
from src.services.regional_auth_service import regional_auth, RegionalPermission

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nexus", tags=["Central Nexus"])


class NexusGenerationRequest(BaseModel):
    """Request to generate or regenerate Central Nexus"""
    force_regenerate: bool = False
    preserve_player_data: bool = True
    districts_to_regenerate: Optional[List[str]] = None


class NexusStatsResponse(BaseModel):
    """Central Nexus statistics response"""
    total_sectors: int
    total_ports: int
    total_planets: int
    total_warp_gates: int
    districts: List[Dict[str, Any]]
    active_players: int
    daily_traffic: int


class DistrictInfoResponse(BaseModel):
    """District information response"""
    district_type: str
    name: str
    sector_range: tuple
    security_level: int
    development_level: int
    sectors_count: int
    ports_count: int
    planets_count: int
    special_features: Dict[str, Any]
    current_traffic: int


@router.post("/generate")
async def generate_central_nexus(
    request: NexusGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_player: Player = Depends(get_current_player),
    session: AsyncSession = Depends(get_async_session)
):
    """Generate the Central Nexus galaxy (Admin only)"""
    try:
        # Check admin permissions
        has_permission = await regional_auth.check_regional_permission(
            str(current_user.id),
            "central-nexus",
            RegionalPermission.GALAXY_ADMIN_FULL
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if nexus already exists
        existing_nexus = await session.execute(
            select(Region).where(Region.name == "central-nexus")
        )
        nexus_region = existing_nexus.scalar_one_or_none()
        
        if nexus_region and not request.force_regenerate:
            raise HTTPException(
                status_code=409,
                detail="Central Nexus already exists. Use force_regenerate=true to regenerate."
            )
        
        # Start generation in background
        background_tasks.add_task(
            generate_nexus_task,
            request.force_regenerate,
            request.preserve_player_data,
            request.districts_to_regenerate
        )
        
        return {
            "message": "Central Nexus generation started",
            "status": "in_progress",
            "estimated_completion": "15-20 minutes"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start nexus generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start generation")


@router.get("/status")
async def get_nexus_status(
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Get Central Nexus status and basic information"""
    try:
        # Check if nexus exists
        result = await session.execute(
            select(Region).where(Region.name == "central-nexus")
        )
        nexus_region = result.scalar_one_or_none()
        
        if not nexus_region:
            return {
                "exists": False,
                "status": "not_generated",
                "message": "Central Nexus has not been generated yet"
            }
        
        # Get basic statistics
        sectors_count = await session.execute(
            select(func.count(Sector.id)).where(Sector.region_id == nexus_region.id)
        )
        total_sectors = sectors_count.scalar() or 0
        
        ports_count = await session.execute(
            select(func.count(Port.id)).where(Port.region_id == nexus_region.id)
        )
        total_ports = ports_count.scalar() or 0
        
        planets_count = await session.execute(
            select(func.count(Planet.id)).where(Planet.region_id == nexus_region.id)
        )
        total_planets = planets_count.scalar() or 0
        
        return {
            "exists": True,
            "status": nexus_region.status,
            "nexus_id": str(nexus_region.id),
            "created_at": nexus_region.created_at.isoformat() if nexus_region.created_at else None,
            "total_sectors": total_sectors,
            "total_ports": total_ports,
            "total_planets": total_planets,
            "governance_type": nexus_region.governance_type,
            "economic_specialization": nexus_region.economic_specialization
        }
    
    except Exception as e:
        logger.error(f"Failed to get nexus status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.get("/stats", response_model=NexusStatsResponse)
async def get_nexus_statistics(
    session: AsyncSession = Depends(get_async_session)
):
    """Get comprehensive Central Nexus statistics"""
    try:
        # Get nexus region
        result = await session.execute(
            select(Region).where(Region.name == "central-nexus")
        )
        nexus_region = result.scalar_one_or_none()
        
        if not nexus_region:
            raise HTTPException(status_code=404, detail="Central Nexus not found")
        
        # Get total counts
        sectors_result = await session.execute(
            select(func.count(Sector.id)).where(Sector.region_id == nexus_region.id)
        )
        total_sectors = sectors_result.scalar() or 0
        
        ports_result = await session.execute(
            select(func.count(Port.id)).where(Port.region_id == nexus_region.id)
        )
        total_ports = ports_result.scalar() or 0
        
        planets_result = await session.execute(
            select(func.count(Planet.id)).where(Planet.region_id == nexus_region.id)
        )
        total_planets = planets_result.scalar() or 0
        
        # Get district breakdown
        districts_result = await session.execute(
            select(
                Sector.district,
                func.count(Sector.id).label('sector_count'),
                func.avg(Sector.security_level).label('avg_security'),
                func.avg(Sector.development_level).label('avg_development')
            ).where(
                Sector.region_id == nexus_region.id
            ).group_by(Sector.district)
        )
        
        districts = []
        for row in districts_result:
            districts.append({
                "district_type": row.district,
                "sectors": row.sector_count,
                "avg_security": round(row.avg_security, 1) if row.avg_security else 0,
                "avg_development": round(row.avg_development, 1) if row.avg_development else 0
            })
        
        # Get active players (would need player location tracking)
        active_players = 0  # Placeholder
        daily_traffic = 0   # Placeholder
        
        return NexusStatsResponse(
            total_sectors=total_sectors,
            total_ports=total_ports,
            total_planets=total_planets,
            total_warp_gates=0,  # Would need to implement warp gate counting
            districts=districts,
            active_players=active_players,
            daily_traffic=daily_traffic
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get nexus statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/districts")
async def get_districts_info(
    session: AsyncSession = Depends(get_async_session)
) -> List[DistrictInfoResponse]:
    """Get information about all districts in Central Nexus"""
    try:
        # Get nexus region
        result = await session.execute(
            select(Region).where(Region.name == "central-nexus")
        )
        nexus_region = result.scalar_one_or_none()
        
        if not nexus_region:
            raise HTTPException(status_code=404, detail="Central Nexus not found")
        
        # Get district information
        districts_result = await session.execute(
            select(
                Sector.district,
                func.count(Sector.id).label('sectors_count'),
                func.min(Sector.sector_number).label('min_sector'),
                func.max(Sector.sector_number).label('max_sector'),
                func.avg(Sector.security_level).label('avg_security'),
                func.avg(Sector.development_level).label('avg_development'),
                func.sum(Sector.traffic_level).label('total_traffic')
            ).where(
                Sector.region_id == nexus_region.id
            ).group_by(Sector.district)
        )
        
        districts = []
        district_names = {
            "commerce_central": "Commerce Central",
            "diplomatic_quarter": "Diplomatic Quarter", 
            "industrial_zone": "Industrial Zone",
            "residential_district": "Residential District",
            "transit_hub": "Transit Hub",
            "high_security_zone": "High Security Zone",
            "cultural_center": "Cultural Center",
            "research_campus": "Research Campus",
            "free_trade_zone": "Free Trade Zone",
            "gateway_plaza": "Gateway Plaza"
        }
        
        for row in districts_result:
            # Get ports and planets count for this district
            district_sectors = await session.execute(
                select(Sector.sector_number).where(
                    Sector.region_id == nexus_region.id,
                    Sector.district == row.district
                )
            )
            sector_numbers = [s.sector_number for s in district_sectors]
            
            ports_count = 0
            planets_count = 0
            if sector_numbers:
                ports_result = await session.execute(
                    select(func.count(Port.id)).where(
                        Port.sector_id.in_(sector_numbers)
                    )
                )
                ports_count = ports_result.scalar() or 0
                
                planets_result = await session.execute(
                    select(func.count(Planet.id)).where(
                        Planet.sector_id.in_(sector_numbers)
                    )
                )
                planets_count = planets_result.scalar() or 0
            
            districts.append(DistrictInfoResponse(
                district_type=row.district,
                name=district_names.get(row.district, row.district.replace('_', ' ').title()),
                sector_range=(row.min_sector, row.max_sector),
                security_level=int(row.avg_security) if row.avg_security else 0,
                development_level=int(row.avg_development) if row.avg_development else 0,
                sectors_count=row.sectors_count,
                ports_count=ports_count,
                planets_count=planets_count,
                special_features={},  # Would get from sector data
                current_traffic=row.total_traffic or 0
            ))
        
        return districts
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get districts info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get districts information")


@router.get("/districts/{district_type}")
async def get_district_details(
    district_type: str,
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Get detailed information about a specific district"""
    try:
        # Get nexus region
        result = await session.execute(
            select(Region).where(Region.name == "central-nexus")
        )
        nexus_region = result.scalar_one_or_none()
        
        if not nexus_region:
            raise HTTPException(status_code=404, detail="Central Nexus not found")
        
        # Get sectors in this district
        sectors_result = await session.execute(
            select(Sector).where(
                Sector.region_id == nexus_region.id,
                Sector.district == district_type
            ).limit(50)  # Limit for performance
        )
        sectors = sectors_result.scalars().all()
        
        if not sectors:
            raise HTTPException(status_code=404, detail="District not found")
        
        # Get sample ports and planets
        sector_numbers = [s.sector_number for s in sectors[:20]]  # Sample first 20
        
        ports_result = await session.execute(
            select(Port).where(Port.sector_id.in_(sector_numbers)).limit(10)
        )
        sample_ports = ports_result.scalars().all()
        
        planets_result = await session.execute(
            select(Planet).where(Planet.sector_id.in_(sector_numbers)).limit(10)
        )
        sample_planets = planets_result.scalars().all()
        
        return {
            "district_type": district_type,
            "total_sectors": len(sectors),
            "sector_range": (min(s.sector_number for s in sectors), max(s.sector_number for s in sectors)),
            "sample_sectors": [
                {
                    "sector_number": s.sector_number,
                    "security_level": s.security_level,
                    "development_level": s.development_level,
                    "traffic_level": s.traffic_level,
                    "special_features": s.special_features or {}
                }
                for s in sectors[:10]
            ],
            "sample_ports": [
                {
                    "sector_id": p.sector_id,
                    "name": p.name,
                    "port_class": p.port_class,
                    "port_type": p.port_type,
                    "docking_fee": p.docking_fee,
                    "security_level": p.security_level
                }
                for p in sample_ports
            ],
            "sample_planets": [
                {
                    "sector_id": p.sector_id,
                    "name": p.name,
                    "planet_type": p.planet_type,
                    "population": p.population,
                    "development_level": p.development_level,
                    "security_level": p.security_level
                }
                for p in sample_planets
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get district details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get district details")


@router.post("/districts/{district_type}/regenerate")
async def regenerate_district(
    district_type: str,
    background_tasks: BackgroundTasks,
    preserve_player_data: bool = True,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Regenerate a specific district (Admin only)"""
    try:
        # Check admin permissions
        has_permission = await regional_auth.check_regional_permission(
            str(current_user.id),
            "central-nexus",
            RegionalPermission.GALAXY_ADMIN_FULL
        )
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Start regeneration in background
        background_tasks.add_task(
            regenerate_district_task,
            district_type,
            preserve_player_data
        )
        
        return {
            "message": f"District {district_type} regeneration started",
            "status": "in_progress",
            "preserve_player_data": preserve_player_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start district regeneration: {e}")
        raise HTTPException(status_code=500, detail="Failed to start regeneration")


# Background task functions
async def generate_nexus_task(
    force_regenerate: bool,
    preserve_player_data: bool,
    districts_to_regenerate: Optional[List[str]]
):
    """Background task to generate Central Nexus"""
    try:
        async with get_async_session() as session:
            if districts_to_regenerate:
                # Regenerate specific districts
                for district_type in districts_to_regenerate:
                    await nexus_generation_service.regenerate_district(
                        session, district_type, preserve_player_data
                    )
            else:
                # Full generation
                result = await nexus_generation_service.generate_central_nexus(session)
            
            logger.info("Central Nexus generation completed successfully")
    
    except Exception as e:
        logger.error(f"Central Nexus generation failed: {e}")


async def regenerate_district_task(district_type: str, preserve_player_data: bool):
    """Background task to regenerate a specific district"""
    try:
        async with get_async_session() as session:
            result = await nexus_generation_service.regenerate_district(
                session, district_type, preserve_player_data
            )
            logger.info(f"District {district_type} regenerated successfully: {result}")
    
    except Exception as e:
        logger.error(f"District {district_type} regeneration failed: {e}")