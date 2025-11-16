from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


class TradingService:
    """Service for handling all trading-related operations"""
    
    @staticmethod
    def can_player_trade(player, port) -> Tuple[bool, str]:
        """Check if a player can trade at a specific port"""
        
        # Check if player is docked
        if not player.is_docked:
            return False, "You must be docked at a port to trade"
        
        # Check if player is in the same sector as the port
        if player.current_sector_id != port.sector_id:
            return False, "You must be in the same sector as the port"
        
        return True, "OK"