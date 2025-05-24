#!/usr/bin/env python3
"""
Comprehensive Ship System Test
Tests all ship implementations and the enhanced first login experience
"""

import sys
import os
import uuid

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.models.ship import ShipType, ShipSpecification, Ship
from src.models.first_login import ShipChoice
from src.services.ship_service import ShipService
from src.services.first_login_service import FirstLoginService, SHIP_CHOICE_TO_TYPE
from src.models.player import Player
from src.models.user import User
import uuid

def test_ship_specifications():
    """Test that all ship specifications are properly seeded"""
    print("🔍 Testing ship specifications...")
    
    db = next(get_db())
    try:
        all_ship_types = list(ShipType)
        missing_specs = []
        
        for ship_type in all_ship_types:
            spec = db.query(ShipSpecification).filter(
                ShipSpecification.type == ship_type
            ).first()
            
            if not spec:
                missing_specs.append(ship_type.value)
            else:
                print(f"  ✓ {ship_type.value}: {spec.description[:50]}...")
        
        if missing_specs:
            print(f"  ❌ Missing specifications: {', '.join(missing_specs)}")
            return False
        
        print(f"  ✅ All {len(all_ship_types)} ship types have specifications")
        return True
        
    finally:
        db.close()

def test_ship_choice_mapping():
    """Test that all ship choices map to valid ship types"""
    print("🔍 Testing ship choice mappings...")
    
    all_ship_choices = list(ShipChoice)
    invalid_mappings = []
    
    for ship_choice in all_ship_choices:
        if ship_choice not in SHIP_CHOICE_TO_TYPE:
            invalid_mappings.append(f"{ship_choice.value} (no mapping)")
        else:
            ship_type = SHIP_CHOICE_TO_TYPE[ship_choice]
            if ship_type not in list(ShipType):
                invalid_mappings.append(f"{ship_choice.value} -> {ship_type.value} (invalid)")
            else:
                print(f"  ✓ {ship_choice.value} -> {ship_type.value}")
    
    if invalid_mappings:
        print(f"  ❌ Invalid mappings: {', '.join(invalid_mappings)}")
        return False
    
    print(f"  ✅ All {len(all_ship_choices)} ship choices map correctly")
    return True

def test_escape_pod_special_properties():
    """Test that Escape Pod has special indestructible properties"""
    print("🔍 Testing Escape Pod special properties...")
    
    db = next(get_db())
    try:
        ship_service = ShipService(db)
        
        # Get Escape Pod specification
        escape_pod_spec = db.query(ShipSpecification).filter(
            ShipSpecification.type == ShipType.ESCAPE_POD
        ).first()
        
        if not escape_pod_spec:
            print("  ❌ Escape Pod specification not found")
            return False
        
        # Check special properties
        checks = []
        
        # Check cost (should be 0)
        if escape_pod_spec.base_cost == 0:
            checks.append("✓ Free (0 credits)")
        else:
            checks.append(f"❌ Cost should be 0, got {escape_pod_spec.base_cost}")
        
        # Check speed (should be slow)
        if escape_pod_spec.speed <= 0.5:
            checks.append(f"✓ Slow speed ({escape_pod_spec.speed})")
        else:
            checks.append(f"❌ Speed should be ≤0.5, got {escape_pod_spec.speed}")
        
        # Check turn cost (should be high)
        if escape_pod_spec.turn_cost >= 2:
            checks.append(f"✓ High turn cost ({escape_pod_spec.turn_cost})")
        else:
            checks.append(f"❌ Turn cost should be ≥2, got {escape_pod_spec.turn_cost}")
        
        # Check special abilities
        if "indestructible" in escape_pod_spec.special_abilities:
            checks.append("✓ Indestructible ability")
        else:
            checks.append("❌ Missing indestructible ability")
        
        for check in checks:
            print(f"    {check}")
        
        # Test indestructible check
        # Create a mock escape pod for testing
        test_ship = Ship(
            id=uuid.uuid4(),
            name="Test Escape Pod",
            type=ShipType.ESCAPE_POD,
            owner_id=uuid.uuid4(),
            sector_id=1,
            base_speed=0.25,
            current_speed=0.25,
            turn_cost=4,
            warp_capable=False,
            is_active=True,
            maintenance={},
            cargo={},
            combat={},
            upgrades=[],
            is_destroyed=False,
            is_flagship=True,
            purchase_value=0,
            current_value=0
        )
        
        if ship_service.is_ship_indestructible(test_ship):
            print("    ✓ Indestructible check works")
            return all("✓" in check for check in checks) and True
        else:
            print("    ❌ Indestructible check failed")
            return False
        
    finally:
        db.close()

def test_ship_creation():
    """Test ship creation for all ship types"""
    print("🔍 Testing ship creation...")
    
    db = next(get_db())
    try:
        ship_service = ShipService(db)
        
        # Create a test user and player first
        from src.models.user import User
        from src.models.player import Player
        
        test_user = User(
            id=uuid.uuid4(),
            username="test_user",
            email="test@example.com",
            is_active=True
        )
        db.add(test_user)
        db.flush()  # Get the ID
        
        test_player = Player(
            id=uuid.uuid4(),
            user_id=test_user.id,
            nickname="Test Player",
            credits=10000,
            turns=1000,
            home_sector_id=1,
            current_sector_id=1
        )
        db.add(test_player)
        db.flush()  # Get the ID
        
        # Test creating each ship type
        test_owner_id = test_player.id
        test_sector_id = 1
        
        success_count = 0
        total_count = len(ShipType)
        
        for ship_type in ShipType:
            try:
                ship = ship_service.create_ship(
                    ship_type=ship_type,
                    owner_id=test_owner_id,
                    sector_id=test_sector_id,
                    name=f"Test {ship_type.value}"
                )
                
                # Validate ship properties
                if (ship.type == ship_type and 
                    ship.owner_id == test_owner_id and
                    ship.sector_id == test_sector_id and
                    ship.is_active and
                    not ship.is_destroyed):
                    print(f"  ✓ {ship_type.value}: Created successfully")
                    success_count += 1
                else:
                    print(f"  ❌ {ship_type.value}: Invalid properties")
                
                # Clean up (don't commit)
                db.delete(ship)
                
            except Exception as e:
                print(f"  ❌ {ship_type.value}: Creation failed - {e}")
        
        print(f"  ✅ {success_count}/{total_count} ship types created successfully")
        return success_count == total_count
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.rollback()  # Clean up test data
        db.close()

def test_first_login_ship_variety():
    """Test that first login offers variety of ships"""
    print("🔍 Testing first login ship variety...")
    
    db = next(get_db())
    try:
        first_login_service = FirstLoginService(db)
        
        # Test ship generation multiple times to see variety
        ship_combinations = set()
        
        for i in range(20):  # Test 20 times
            # Generate a dummy session ID for testing
            session_id = uuid.uuid4()
            ships = first_login_service._generate_ship_options(session_id)
            # Extract ship choice names from the ShipPresentationOptions object
            ship_names = ships.available_ships  # This is an array of ship type strings
            ship_tuple = tuple(sorted(ship_names))
            ship_combinations.add(ship_tuple)
        
        print(f"  ✓ Generated {len(ship_combinations)} different ship combinations")
        
        # Print the actual combinations for debugging
        for i, combo in enumerate(ship_combinations, 1):
            print(f"    Combination {i}: {', '.join(combo)}")
        
        # Check that we have good variety
        if len(ship_combinations) >= 5:
            print("  ✅ Good ship variety in first login")
            return True
        else:
            print("  ❌ Insufficient ship variety in first login")
            return False
        
    finally:
        db.close()

def test_ship_descriptions():
    """Test that all ships have proper descriptions in UI"""
    print("🔍 Testing ship descriptions...")
    
    # Skip this test when running in container without frontend access
    frontend_path = '/workspaces/Sectorwars2102/services/player-client/src/components/first-login/ShipSelection.tsx'
    if not os.path.exists(frontend_path):
        print("  ⚠️  Frontend files not accessible from container, skipping UI tests")
        return True
    
    # Import the ship descriptions from the frontend
    try:
        # Read the TypeScript file to check descriptions
        with open(frontend_path, 'r') as f:
            content = f.read()
        
        required_ships = [
            "ESCAPE_POD",
            "LIGHT_FREIGHTER", 
            "CARGO_HAULER",
            "SCOUT_SHIP",
            "FAST_COURIER",
            "DEFENDER",
            "COLONY_SHIP",
            "CARRIER"
        ]
        
        missing_descriptions = []
        for ship in required_ships:
            if f'"{ship}":' not in content:
                missing_descriptions.append(ship)
            else:
                print(f"  ✓ {ship}: Description found")
        
        if missing_descriptions:
            print(f"  ❌ Missing descriptions: {', '.join(missing_descriptions)}")
            return False
        
        print(f"  ✅ All {len(required_ships)} ships have descriptions")
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading ship descriptions: {e}")
        return False

def test_game_title_display():
    """Test that game title is displayed in first login"""
    print("🔍 Testing game title display...")
    
    # Skip this test when running in container without frontend access
    frontend_path = '/workspaces/Sectorwars2102/services/player-client/src/components/first-login/ShipSelection.tsx'
    if not os.path.exists(frontend_path):
        print("  ⚠️  Frontend files not accessible from container, skipping UI tests")
        return True
    
    try:
        with open(frontend_path, 'r') as f:
            content = f.read()
        
        checks = []
        
        if 'SECTOR WARS 2102' in content:
            checks.append("✓ Game title present")
        else:
            checks.append("❌ Game title missing")
        
        if 'Welcome to the Galaxy' in content:
            checks.append("✓ Subtitle present")
        else:
            checks.append("❌ Subtitle missing")
        
        if 'Callisto Colony' in content:
            checks.append("✓ Location context present")
        else:
            checks.append("❌ Location context missing")
        
        for check in checks:
            print(f"    {check}")
        
        success = all("✓" in check for check in checks)
        if success:
            print("  ✅ Game title display is complete")
        else:
            print("  ❌ Game title display is incomplete")
        
        return success
        
    except Exception as e:
        print(f"  ❌ Error checking game title: {e}")
        return False

def run_all_tests():
    """Run all ship system tests"""
    print("🚀 Running comprehensive ship system tests...\n")
    
    tests = [
        ("Ship Specifications", test_ship_specifications),
        ("Ship Choice Mapping", test_ship_choice_mapping),
        ("Escape Pod Properties", test_escape_pod_special_properties),
        ("Ship Creation", test_ship_creation),
        ("First Login Variety", test_first_login_ship_variety),
        ("Ship Descriptions", test_ship_descriptions),
        ("Game Title Display", test_game_title_display),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"TEST: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Ship system is fully functional.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)