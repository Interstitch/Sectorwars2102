#!/usr/bin/env python3
"""
Update existing first login dialogue exchanges to include the cat in the opening prompt
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.models.first_login import DialogueExchange
from src.services.first_login_service import INITIAL_GUARD_PROMPT

def update_existing_prompts():
    """Update existing dialogue exchanges to include the cat"""
    print("🔧 Updating existing first login prompts to include cat...")
    
    db = next(get_db())
    try:
        # Find all initial dialogue exchanges (sequence_number = 1)
        initial_exchanges = db.query(DialogueExchange).filter_by(
            sequence_number=1,
            topic="introduction"
        ).all()
        
        print(f"✓ Found {len(initial_exchanges)} initial dialogue exchanges")
        
        if not initial_exchanges:
            print("ℹ️  No existing exchanges to update")
            return
        
        # Update each exchange with the new prompt that includes the cat
        updated_count = 0
        for exchange in initial_exchanges:
            if "small orange cat" not in exchange.npc_prompt:
                print(f"  🔄 Updating exchange {exchange.id} for session {exchange.session_id}")
                exchange.npc_prompt = INITIAL_GUARD_PROMPT
                updated_count += 1
            else:
                print(f"  ✓ Exchange {exchange.id} already has cat - skipping")
        
        if updated_count > 0:
            db.commit()
            print(f"✅ Successfully updated {updated_count} dialogue exchanges with cat")
        else:
            print("ℹ️  All exchanges already contain the cat")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating prompts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_existing_prompts()