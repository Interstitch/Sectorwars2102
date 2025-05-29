"""
Faction service for managing faction relationships, reputation, and missions.
"""

from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from src.models.faction import Faction, FactionType, FactionMission
from src.models.reputation import Reputation, ReputationLevel
from src.models.player import Player
from src.models.sector import Sector
from src.services.websocket_service import ConnectionManager

logger = logging.getLogger(__name__)
manager = ConnectionManager()


class FactionService:
    """Service for managing faction-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_factions(self) -> List[Faction]:
        """Get all factions in the game."""
        return self.db.query(Faction).all()
    
    async def get_faction_by_id(self, faction_id: UUID) -> Optional[Faction]:
        """Get a specific faction by ID."""
        return self.db.query(Faction).filter(Faction.id == faction_id).first()
    
    async def get_faction_by_type(self, faction_type: FactionType) -> Optional[Faction]:
        """Get a faction by its type."""
        return self.db.query(Faction).filter(Faction.faction_type == faction_type).first()
    
    async def get_player_reputation(self, player_id: UUID, faction_id: UUID) -> Optional[Reputation]:
        """Get a player's reputation with a specific faction."""
        return self.db.query(Reputation).filter(
            and_(
                Reputation.player_id == player_id,
                Reputation.faction_id == faction_id
            )
        ).first()
    
    async def get_all_player_reputations(self, player_id: UUID) -> List[Reputation]:
        """Get all reputation records for a player."""
        return self.db.query(Reputation).filter(
            Reputation.player_id == player_id
        ).all()
    
    async def initialize_player_reputations(self, player_id: UUID) -> List[Reputation]:
        """Initialize reputation records for a new player with all factions."""
        factions = await self.get_all_factions()
        reputations = []
        
        for faction in factions:
            # Check if reputation already exists
            existing = await self.get_player_reputation(player_id, faction.id)
            if existing:
                reputations.append(existing)
                continue
            
            # Create new reputation record
            reputation = Reputation(
                player_id=player_id,
                faction_id=faction.id,
                current_value=0,
                current_level=ReputationLevel.NEUTRAL,
                title="Neutral",
                trade_modifier=0.0,
                port_access_level=0,
                combat_response="neutral"
            )
            self.db.add(reputation)
            reputations.append(reputation)
        
        self.db.commit()
        return reputations
    
    async def update_reputation(
        self, 
        player_id: UUID, 
        faction_id: UUID, 
        change: int,
        reason: str = "Unknown"
    ) -> Reputation:
        """
        Update a player's reputation with a faction.
        
        Args:
            player_id: The player's ID
            faction_id: The faction's ID
            change: The reputation change (positive or negative)
            reason: The reason for the change
            
        Returns:
            Updated reputation record
        """
        reputation = await self.get_player_reputation(player_id, faction_id)
        if not reputation:
            # Initialize if doesn't exist
            await self.initialize_player_reputations(player_id)
            reputation = await self.get_player_reputation(player_id, faction_id)
        
        old_value = reputation.current_value
        old_level = reputation.current_level
        
        # Update reputation value (clamped between -800 and +800)
        reputation.current_value = max(-800, min(800, reputation.current_value + change))
        
        # Update reputation level based on new value
        reputation.current_level = self._calculate_reputation_level(reputation.current_value)
        reputation.title = self._get_reputation_title(reputation.current_level)
        
        # Update effects
        reputation.trade_modifier = self._calculate_trade_modifier(reputation.current_value)
        reputation.port_access_level = self._calculate_port_access_level(reputation.current_value)
        reputation.combat_response = self._calculate_combat_response(reputation.current_value)
        
        # Add to history
        if not reputation.history:
            reputation.history = []
        reputation.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "old_value": old_value,
            "new_value": reputation.current_value,
            "change": change,
            "reason": reason
        })
        
        reputation.last_updated = datetime.utcnow()
        self.db.commit()
        
        # Send WebSocket notification if reputation level changed
        if old_level != reputation.current_level:
            await manager.send_to_player(str(player_id), {
                "type": "reputation_changed",
                "faction_id": str(faction_id),
                "faction_name": reputation.faction.name,
                "old_level": old_level.value,
                "new_level": reputation.current_level.value,
                "old_value": old_value,
                "new_value": reputation.current_value,
                "title": reputation.title
            })
        
        logger.info(f"Updated reputation for player {player_id} with faction {faction_id}: {old_value} -> {reputation.current_value}")
        return reputation
    
    def _calculate_reputation_level(self, value: int) -> ReputationLevel:
        """Calculate reputation level from numeric value."""
        if value >= 700:
            return ReputationLevel.EXALTED
        elif value >= 600:
            return ReputationLevel.REVERED
        elif value >= 500:
            return ReputationLevel.HONORED
        elif value >= 400:
            return ReputationLevel.VALUED
        elif value >= 300:
            return ReputationLevel.RESPECTED
        elif value >= 200:
            return ReputationLevel.TRUSTED
        elif value >= 100:
            return ReputationLevel.ACKNOWLEDGED
        elif value >= 50:
            return ReputationLevel.RECOGNIZED
        elif value >= -50:
            return ReputationLevel.NEUTRAL
        elif value >= -100:
            return ReputationLevel.QUESTIONABLE
        elif value >= -200:
            return ReputationLevel.SUSPICIOUS
        elif value >= -300:
            return ReputationLevel.UNTRUSTWORTHY
        elif value >= -400:
            return ReputationLevel.SMUGGLER
        elif value >= -500:
            return ReputationLevel.PIRATE
        elif value >= -600:
            return ReputationLevel.OUTLAW
        elif value >= -700:
            return ReputationLevel.CRIMINAL
        else:
            return ReputationLevel.PUBLIC_ENEMY
    
    def _get_reputation_title(self, level: ReputationLevel) -> str:
        """Get display title for reputation level."""
        titles = {
            ReputationLevel.EXALTED: "Exalted",
            ReputationLevel.REVERED: "Revered",
            ReputationLevel.HONORED: "Honored",
            ReputationLevel.VALUED: "Valued",
            ReputationLevel.RESPECTED: "Respected",
            ReputationLevel.TRUSTED: "Trusted",
            ReputationLevel.ACKNOWLEDGED: "Acknowledged",
            ReputationLevel.RECOGNIZED: "Recognized",
            ReputationLevel.NEUTRAL: "Neutral",
            ReputationLevel.QUESTIONABLE: "Questionable",
            ReputationLevel.SUSPICIOUS: "Suspicious",
            ReputationLevel.UNTRUSTWORTHY: "Untrustworthy",
            ReputationLevel.SMUGGLER: "Smuggler",
            ReputationLevel.PIRATE: "Pirate",
            ReputationLevel.OUTLAW: "Outlaw",
            ReputationLevel.CRIMINAL: "Criminal",
            ReputationLevel.PUBLIC_ENEMY: "Public Enemy"
        }
        return titles.get(level, "Unknown")
    
    def _calculate_trade_modifier(self, value: int) -> float:
        """Calculate trade price modifier based on reputation."""
        # Linear scale from -30% to +30% based on reputation
        return round(value / 800 * 0.3, 2)
    
    def _calculate_port_access_level(self, value: int) -> int:
        """Calculate port access level based on reputation."""
        if value >= 600:
            return 3  # Full access
        elif value >= 200:
            return 2  # Standard access
        elif value >= -200:
            return 1  # Limited access
        else:
            return 0  # No access
    
    def _calculate_combat_response(self, value: int) -> str:
        """Calculate NPC combat response based on reputation."""
        if value >= 400:
            return "friendly"
        elif value >= -200:
            return "neutral"
        else:
            return "hostile"
    
    async def get_faction_pricing_modifier(
        self, 
        player_id: UUID, 
        faction_id: UUID
    ) -> float:
        """
        Get the pricing modifier for a player at faction-controlled ports.
        
        Returns:
            Float multiplier for prices (e.g., 0.8 = 20% discount)
        """
        faction = await self.get_faction_by_id(faction_id)
        if not faction:
            return 1.0
        
        reputation = await self.get_player_reputation(player_id, faction_id)
        if not reputation:
            return faction.base_pricing_modifier
        
        return faction.get_pricing_modifier(reputation.current_value)
    
    async def check_territory_access(
        self, 
        player_id: UUID, 
        sector_id: UUID
    ) -> Dict[str, Any]:
        """
        Check if a player can access a faction-controlled sector.
        
        Returns:
            Dict with 'allowed' boolean and 'reason' string
        """
        # Find which faction controls this sector
        controlling_faction = None
        factions = await self.get_all_factions()
        
        for faction in factions:
            if sector_id in (faction.territory_sectors or []):
                controlling_faction = faction
                break
        
        if not controlling_faction:
            # Sector is not faction-controlled
            return {"allowed": True, "reason": "Neutral territory"}
        
        # Check player reputation
        reputation = await self.get_player_reputation(player_id, controlling_faction.id)
        if not reputation:
            # No reputation record, treat as hostile
            return {
                "allowed": False, 
                "reason": f"No standing with {controlling_faction.name}"
            }
        
        if controlling_faction.can_access_territory(reputation.current_value):
            return {"allowed": True, "reason": "Good standing"}
        else:
            return {
                "allowed": False, 
                "reason": f"Insufficient reputation with {controlling_faction.name}"
            }
    
    async def get_available_missions(
        self, 
        player_id: UUID, 
        faction_id: Optional[UUID] = None
    ) -> List[FactionMission]:
        """
        Get available missions for a player.
        
        Args:
            player_id: The player's ID
            faction_id: Optional specific faction to filter by
            
        Returns:
            List of available missions
        """
        # Get player info
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return []
        
        # Base query
        query = self.db.query(FactionMission).filter(
            and_(
                FactionMission.is_active == 1,
                or_(
                    FactionMission.expires_at.is_(None),
                    FactionMission.expires_at > datetime.utcnow()
                )
            )
        )
        
        # Filter by faction if specified
        if faction_id:
            query = query.filter(FactionMission.faction_id == faction_id)
        
        missions = query.all()
        available_missions = []
        
        for mission in missions:
            # Check reputation requirement
            reputation = await self.get_player_reputation(player_id, mission.faction_id)
            if reputation and reputation.current_value >= mission.min_reputation:
                # Check level requirement (you'll need to implement player level)
                # For now, assume all players meet level requirements
                available_missions.append(mission)
        
        return available_missions
    
    async def create_mission(
        self,
        faction_id: UUID,
        title: str,
        description: str,
        mission_type: str,
        credit_reward: int,
        reputation_reward: int,
        **kwargs
    ) -> FactionMission:
        """Create a new faction mission."""
        mission = FactionMission(
            faction_id=faction_id,
            title=title,
            description=description,
            mission_type=mission_type,
            credit_reward=credit_reward,
            reputation_reward=reputation_reward,
            min_reputation=kwargs.get('min_reputation', -800),
            min_level=kwargs.get('min_level', 1),
            item_rewards=kwargs.get('item_rewards', []),
            target_sector_id=kwargs.get('target_sector_id'),
            cargo_type=kwargs.get('cargo_type'),
            cargo_quantity=kwargs.get('cargo_quantity'),
            target_faction_id=kwargs.get('target_faction_id'),
            expires_at=kwargs.get('expires_at'),
            is_active=1
        )
        
        self.db.add(mission)
        self.db.commit()
        self.db.refresh(mission)
        
        return mission
    
    async def update_faction_territory(
        self,
        faction_id: UUID,
        sector_ids: List[UUID]
    ) -> Faction:
        """Update the territory controlled by a faction."""
        faction = await self.get_faction_by_id(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        faction.territory_sectors = sector_ids
        faction.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(faction)
        
        # Broadcast territory change
        await manager.broadcast({
            "type": "faction_territory_changed",
            "faction_id": str(faction_id),
            "faction_name": faction.name,
            "sectors": [str(sid) for sid in sector_ids]
        })
        
        return faction