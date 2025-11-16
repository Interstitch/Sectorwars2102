"""
Planetary management service for handling planet operations.

This service manages planetary colonization, resource allocation,
building construction, defenses, and sieges.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from src.models.player import Player
from src.models.planet import Planet, player_planets
from src.models.sector import Sector
from src.models.genesis_device import GenesisDevice, GenesisType, GenesisStatus, PlanetFormation
from src.models.team import Team

logger = logging.getLogger(__name__)


class PlanetaryService:
    """Service for managing planetary operations."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_player_planets(self, player_id: UUID) -> List[Dict[str, Any]]:
        """Get all planets owned by a player."""
        # Get planets through the association table
        planets = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            player_planets.c.player_id == player_id
        ).all()
        
        result = []
        for planet in planets:
            planet_data = self._format_planet_data(planet)
            result.append(planet_data)
            
        return result
        
    def get_planet_details(self, planet_id: UUID, player_id: UUID) -> Dict[str, Any]:
        """Get detailed information about a specific planet."""
        # Verify planet ownership
        planet = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            and_(
                Planet.id == planet_id,
                player_planets.c.player_id == player_id
            )
        ).first()
        
        if not planet:
            raise ValueError("Planet not found or not owned by player")
            
        return self._format_planet_data(planet)
        
    def allocate_colonists(
        self,
        planet_id: UUID,
        player_id: UUID,
        fuel: int,
        organics: int,
        equipment: int
    ) -> Dict[str, Any]:
        """Allocate colonists to different production areas."""
        # Verify ownership
        planet = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            and_(
                Planet.id == planet_id,
                player_planets.c.player_id == player_id
            )
        ).first()
        
        if not planet:
            raise ValueError("Planet not found or not owned by player")
            
        # Validate allocation totals
        total_allocated = fuel + organics + equipment
        if total_allocated > planet.colonists:
            raise ValueError(f"Cannot allocate {total_allocated} colonists, only {planet.colonists} available")
            
        # Update allocations
        planet.fuel_allocation = fuel
        planet.organics_allocation = organics
        planet.equipment_allocation = equipment
        
        # Calculate production rates based on allocations
        production_rates = self._calculate_production_rates(planet)
        
        self.db.commit()
        self.db.refresh(planet)
        
        return {
            "success": True,
            "allocations": {
                "fuel": planet.fuel_allocation,
                "organics": planet.organics_allocation,
                "equipment": planet.equipment_allocation,
                "unused": planet.colonists - total_allocated
            },
            "productionRates": production_rates
        }
        
    def upgrade_building(
        self,
        planet_id: UUID,
        player_id: UUID,
        building_type: str,
        target_level: int
    ) -> Dict[str, Any]:
        """Upgrade a building on a planet."""
        # Verify ownership
        planet = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            and_(
                Planet.id == planet_id,
                player_planets.c.player_id == player_id
            )
        ).first()
        
        if not planet:
            raise ValueError("Planet not found or not owned by player")
            
        # Get current building level
        current_level = self._get_building_level(planet, building_type)
        
        if target_level <= current_level:
            raise ValueError(f"Target level must be higher than current level ({current_level})")
            
        # Calculate upgrade cost
        cost = self._calculate_upgrade_cost(building_type, current_level, target_level)
        
        # Check if player can afford
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if player.credits < cost["credits"]:
            raise ValueError("Insufficient credits for upgrade")
            
        # Deduct cost
        player.credits -= cost["credits"]
        
        # Update building level
        self._set_building_level(planet, building_type, target_level)
        
        # Calculate completion time (1 hour per level)
        completion_time = datetime.utcnow() + timedelta(hours=(target_level - current_level))
        
        self.db.commit()
        
        return {
            "success": True,
            "buildingType": building_type,
            "newLevel": target_level,
            "completionTime": completion_time.isoformat(),
            "cost": cost
        }
        
    def update_defenses(
        self,
        planet_id: UUID,
        player_id: UUID,
        turrets: Optional[int] = None,
        shields: Optional[int] = None,
        drones: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update planetary defenses."""
        # Verify ownership
        planet = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            and_(
                Planet.id == planet_id,
                player_planets.c.player_id == player_id
            )
        ).first()

        if not planet:
            raise ValueError("Planet not found or not owned by player")

        # Update defenses if provided
        if turrets is not None:
            planet.defense_turrets = max(0, turrets)
        if shields is not None:
            planet.defense_shields = max(0, shields)
        if drones is not None:
            planet.defense_drones = max(0, drones)

        # Calculate total defense power
        defense_power = (
            planet.defense_turrets * 10 +
            planet.defense_shields * 5 +
            planet.defense_drones * 2
        )

        self.db.commit()
        self.db.refresh(planet)

        return {
            "success": True,
            "defenses": {
                "turrets": planet.defense_turrets,
                "shields": planet.defense_shields,
                "drones": planet.defense_drones
            },
            "defensePower": defense_power
        }
        
    def deploy_genesis_device(
        self,
        player_id: UUID,
        sector_id: UUID,
        planet_name: str,
        planet_type: str
    ) -> Dict[str, Any]:
        """Deploy a genesis device to create a new planet."""
        # Check if player has genesis devices
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise ValueError("Player not found")
            
        if player.genesis_devices <= 0:
            raise ValueError("No genesis devices available")
            
        # Verify sector exists
        sector = self.db.query(Sector).filter(Sector.id == sector_id).first()
        if not sector:
            raise ValueError("Sector not found")
            
        # Check if sector already has maximum planets (let's say 5)
        existing_planets = self.db.query(func.count(Planet.id)).filter(
            Planet.sector_id == sector_id
        ).scalar()
        
        if existing_planets >= 5:
            raise ValueError("Sector already has maximum number of planets")
            
        # Create genesis device deployment
        genesis = GenesisDevice(
            player_id=player_id,
            sector_id=sector_id,
            genesis_type=planet_type,
            status=GenesisStatus.DEPLOYED,
            deployed_at=datetime.utcnow()
        )
        
        # Deployment takes 24 hours
        deployment_time = 24 * 3600  # seconds
        completion_time = datetime.utcnow() + timedelta(seconds=deployment_time)
        
        # Create planet formation record
        formation = PlanetFormation(
            genesis_device_id=genesis.id,
            sector_id=sector_id,
            planet_name=planet_name,
            planet_type=planet_type,
            started_at=datetime.utcnow(),
            completion_at=completion_time
        )
        
        # Deduct genesis device
        player.genesis_devices -= 1
        
        # Create the planet immediately for gameplay purposes
        planet = Planet(
            name=planet_name,
            sector_id=sector_id,
            planet_type=planet_type,
            colonists=100,  # Start with 100 colonists
            max_colonists=10000,  # Base max
            fuel_ore=100,
            organics=100,
            equipment=100,
            drones=0
        )
        
        self.db.add(genesis)
        self.db.add(formation)
        self.db.add(planet)
        self.db.commit()
        self.db.refresh(planet)
        
        # Add planet to player's planets
        self.db.execute(
            player_planets.insert().values(
                player_id=player_id,
                planet_id=planet.id
            )
        )
        self.db.commit()
        
        return {
            "success": True,
            "planetId": str(planet.id),
            "deploymentTime": deployment_time,
            "genesisDevicesRemaining": player.genesis_devices
        }
        
    def set_specialization(
        self,
        planet_id: UUID,
        player_id: UUID,
        specialization: str
    ) -> Dict[str, Any]:
        """Set planet specialization."""
        # Verify ownership
        planet = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            and_(
                Planet.id == planet_id,
                player_planets.c.player_id == player_id
            )
        ).first()
        
        if not planet:
            raise ValueError("Planet not found or not owned by player")
            
        # Validate specialization
        valid_specializations = ["agricultural", "industrial", "military", "research", "balanced"]
        if specialization not in valid_specializations:
            raise ValueError(f"Invalid specialization. Must be one of: {valid_specializations}")
            
        planet.specialization = specialization
        
        # Calculate bonuses based on specialization
        bonuses = self._calculate_specialization_bonuses(specialization)
        
        self.db.commit()
        
        return {
            "success": True,
            "specialization": specialization,
            "bonuses": bonuses
        }
        
    def get_siege_status(self, planet_id: UUID, player_id: UUID) -> Dict[str, Any]:
        """Get siege status of a planet."""
        # Verify ownership
        planet = self.db.query(Planet).join(
            player_planets,
            Planet.id == player_planets.c.planet_id
        ).filter(
            and_(
                Planet.id == planet_id,
                player_planets.c.player_id == player_id
            )
        ).first()
        
        if not planet:
            raise ValueError("Planet not found or not owned by player")
            
        # Check if planet is under siege
        # For now, return not under siege
        # TODO: Implement siege mechanics
        
        return {
            "underSiege": False,
            "siegeDetails": None
        }
        
    # Helper methods
    
    def _format_planet_data(self, planet: Planet) -> Dict[str, Any]:
        """Format planet data for API response."""
        sector = planet.sector if planet.sector else None
        
        # Calculate production rates
        production_rates = self._calculate_production_rates(planet)
        
        # Get building data
        buildings = self._get_buildings_data(planet)
        
        # Calculate unused colonists
        total_allocated = (
            (planet.fuel_allocation or 0) +
            (planet.organics_allocation or 0) +
            (planet.equipment_allocation or 0)
        )
        
        return {
            "id": str(planet.id),
            "name": planet.name,
            "sectorId": str(planet.sector_id) if planet.sector_id else None,
            "sectorName": sector.name if sector else "Unknown",
            "planetType": planet.planet_type or "terran",
            "colonists": planet.colonists,
            "maxColonists": planet.max_colonists,
            "productionRates": production_rates,
            "allocations": {
                "fuel": planet.fuel_allocation or 0,
                "organics": planet.organics_allocation or 0,
                "equipment": planet.equipment_allocation or 0,
                "unused": planet.colonists - total_allocated
            },
            "buildings": buildings,
            "defenses": {
                "turrets": planet.defense_turrets or 0,
                "shields": planet.defense_shields or 0,
                "drones": planet.defense_drones or 0
            },
            "underSiege": False,  # TODO: Implement siege detection
            "siegeDetails": None
        }
        
    def _calculate_production_rates(self, planet: Planet) -> Dict[str, float]:
        """Calculate production rates based on allocations and buildings."""
        base_rate = 10  # Base production per colonist per day
        
        # Get building levels
        factory_level = planet.factory_level or 0
        farm_level = planet.farm_level or 0
        mine_level = planet.mine_level or 0
        
        # Calculate rates with building bonuses
        fuel_rate = (planet.fuel_allocation or 0) * base_rate * (1 + mine_level * 0.1)
        organics_rate = (planet.organics_allocation or 0) * base_rate * (1 + farm_level * 0.1)
        equipment_rate = (planet.equipment_allocation or 0) * base_rate * (1 + factory_level * 0.1)
        
        # Colonist growth rate (1% per day base)
        colonist_rate = planet.colonists * 0.01
        
        # Apply specialization bonuses
        if planet.specialization:
            bonuses = self._calculate_specialization_bonuses(planet.specialization)
            production_bonus = bonuses["production"]
            
            fuel_rate *= production_bonus.get("fuel", 1.0)
            organics_rate *= production_bonus.get("organics", 1.0)
            equipment_rate *= production_bonus.get("equipment", 1.0)
            colonist_rate *= production_bonus.get("colonists", 1.0)
            
        return {
            "fuel": round(fuel_rate, 2),
            "organics": round(organics_rate, 2),
            "equipment": round(equipment_rate, 2),
            "colonists": round(colonist_rate, 2)
        }
        
    def _get_buildings_data(self, planet: Planet) -> List[Dict[str, Any]]:
        """Get building data for a planet."""
        buildings = []
        
        # Factory
        if planet.factory_level and planet.factory_level > 0:
            buildings.append({
                "type": "factory",
                "level": planet.factory_level,
                "upgrading": False,
                "completionTime": None
            })
            
        # Farm
        if planet.farm_level and planet.farm_level > 0:
            buildings.append({
                "type": "farm",
                "level": planet.farm_level,
                "upgrading": False,
                "completionTime": None
            })
            
        # Mine
        if planet.mine_level and planet.mine_level > 0:
            buildings.append({
                "type": "mine",
                "level": planet.mine_level,
                "upgrading": False,
                "completionTime": None
            })
            
        # Defense
        if planet.defense_level and planet.defense_level > 0:
            buildings.append({
                "type": "defense",
                "level": planet.defense_level,
                "upgrading": False,
                "completionTime": None
            })
            
        # Research
        if planet.research_level and planet.research_level > 0:
            buildings.append({
                "type": "research",
                "level": planet.research_level,
                "upgrading": False,
                "completionTime": None
            })
            
        return buildings
        
    def _get_building_level(self, planet: Planet, building_type: str) -> int:
        """Get current level of a building."""
        building_map = {
            "factory": planet.factory_level or 0,
            "farm": planet.farm_level or 0,
            "mine": planet.mine_level or 0,
            "defense": planet.defense_level or 0,
            "research": planet.research_level or 0
        }
        return building_map.get(building_type, 0)
        
    def _set_building_level(self, planet: Planet, building_type: str, level: int):
        """Set building level."""
        if building_type == "factory":
            planet.factory_level = level
        elif building_type == "farm":
            planet.farm_level = level
        elif building_type == "mine":
            planet.mine_level = level
        elif building_type == "defense":
            planet.defense_level = level
        elif building_type == "research":
            planet.research_level = level
            
    def _calculate_upgrade_cost(self, building_type: str, current_level: int, target_level: int) -> Dict[str, Any]:
        """Calculate cost to upgrade a building."""
        base_cost = 1000
        cost_per_level = base_cost * (target_level - current_level) * (target_level + current_level) // 2
        
        return {
            "credits": cost_per_level,
            "resources": {
                "equipment": cost_per_level // 100
            }
        }
        
    def _calculate_specialization_bonuses(self, specialization: str) -> Dict[str, Any]:
        """Calculate bonuses based on planet specialization."""
        bonuses = {
            "agricultural": {
                "production": {"fuel": 0.8, "organics": 1.5, "equipment": 0.8, "colonists": 1.2},
                "defense": 0.9,
                "research": 0.8
            },
            "industrial": {
                "production": {"fuel": 0.9, "organics": 0.8, "equipment": 1.5, "colonists": 0.9},
                "defense": 1.0,
                "research": 0.9
            },
            "military": {
                "production": {"fuel": 0.9, "organics": 0.9, "equipment": 1.1, "colonists": 0.8},
                "defense": 1.5,
                "research": 0.8
            },
            "research": {
                "production": {"fuel": 0.8, "organics": 0.8, "equipment": 0.9, "colonists": 0.9},
                "defense": 0.8,
                "research": 1.5
            },
            "balanced": {
                "production": {"fuel": 1.0, "organics": 1.0, "equipment": 1.0, "colonists": 1.0},
                "defense": 1.0,
                "research": 1.0
            }
        }
        
        return bonuses.get(specialization, bonuses["balanced"])