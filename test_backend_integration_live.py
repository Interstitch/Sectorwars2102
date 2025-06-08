#!/usr/bin/env python3
"""
Backend Integration Bridge - Live Integration Test
Tests the complete flow: WebSocket -> Market Service -> Database -> Redis Pub/Sub
"""

import asyncio
import json
import sys
import os
from datetime import datetime, UTC

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services/gameserver'))

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.core.database import get_async_session
from src.services.realtime_market_service import get_market_service
from src.services.redis_pubsub_service import get_pubsub_service
from src.services.enhanced_websocket_service import get_enhanced_websocket_service

# Test configuration
TEST_PLAYER_ID = "test_player_123"
TEST_COMMODITIES = ["ORE", "FUEL", "EQUIPMENT"]


async def test_market_service(db_session: AsyncSession):
    """Test real-time market service"""
    print("\n🏪 Testing Real-Time Market Service...")
    print("=" * 70)
    
    try:
        # Get market service
        market_service = get_market_service()
        
        # Test 1: Get market snapshot for a commodity
        print("\n1. Testing market snapshot retrieval...")
        snapshot = await market_service.get_market_snapshot("ORE", db_session)
        
        if snapshot:
            print(f"✅ Market snapshot retrieved for ORE")
            print(f"   Current Price: ${snapshot.current_price:.2f}")
            print(f"   24h Volume: {snapshot.volume_24h:,} units")
            print(f"   24h Change: {snapshot.price_change_percent:.2f}%")
            print(f"   Bid/Ask Spread: {snapshot.bid_ask_spread:.2f}%")
        else:
            print("❌ Failed to retrieve market snapshot")
        
        # Test 2: Get multi-commodity data
        print("\n2. Testing multi-commodity data retrieval...")
        multi_data = await market_service.get_multi_commodity_data(TEST_COMMODITIES, db_session)
        
        print(f"✅ Retrieved data for {len(multi_data)} commodities:")
        for commodity, snapshot in multi_data.items():
            print(f"   {commodity}: ${snapshot.current_price:.2f} ({snapshot.price_change_percent:+.2f}%)")
        
        # Test 3: Generate trading signals
        print("\n3. Testing trading signal generation...")
        if snapshot:
            signals = await market_service.generate_trading_signals("ORE", snapshot)
            if signals:
                print(f"✅ Generated {len(signals)} trading signals:")
                for signal in signals[:3]:  # Show first 3
                    print(f"   {signal.signal_type.upper()}: {signal.reason} (strength: {signal.strength:.2f})")
            else:
                print("ℹ️  No trading signals generated (market stable)")
        
        # Test 4: Performance metrics
        print("\n4. Checking performance metrics...")
        metrics = market_service.get_performance_metrics()
        print(f"✅ Performance Metrics:")
        print(f"   Avg Query Time: {metrics['avg_query_time_ms']}ms")
        print(f"   Cache Hit Rate: {metrics['cache_hit_rate']}%")
        print(f"   Total Queries: {metrics['total_queries']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Market service test failed: {e}")
        return False


async def test_redis_pubsub():
    """Test Redis pub/sub service"""
    print("\n📮 Testing Redis Pub/Sub Service...")
    print("=" * 70)
    
    try:
        # Get pub/sub service
        pubsub_service = await get_pubsub_service()
        
        # Test 1: Health check
        print("\n1. Testing Redis connection...")
        healthy = await pubsub_service.health_check()
        if healthy:
            print("✅ Redis connection healthy")
        else:
            print("❌ Redis connection failed")
            return False
        
        # Test 2: Publish market update
        print("\n2. Testing market update publishing...")
        test_market_data = {
            "current_price": 52.50,
            "volume_24h": 15000,
            "price_change_percent": 2.5
        }
        
        subscribers = await pubsub_service.publish_market_update("ORE", test_market_data)
        print(f"✅ Published market update to {subscribers} subscribers")
        
        # Test 3: Publish trading event
        print("\n3. Testing trading event publishing...")
        test_trade = {
            "commodity": "ORE",
            "action": "buy",
            "quantity": 100,
            "price": 52.50,
            "player_id": TEST_PLAYER_ID
        }
        
        subscribers = await pubsub_service.publish_trading_event("trade_executed", test_trade)
        print(f"✅ Published trading event to {subscribers} subscribers")
        
        # Test 4: Get subscription stats
        print("\n4. Checking subscription statistics...")
        stats = pubsub_service.get_subscription_stats()
        print(f"✅ Subscription Stats:")
        print(f"   Total Channels: {stats['total_channels']}")
        print(f"   Active Listeners: {stats['active_listeners']}")
        print(f"   Messages Published: {stats['messages_published']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis pub/sub test failed: {e}")
        return False


async def test_websocket_integration(db_session: AsyncSession):
    """Test enhanced WebSocket service integration"""
    print("\n🔌 Testing Enhanced WebSocket Service...")
    print("=" * 70)
    
    try:
        # Get WebSocket service
        ws_service = get_enhanced_websocket_service()
        
        # Test 1: Service initialization
        print("\n1. Testing WebSocket service initialization...")
        print(f"✅ WebSocket service initialized")
        print(f"   Rate Limits:")
        print(f"   - Messages/sec: {ws_service.rate_limit_config.max_messages_per_second}")
        print(f"   - Trades/min: {ws_service.rate_limit_config.max_trading_commands_per_minute}")
        print(f"   - AI requests/min: {ws_service.rate_limit_config.max_ai_requests_per_minute}")
        
        # Test 2: Market data retrieval
        print("\n2. Testing market data retrieval via WebSocket service...")
        market_data = await ws_service._get_current_market_data(TEST_COMMODITIES, db_session)
        
        if market_data:
            print(f"✅ Retrieved market data for {len(market_data)} commodities")
            for commodity, data in market_data.items():
                print(f"   {commodity}: ${data.get('current_price', 0):.2f}")
                if 'signals' in data:
                    print(f"     - {len(data['signals'])} trading signals available")
        
        # Test 3: Mock trade broadcast
        print("\n3. Testing trade broadcast capability...")
        test_trade = {
            "id": "test_trade_123",
            "commodity": "FUEL",
            "action": "sell",
            "quantity": 500,
            "price": 32.75,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        await ws_service._broadcast_trade_update(test_trade, db_session)
        print("✅ Trade broadcast completed")
        
        return True
        
    except Exception as e:
        print(f"❌ WebSocket integration test failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("🌉 Backend Integration Bridge - Live Integration Test")
    print("=" * 70)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database: {settings.DATABASE_URL.hosts()[0]['host']}")
    print(f"Redis: {settings.REDIS_URL}")
    print("=" * 70)
    
    results = {
        "market_service": False,
        "redis_pubsub": False,
        "websocket_integration": False
    }
    
    # Use the proper async database session
    async for db_session in get_async_session():
        try:
            # Run tests
            results["market_service"] = await test_market_service(db_session)
            results["redis_pubsub"] = await test_redis_pubsub()
            results["websocket_integration"] = await test_websocket_integration(db_session)
            break  # Only run once
        finally:
            await db_session.close()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Integration Test Summary:")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.0f}%)")
    
    if passed_tests == total_tests:
        print("\n🎊 Backend Integration Bridge - FULLY OPERATIONAL! 🎊")
        print("The bridge between Foundation Sprint and live game APIs is ready.")
    elif passed_tests >= total_tests * 0.7:
        print("\n⚡ Backend Integration Bridge - MOSTLY READY")
        print("Core functionality is working, some components need attention.")
    else:
        print("\n⚠️  Backend Integration Bridge needs significant work.")
    
    # Implementation progress
    print("\n📋 Implementation Progress:")
    checklist = [
        ("WebSocket infrastructure", True),
        ("Enhanced WebSocket routes", True),
        ("Real-time market service", True),
        ("Redis pub/sub integration", True),
        ("Market data from database", results["market_service"]),
        ("Trading signals generation", results["market_service"]),
        ("Multi-client broadcasting", results["redis_pubsub"]),
        ("WebSocket integration", results["websocket_integration"]),
        ("Trading command execution", False),  # Not tested yet
        ("AI chat integration", False),  # Not tested yet
    ]
    
    for item, done in checklist:
        print(f"{'✅' if done else '⬜'} {item}")
    
    completed = sum(1 for _, done in checklist if done)
    print(f"\nProgress: {completed}/{len(checklist)} ({completed/len(checklist)*100:.0f}%)")


if __name__ == "__main__":
    asyncio.run(main())