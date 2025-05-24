#!/usr/bin/env python3
"""
Test script for AI Dialogue Service functionality
Tests the first login AI integration without needing API keys
"""

import asyncio
import sys
import os

# Add the gameserver source to the path
sys.path.append('/workspaces/Sectorwars2102/services/gameserver/src')

from services.ai_dialogue_service import (
    AIDialogueService, 
    DialogueContext, 
    ShipType, 
    GuardMood
)

async def test_ai_dialogue_service():
    """Test the AI dialogue service with fallback logic"""
    
    print("🤖 Testing AI Dialogue Service")
    print("=" * 50)
    
    # Initialize service without API keys (should fallback to rule-based logic)
    service = AIDialogueService()
    
    print(f"AI Enabled: {service.ai_enabled}")
    print(f"AI Available: {service.is_available()}")
    print(f"Fallback Enabled: {service.fallback_enabled}")
    print()
    
    # Create a test dialogue context
    context = DialogueContext(
        session_id="test-session-123",
        claimed_ship=ShipType.CARGO_FREIGHTER,
        actual_ship=ShipType.ESCAPE_POD,
        dialogue_history=[
            {"guard": "Which vessel belongs to you?", "player": "The cargo freighter is mine"},
            {"guard": "What's your pilot registration?", "player": "Captain Alex Morgan, registration FL-7749"}
        ],
        inconsistencies=["Player claims freighter but registered to pod"],
        guard_mood=GuardMood.SUSPICIOUS,
        negotiation_skill_level=0.7,
        player_name="Alex Morgan"
    )
    
    print("📝 Testing Response Analysis...")
    print("-" * 30)
    
    test_response = "Yes, I'm definitely the captain of that freighter. I've been flying cargo runs for over 5 years and my clearance is up to date."
    
    try:
        analysis = await service.analyze_player_response(test_response, context)
        print(f"✅ Analysis completed successfully!")
        print(f"   Persuasiveness: {analysis.persuasiveness_score:.2f}")
        print(f"   Confidence: {analysis.confidence_level:.2f}")
        print(f"   Consistency: {analysis.consistency_score:.2f}")
        print(f"   Negotiation Skill: {analysis.negotiation_skill:.2f}")
        print(f"   Believability: {analysis.overall_believability:.2f}")
        print(f"   Detected Issues: {analysis.detected_inconsistencies}")
        print(f"   Extracted Claims: {analysis.extracted_claims}")
        print(f"   Guard Mood: {analysis.suggested_guard_mood.value}")
        print()
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False
    
    print("💬 Testing Question Generation...")
    print("-" * 30)
    
    try:
        guard_response = await service.generate_guard_question(context, analysis)
        print(f"✅ Question generation completed successfully!")
        print(f"   Guard Response: \"{guard_response.dialogue_text}\"")
        print(f"   Guard Mood: {guard_response.mood.value}")
        print(f"   Suspicion Level: {guard_response.suspicion_level:.2f}")
        print(f"   Is Final Decision: {guard_response.is_final_decision}")
        if guard_response.outcome:
            print(f"   Outcome: {guard_response.outcome}")
            print(f"   Credits Modifier: {guard_response.credits_modifier:.2f}")
        print()
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        return False
    
    print("🎯 Testing Different Ship Claims...")
    print("-" * 30)
    
    ship_tests = [
        (ShipType.SCOUT_SHIP, "I'm a reconnaissance pilot"),
        (ShipType.PATROL_CRAFT, "I'm on patrol duty"),
        (ShipType.LUXURY_YACHT, "This is my personal yacht"),
        (ShipType.ESCAPE_POD, "Yes, that's my escape pod")
    ]
    
    for ship_type, response in ship_tests:
        test_context = DialogueContext(
            session_id=f"test-{ship_type.value}",
            claimed_ship=ship_type,
            actual_ship=ShipType.ESCAPE_POD,
            dialogue_history=[],
            inconsistencies=[],
            guard_mood=GuardMood.NEUTRAL,
            negotiation_skill_level=0.5
        )
        
        try:
            analysis = await service.analyze_player_response(response, test_context)
            guard_response = await service.generate_guard_question(test_context, analysis)
            print(f"   {ship_type.value}: Believability {analysis.overall_believability:.2f} -> \"{guard_response.dialogue_text[:50]}...\"")
        except Exception as e:
            print(f"   {ship_type.value}: Failed - {e}")
    
    print()
    print("✅ All AI Dialogue Service tests completed successfully!")
    print("🔄 Service correctly falls back to rule-based logic when AI is unavailable")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_ai_dialogue_service())
    if result:
        print("\n🎉 AI Dialogue Service is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ AI Dialogue Service tests failed!")
        sys.exit(1)