#!/usr/bin/env python3
"""
Regenerate ship options for existing first login sessions to show the full variety
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.models.first_login import FirstLoginSession, ShipPresentationOptions
from src.services.first_login_service import FirstLoginService
from src.services.ai_dialogue_service import AIDialogueService

def regenerate_ship_options():
    """Regenerate ship options for existing first login sessions"""
    print("🎲 Regenerating ship options for existing first login sessions...")
    
    db = next(get_db())
    try:
        # Create services (AI service can be None for this operation)
        ai_service = AIDialogueService()
        first_login_service = FirstLoginService(db, ai_service)
        
        # Find all active first login sessions (not completed)
        active_sessions = db.query(FirstLoginSession).filter_by(completed_at=None).all()
        
        print(f"✓ Found {len(active_sessions)} active first login sessions")
        
        if not active_sessions:
            print("ℹ️  No active sessions to update")
            return
        
        # Regenerate ship options for each session
        updated_count = 0
        for session in active_sessions:
            print(f"  🔄 Regenerating ships for session {session.id}")
            
            # Delete old ship options
            old_options = db.query(ShipPresentationOptions).filter_by(session_id=session.id).first()
            if old_options:
                db.delete(old_options)
            
            # Generate new ship options
            new_options = first_login_service._generate_ship_options(session.id)
            db.add(new_options)
            
            print(f"    ✓ New ships: {', '.join(new_options.available_ships)}")
            print(f"    ✓ Rarity roll: {new_options.rarity_roll}")
            
            updated_count += 1
        
        if updated_count > 0:
            db.commit()
            print(f"✅ Successfully regenerated ship options for {updated_count} sessions")
            print("🎮 Refresh your browser to see the new ship selection!")
        else:
            print("ℹ️  No sessions needed updating")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error regenerating ship options: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    regenerate_ship_options()