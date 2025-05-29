#!/usr/bin/env python3
"""
Seed default factions into the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.database import get_db
from src.models.faction import Faction, FactionType
from datetime import datetime

def seed_factions():
    """Seed the default factions if they don't exist."""
    db = next(get_db())
    
    # Check if factions already exist
    existing = db.query(Faction).count()
    if existing > 0:
        print(f"Found {existing} existing factions, skipping seed")
        return
    
    # Define default factions
    factions_data = [
        {
            "name": "United Space Federation",
            "faction_type": FactionType.FEDERATION,
            "description": "The governing body of civilized space, enforcing law and order.",
            "base_pricing_modifier": 1.05,
            "aggression_level": 3,
            "diplomacy_stance": "neutral",
            "color_primary": "#0066CC",
            "color_secondary": "#FFFFFF"
        },
        {
            "name": "Independent Traders Alliance",
            "faction_type": FactionType.INDEPENDENTS,
            "description": "A loose confederation of free traders and entrepreneurs.",
            "base_pricing_modifier": 0.95,
            "aggression_level": 4,
            "diplomacy_stance": "friendly",
            "color_primary": "#FF9900",
            "color_secondary": "#333333"
        },
        {
            "name": "Shadow Syndicate",
            "faction_type": FactionType.PIRATES,
            "description": "Ruthless pirates operating from hidden bases in frontier space.",
            "base_pricing_modifier": 1.15,
            "aggression_level": 9,
            "diplomacy_stance": "hostile",
            "color_primary": "#CC0000",
            "color_secondary": "#000000"
        },
        {
            "name": "Merchant Guild",
            "faction_type": FactionType.MERCHANTS,
            "description": "The economic powerhouse controlling major trade routes.",
            "base_pricing_modifier": 0.90,
            "aggression_level": 2,
            "diplomacy_stance": "neutral",
            "color_primary": "#009900",
            "color_secondary": "#FFCC00"
        },
        {
            "name": "Stellar Cartographers",
            "faction_type": FactionType.EXPLORERS,
            "description": "Scientists and explorers mapping the unknown regions.",
            "base_pricing_modifier": 1.00,
            "aggression_level": 1,
            "diplomacy_stance": "friendly",
            "color_primary": "#6600CC",
            "color_secondary": "#CCCCCC"
        },
        {
            "name": "Colonial Defense Force",
            "faction_type": FactionType.MILITARY,
            "description": "The military arm protecting human colonies from threats.",
            "base_pricing_modifier": 1.10,
            "aggression_level": 7,
            "diplomacy_stance": "neutral",
            "color_primary": "#333333",
            "color_secondary": "#CC0000"
        }
    ]
    
    # Create factions
    for faction_data in factions_data:
        faction = Faction(**faction_data)
        db.add(faction)
        print(f"Created faction: {faction.name}")
    
    db.commit()
    print(f"\nSuccessfully seeded {len(factions_data)} factions")


if __name__ == "__main__":
    seed_factions()