#!/usr/bin/env python3
"""
One-time script to backfill MarketPrice entries for all stations.

Run inside the gameserver container:
    docker compose exec gameserver python backfill_market_prices.py

This fixes the bug where galaxy generation created stations with commodities
in their JSONB field but did not create corresponding MarketPrice rows.
The trading endpoint reads from market_prices table, so without these rows,
all stations show empty resources and trading is non-functional.
"""

import sys
import os

# Ensure the src module is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.database import SessionLocal
from src.services.galaxy_service import GalaxyGenerator


def main():
    print("Starting MarketPrice backfill...")
    db = SessionLocal()
    try:
        stats = GalaxyGenerator.backfill_market_prices(db)
        print(f"\nBackfill complete!")
        print(f"  Stations processed: {stats['stations_processed']}")
        print(f"  Market prices created: {stats['prices_created']}")
        print(f"  Stations skipped (already had prices): {stats['stations_skipped']}")
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
