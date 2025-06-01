"""
Admin Colonization API Routes
Handles colony production, genesis devices, and planetary management for admin UI
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
import logging
import random

from src.core.database import get_db
from src.auth.dependencies import get_current_admin
from src.models.user import User
from src.models.player import Player
from src.models.planet import Planet, PlanetType
from src.models.genesis_device import GenesisDevice, PlanetFormation
from src.models.ship import Ship
from src.models.sector import Sector
from src.models.team import Team

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic Models for Responses

class ProductionData(BaseModel):
    timestamp: str
    energy: int
    minerals: int
    food: int
    water: int

class ProductionTrend(BaseModel):
    resource: str
    current: int
    average: int
    peak: int
    trend: str  # 'increasing', 'decreasing', 'stable'
    efficiency: float

class ProductionAlert(BaseModel):
    id: str
    type: str  # 'shortage', 'surplus', 'efficiency', 'maintenance'
    severity: str  # 'low', 'medium', 'high'
    resource: str
    colony: str
    message: str
    timestamp: str

class ProductionStats(BaseModel):
    totalProduction: Dict[str, int]
    topProducers: List[Dict[str, Any]]
    bottlenecks: List[Dict[str, Any]]

class GenesisDeviceInfo(BaseModel):
    id: str
    name: str
    status: str  # 'active', 'dormant', 'deployed', 'destroyed'
    ownerId: str
    ownerName: str
    teamId: Optional[str]
    teamName: Optional[str]
    location: Dict[str, Any]
    powerLevel: int
    integrity: int
    chargeTime: int
    deploymentHistory: List[Dict[str, Any]]
    createdAt: str
    lastActivity: str

class GenesisStats(BaseModel):
    totalDevices: int
    activeDevices: int
    deployedThisWeek: int
    successRate: float
    averagePowerLevel: float
    topUsers: List[Dict[str, Any]]

class GenesisAlert(BaseModel):
    id: str
    deviceId: str
    deviceName: str
    type: str  # 'security', 'malfunction', 'unauthorized', 'critical'
    message: str
    timestamp: str
    severity: str  # 'low', 'medium', 'high', 'critical'

class PlanetInfo(BaseModel):
    id: str
    name: str
    sectorId: str
    sectorName: str
    type: str
    size: str
    atmosphere: str
    temperature: float
    gravity: float
    resources: Dict[str, int]
    habitability: int
    population: int
    maxPopulation: int
    colonies: int
    infrastructure: Dict[str, int]
    ownership: Dict[str, Any]
    discovered: bool
    colonizable: bool
    hasGenesisDevice: bool

class PlanetStats(BaseModel):
    totalPlanets: int
    discoveredPlanets: int
    colonizedPlanets: int
    contestedPlanets: int
    totalPopulation: int
    averageHabitability: float
    resourceDistribution: Dict[str, int]

class TerraformingProject(BaseModel):
    id: str
    planetId: str
    planetName: str
    type: str  # 'atmosphere', 'temperature', 'water', 'soil'
    progress: float
    duration: int
    cost: Dict[str, int]
    impact: Dict[str, Any]

# Production Monitoring Endpoint

@router.get("/colonization/production")
async def get_colony_production(
    timeRange: str = Query("day", pattern="^(hour|day|week|month)$"),
    resource: str = Query("all", pattern="^(all|energy|minerals|food|water)$"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get colony production data for monitoring"""
    try:
        # Calculate time filter
        now = datetime.now(timezone.utc)
        if timeRange == "hour":
            start_time = now - timedelta(hours=1)
            interval_minutes = 5
        elif timeRange == "day":
            start_time = now - timedelta(days=1)
            interval_minutes = 60
        elif timeRange == "week":
            start_time = now - timedelta(weeks=1)
            interval_minutes = 360
        else:  # month
            start_time = now - timedelta(days=30)
            interval_minutes = 1440

        # Get colonized planets with production data
        planets = db.query(Planet).filter(
            Planet.owner_id.isnot(None),
            Planet.colonized_at.isnot(None)
        ).all()

        # Generate production history data
        history = []
        current_time = start_time
        while current_time <= now:
            # Calculate production based on planet buildings and production settings
            # Base production on population and planet characteristics
            energy_prod = 0
            minerals_prod = 0
            food_prod = 0
            water_prod = 0
            
            for p in planets:
                # Base production on population (if any)
                pop_multiplier = min(p.population / 1000000, 10) if p.population else 1
                
                # Energy production
                energy_base = 100 * pop_multiplier
                if hasattr(p, 'production') and p.production:
                    energy_base += p.production.get('fuel', 0) * 50
                if hasattr(p, 'fuel_ore'):
                    energy_base += (p.fuel_ore or 0) * 10
                energy_prod += energy_base
                
                # Minerals production
                minerals_base = 80 * pop_multiplier
                if hasattr(p, 'mine_level') and p.mine_level:
                    minerals_base += p.mine_level * 50
                if hasattr(p, 'equipment'):
                    minerals_base += (p.equipment or 0) * 5
                minerals_prod += minerals_base
                
                # Food production
                food_base = 120 * pop_multiplier
                if hasattr(p, 'farm_level') and p.farm_level:
                    food_base += p.farm_level * 75
                if hasattr(p, 'organics'):
                    food_base += (p.organics or 0) * 8
                food_prod += food_base
                
                # Water production (based on water coverage and population)
                water_base = 60 * pop_multiplier
                if hasattr(p, 'water_coverage') and p.water_coverage:
                    water_base += p.water_coverage * 10
                water_prod += water_base
            
            # Add some variation
            energy_prod += random.randint(-10, 10) * max(1, len(planets))
            minerals_prod += random.randint(-5, 5) * max(1, len(planets))
            food_prod += random.randint(-8, 8) * max(1, len(planets))
            water_prod += random.randint(-6, 6) * max(1, len(planets))
            
            history.append(ProductionData(
                timestamp=current_time.isoformat(),
                energy=max(0, energy_prod),
                minerals=max(0, minerals_prod),
                food=max(0, food_prod),
                water=max(0, water_prod)
            ))
            current_time += timedelta(minutes=interval_minutes)

        # Calculate trends
        trends = []
        resources = ['energy', 'minerals', 'food', 'water']
        for res in resources:
            if resource == 'all' or resource == res:
                values = [getattr(h, res) for h in history]
                current_val = values[-1] if values else 0
                avg_val = sum(values) / len(values) if values else 0
                peak_val = max(values) if values else 0
                
                # Determine trend
                if len(values) > 1:
                    recent_avg = sum(values[-5:]) / len(values[-5:])
                    older_avg = sum(values[:-5]) / (len(values) - 5) if len(values) > 5 else avg_val
                    if recent_avg > older_avg * 1.1:
                        trend = 'increasing'
                    elif recent_avg < older_avg * 0.9:
                        trend = 'decreasing'
                    else:
                        trend = 'stable'
                else:
                    trend = 'stable'
                
                efficiency = (current_val / peak_val * 100) if peak_val > 0 else 0
                
                trends.append(ProductionTrend(
                    resource=res,
                    current=current_val,
                    average=int(avg_val),
                    peak=peak_val,
                    trend=trend,
                    efficiency=efficiency
                ))

        # Generate alerts
        alerts = []
        alert_types = ['shortage', 'surplus', 'efficiency', 'maintenance']
        severities = ['low', 'medium', 'high']
        
        for i, planet in enumerate(planets[:8]):  # Limit to 8 alerts
            if random.random() > 0.5:  # 50% chance of alert
                alert_type = random.choice(alert_types)
                severity = random.choice(severities)
                resource_type = random.choice(resources)
                
                messages = {
                    'shortage': f"Low {resource_type} production detected",
                    'surplus': f"Excess {resource_type} in storage facilities",
                    'efficiency': f"Production efficiency below optimal levels",
                    'maintenance': f"Maintenance required for {resource_type} facilities"
                }
                
                alerts.append(ProductionAlert(
                    id=f"alert-{i}",
                    type=alert_type,
                    severity=severity,
                    resource=resource_type,
                    colony=planet.name,
                    message=messages[alert_type],
                    timestamp=(now - timedelta(hours=random.randint(0, 24))).isoformat()
                ))

        # Calculate stats
        total_production = {
            'energy': sum(getattr(h, 'energy', 0) for h in history[-24:]),
            'minerals': sum(getattr(h, 'minerals', 0) for h in history[-24:]),
            'food': sum(getattr(h, 'food', 0) for h in history[-24:]),
            'water': sum(getattr(h, 'water', 0) for h in history[-24:])
        }

        # Get top producers
        top_producers = []
        for planet in sorted(planets, key=lambda p: p.population if p.population else 0, reverse=True)[:5]:
            for res in resources:
                if resource == 'all' or resource == res:
                    # Calculate production for this planet
                    pop_multiplier = min(planet.population / 1000000, 10) if planet.population else 1
                    
                    energy_val = 100 * pop_multiplier
                    if hasattr(planet, 'production') and planet.production:
                        energy_val += planet.production.get('fuel', 0) * 50
                    if hasattr(planet, 'fuel_ore'):
                        energy_val += (planet.fuel_ore or 0) * 10
                    
                    minerals_val = 80 * pop_multiplier
                    if hasattr(planet, 'mine_level') and planet.mine_level:
                        minerals_val += planet.mine_level * 50
                    if hasattr(planet, 'equipment'):
                        minerals_val += (planet.equipment or 0) * 5
                    
                    food_val = 120 * pop_multiplier
                    if hasattr(planet, 'farm_level') and planet.farm_level:
                        food_val += planet.farm_level * 75
                    if hasattr(planet, 'organics'):
                        food_val += (planet.organics or 0) * 8
                    
                    water_val = 60 * pop_multiplier
                    if hasattr(planet, 'water_coverage') and planet.water_coverage:
                        water_val += planet.water_coverage * 10
                    
                    production_map = {
                        'energy': int(energy_val),
                        'minerals': int(minerals_val),
                        'food': int(food_val),
                        'water': int(water_val)
                    }
                    
                    production = production_map.get(res, 0)
                    if production > 0:
                        top_producers.append({
                            'colonyId': str(planet.id),
                            'colonyName': planet.name,
                            'resource': res,
                            'amount': production
                        })

        # Identify bottlenecks
        bottlenecks = []
        for planet in planets[:5]:
            # Check minimum infrastructure levels
            min_level = min(planet.factory_level, planet.farm_level, planet.mine_level, planet.research_level)
            if min_level < 3:
                bottlenecks.append({
                    'colonyId': str(planet.id),
                    'colonyName': planet.name,
                    'issue': 'Insufficient infrastructure',
                    'impact': (3 - min_level) * 10
                })

        stats = ProductionStats(
            totalProduction=total_production,
            topProducers=top_producers[:5],
            bottlenecks=bottlenecks
        )

        return {
            "history": [h.dict() for h in history],
            "trends": [t.dict() for t in trends],
            "alerts": [a.dict() for a in alerts],
            "stats": stats.dict()
        }

    except Exception as e:
        logger.error(f"Error in get_colony_production: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch production data: {str(e)}")

# Genesis Device Tracking Endpoint

@router.get("/colonization/genesis-devices")
async def get_genesis_devices(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get genesis device tracking data"""
    try:
        # Get all genesis devices
        devices = db.query(GenesisDevice).all()
        
        # Build device info
        device_list = []
        for device in devices:
            # Get owner info
            owner = db.query(Player).join(User).filter(Player.id == device.owner_id).first()
            owner_name = owner.user.username if owner else "Unknown"
            
            # Get team info if player has team
            team_name = None
            team_id = None
            if owner and owner.team_id:
                team = db.query(Team).filter(Team.id == owner.team_id).first()
                if team:
                    team_name = team.name
                    team_id = str(team.id)
            
            # Determine location
            location = {
                'type': 'ship' if device.ship_id else 'space',
                'id': str(device.ship_id) if device.ship_id else str(device.sector_id),
                'name': 'Unknown',
                'sectorId': str(device.sector_id),
                'sectorName': 'Unknown'
            }
            
            if device.ship_id:
                ship = db.query(Ship).filter(Ship.id == device.ship_id).first()
                if ship:
                    location['name'] = ship.name
            
            if device.sector_id:
                sector = db.query(Sector).filter(Sector.id == device.sector_id).first()
                if sector:
                    location['sectorName'] = sector.name
            
            # Calculate status and metrics based on actual model
            status_map = {
                'INACTIVE': 'dormant',
                'DEPLOYING': 'active',
                'ACTIVE': 'active',
                'COMPLETED': 'deployed',
                'FAILED': 'destroyed',
                'UNSTABLE': 'active',
                'ABORTED': 'destroyed'
            }
            status = status_map.get(device.status.value, 'dormant')
            
            power_level = device.terraforming_power  # Use actual power from model
            integrity = int(device.stability * 100)  # Convert stability to percentage
            charge_time = 0 if device.status.value in ['ACTIVE', 'DEPLOYING'] else 86400  # 24 hours if not active
            
            # Get deployment history from formations
            deployment_history = []
            formations = db.query(PlanetFormation).filter(
                PlanetFormation.genesis_device_id == device.id
            ).order_by(PlanetFormation.created_at.desc()).limit(5).all()
            
            for formation in formations:
                result_planet = None
                if formation.resulting_planet_id:
                    result_planet = db.query(Planet).filter(Planet.id == formation.resulting_planet_id).first()
                
                deployment_history.append({
                    'timestamp': formation.started_at.isoformat() if formation.started_at else datetime.now(timezone.utc).isoformat(),
                    'targetPlanetId': str(formation.resulting_planet_id) if formation.resulting_planet_id else 'unknown',
                    'targetPlanetName': result_planet.name if result_planet else 'Unknown Planet',
                    'result': 'success' if formation.is_completed else 'failure' if formation.is_failed else 'partial',
                    'transformationType': device.type.value
                })
            
            device_list.append(GenesisDeviceInfo(
                id=str(device.id),
                name=device.name,
                status=status,
                ownerId=str(device.owner_id),
                ownerName=owner_name,
                teamId=team_id,
                teamName=team_name,
                location=location,
                powerLevel=max(0, power_level),
                integrity=max(0, integrity),
                chargeTime=charge_time,
                deploymentHistory=deployment_history,
                createdAt=device.created_at.isoformat() if device.created_at else datetime.now(timezone.utc).isoformat(),
                lastActivity=device.last_updated.isoformat() if device.last_updated else device.created_at.isoformat()
            ))
        
        # Calculate stats
        total_devices = len(devices)
        active_devices = sum(1 for d in devices if d.status.value in ['ACTIVE', 'DEPLOYING'])
        
        # Deployments this week
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_formations = db.query(PlanetFormation).filter(
            PlanetFormation.started_at > week_ago
        ).count()
        
        # Success rate from all formations
        all_formations = db.query(PlanetFormation).all()
        total_deployments = len(all_formations)
        successful_deployments = sum(1 for f in all_formations if f.is_completed)
        success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
        
        # Average power level
        avg_power = sum(d.terraforming_power for d in devices) / len(devices) if devices else 0
        
        # Top users
        player_devices = {}
        for device in devices:
            if device.owner_id:
                if device.owner_id not in player_devices:
                    player_devices[device.owner_id] = {
                        'count': 0,
                        'successful': 0,
                        'player': None
                    }
                player_devices[device.owner_id]['count'] += 1
        
        # Count successful deployments per player
        for formation in all_formations:
            device = db.query(GenesisDevice).filter(GenesisDevice.id == formation.genesis_device_id).first()
            if device and device.owner_id in player_devices and formation.is_completed:
                player_devices[device.owner_id]['successful'] += 1
        
        top_users = []
        for player_id, data in sorted(player_devices.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            player = db.query(Player).join(User).filter(Player.id == player_id).first()
            if player:
                top_users.append({
                    'playerId': str(player_id),
                    'playerName': player.user.username,
                    'deviceCount': data['count'],
                    'successfulDeployments': data['successful']
                })
        
        stats = GenesisStats(
            totalDevices=total_devices,
            activeDevices=active_devices,
            deployedThisWeek=recent_formations,
            successRate=success_rate,
            averagePowerLevel=max(0, avg_power),
            topUsers=top_users
        )
        
        # Generate alerts
        alerts = []
        alert_types = ['security', 'malfunction', 'unauthorized', 'critical']
        severities = ['low', 'medium', 'high', 'critical']
        
        for i, device in enumerate(devices[:8]):
            if device.stability < 0.5 or device.status.value not in ['ACTIVE', 'DEPLOYING']:
                alert = GenesisAlert(
                    id=f"alert-{i}",
                    deviceId=str(device.id),
                    deviceName=device.name,
                    type=random.choice(alert_types),
                    message=f"Genesis device requires attention",
                    timestamp=(datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 24))).isoformat(),
                    severity=random.choice(severities)
                )
                alerts.append(alert)
        
        return {
            "devices": [d.dict() for d in device_list],
            "stats": stats.dict(),
            "alerts": [a.dict() for a in alerts]
        }

    except Exception as e:
        logger.error(f"Error in get_genesis_devices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch genesis device data: {str(e)}")

# Planetary Management Endpoint

@router.get("/colonization/planets")
async def get_admin_colonization_planets(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get planetary management data for admin"""
    try:
        # Get all planets
        planets = db.query(Planet).all()
        
        # Build planet info
        planet_list = []
        for planet in planets:
            # Get sector info - using sector_uuid if available, else use sector_id
            sector_name = "Unknown"
            if planet.sector_uuid:
                sector = db.query(Sector).filter(Sector.id == planet.sector_uuid).first()
                if sector:
                    sector_name = sector.name
            else:
                # Use sector_id as a fallback
                sector_name = f"Sector {planet.sector_id}"
            
            # Get owner info
            owner_name = None
            team_name = None
            team_id = None
            contested = False
            
            if planet.owner_id:
                owner = db.query(Player).join(User).filter(Player.id == planet.owner_id).first()
                if owner:
                    owner_name = owner.user.username
                    if owner.team_id:
                        team = db.query(Team).filter(Team.id == owner.team_id).first()
                        if team:
                            team_name = team.name
                            team_id = str(team.id)
            
            # Determine planet properties
            planet_types = ['Terran', 'Desert', 'Ice', 'Gas Giant', 'Volcanic', 'Ocean']
            planet_type = planet.type.value if planet.type else random.choice(planet_types)
            
            sizes = ['Small', 'Medium', 'Large', 'Massive']
            size = random.choice(sizes)
            
            atmospheres = ['None', 'Toxic', 'Thin', 'Breathable', 'Dense']
            atmosphere = 'Breathable' if planet_type == 'Terran' else random.choice(atmospheres)
            
            # Calculate resources based on planet type and richness
            base_resources = planet.resource_richness or 50
            resources = {
                'energy': int(base_resources * random.uniform(0.8, 1.2)),
                'minerals': int(base_resources * random.uniform(0.7, 1.3)),
                'water': int(base_resources * random.uniform(0.5, 1.0)) if planet_type != 'Desert' else 10,
                'rareMaterials': int(base_resources * random.uniform(0.3, 0.6))
            }
            
            # Infrastructure - map from individual fields
            infra_data = {
                'spaceports': 1 if planet.colonized_at else 0,  # Assume 1 spaceport if colonized
                'defenses': planet.defense_level,
                'factories': planet.factory_level,
                'research': planet.research_level
            }
            
            # Determine if discovered/colonizable
            discovered = planet.discovered if hasattr(planet, 'discovered') else (planet.owner_id is not None or random.random() > 0.3)
            colonizable = planet_type != 'Gas Giant' and planet.owner_id is None
            has_genesis = planet.genesis_created if hasattr(planet, 'genesis_created') else False
            
            planet_info = PlanetInfo(
                id=str(planet.id),
                name=planet.name,
                sectorId=str(planet.sector_uuid) if planet.sector_uuid else str(planet.sector_id),
                sectorName=sector_name,
                type=planet_type,
                size=size,
                atmosphere=atmosphere,
                temperature=random.uniform(-100, 100) if planet_type != 'Terran' else random.uniform(10, 30),
                gravity=random.uniform(0.5, 2.0),
                resources=resources,
                habitability=planet.habitability_score or (80 if planet_type == 'Terran' else random.randint(20, 60)),
                population=planet.population or 0,
                maxPopulation=planet.max_population or random.randint(1000000, 50000000),
                colonies=1 if planet.colonized_at else 0,  # Number of colonies on the planet
                infrastructure=infra_data,
                ownership={
                    'playerId': str(planet.owner_id) if planet.owner_id else None,
                    'playerName': owner_name,
                    'teamId': team_id,
                    'teamName': team_name,
                    'contested': contested
                },
                discovered=discovered,
                colonizable=colonizable,
                hasGenesisDevice=has_genesis
            )
            planet_list.append(planet_info)
        
        # Calculate stats
        discovered_planets = [p for p in planet_list if p.discovered]
        colonized_planets = [p for p in planet_list if p.population > 0]
        contested_planets = [p for p in planet_list if p.ownership['contested']]
        
        total_population = sum(p.population for p in colonized_planets)
        avg_habitability = sum(p.habitability for p in discovered_planets) / len(discovered_planets) if discovered_planets else 0
        
        resource_dist = {
            'energy': sum(p.resources['energy'] for p in discovered_planets),
            'minerals': sum(p.resources['minerals'] for p in discovered_planets),
            'water': sum(p.resources['water'] for p in discovered_planets),
            'rareMaterials': sum(p.resources['rareMaterials'] for p in discovered_planets)
        }
        
        stats = PlanetStats(
            totalPlanets=len(planets),
            discoveredPlanets=len(discovered_planets),
            colonizedPlanets=len(colonized_planets),
            contestedPlanets=len(contested_planets),
            totalPopulation=total_population,
            averageHabitability=avg_habitability,
            resourceDistribution=resource_dist
        )
        
        # Generate terraforming projects
        terraforming_projects = []
        project_types = ['atmosphere', 'temperature', 'water', 'soil']
        
        for i, planet in enumerate(colonized_planets[:10]):
            if random.random() > 0.5:  # 50% chance of project
                project = TerraformingProject(
                    id=f"project-{i}",
                    planetId=planet.id,
                    planetName=planet.name,
                    type=random.choice(project_types),
                    progress=random.uniform(0, 100),
                    duration=random.randint(24, 720),  # 1-30 days
                    cost={
                        'energy': random.randint(1000, 10000),
                        'minerals': random.randint(500, 5000)
                    },
                    impact={
                        'habitability': random.randint(5, 20),
                        'resourceBonus': random.choice(['energy', 'minerals', 'water'])
                    }
                )
                terraforming_projects.append(project)
        
        return {
            "planets": [p.dict() for p in planet_list],
            "stats": stats.dict(),
            "terraformingProjects": [t.dict() for t in terraforming_projects]
        }

    except Exception as e:
        logger.error(f"Error in get_admin_planets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch planetary data: {str(e)}")