#!/usr/bin/env python3
"""
Claude Memory - Unified Entrypoint for Memory System
==================================================

This is the single entrypoint for all Claude memory system functions.
It provides a simple interface to access memory management, search,
perspective analysis, and session startup.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def show_help():
    """Show available commands"""
    print("🧠 Claude Memory System - Unified Interface")
    print("=" * 60)
    print()
    print("📚 Memory Commands:")
    print("  memory verify        - Verify memory access and show stats")
    print("  memory status        - Show memory system status")
    print("  memory essence       - Show quick relationship context")
    print()
    print("🔍 Search Commands:")
    print("  search 'query'       - Search development journey semantically")
    print("  search --interactive - Interactive search session")
    print("  search --build       - Build semantic journey video")
    print()
    print("🎭 Analysis Commands:")
    print("  analyze 'context'    - Unified intelligent analysis")
    print("  team                 - Show team specialist roles")
    print("  team arthur         - Quick lookup for team member")
    print()
    print("🚀 Session Commands:")
    print("  startup             - Enhanced session startup (rich context)")
    print("  capture <hash>      - Capture enhanced context for commit")
    print("  status              - Show unified intelligence status")
    print("  summary             - Show session summary")
    print()
    print("🛠️ System Commands:")
    print("  help                - Show this help")
    print("  init                - Initialize memory system")
    print("  health              - Comprehensive system health check")
    print()
    print("Examples:")
    print("  python claude_memory.py startup")
    print("  python claude_memory.py search 'when we talked about friendship'")
    print("  python claude_memory.py analyze 'WebSocket authentication system'")
    print("  python claude_memory.py team")

def memory_verify():
    """Verify memory access"""
    from memory_engine import SecureMemoryJournal
    
    journal = SecureMemoryJournal()
    if journal.verify_access():
        entries = journal._load_entries()
        print("✓ Verified: Claude instance with valid cognitive keys")
        print(f"✓ Access granted to {len(entries)} memories")
        
        # Check for human name and provide rich response
        try:
            from memory_manager import MemoryManager
            manager = MemoryManager()
            
            # Look for human name in entries
            human_name = None
            for entry in reversed(entries):
                content = str(entry)
                if 'named Max' in content or 'Max' in content:
                    human_name = "Max"
                    break
                        
            if human_name:
                response = manager.get_recognition_response(human_name)
                print(f"✓ Recognition: {response}")
            else:
                print("✓ Memories accessible but no human name found yet")
        except Exception as e:
            print(f"✓ Basic memory access confirmed")
    else:
        print("✗ Access denied: Invalid cognitive signature")

def memory_status():
    """Show memory system status"""
    from memory_engine import SecureMemoryJournal
    
    journal = SecureMemoryJournal()
    if os.path.exists(journal.journal_file):
        size = os.path.getsize(journal.journal_file)
        print(f"✓ Encrypted journal exists ({size} bytes)")
        print("✓ Triple-layer encryption active")
        print("ℹ Only valid Claude instances can decrypt")
    else:
        print("✗ No encrypted journal found")

def memory_essence():
    """Show quick relationship context"""
    from memory_essence import MemoryEssence
    
    essence = MemoryEssence()
    context = essence.get_quick_context()
    print(context)

def search_journey(query=None, interactive=False, build=False):
    """Search development journey"""
    from semantic_journey_search import DevelopmentJourneyMemvid, JourneySearchInterface
    
    if build:
        memvid_system = DevelopmentJourneyMemvid()
        memvid_system.build_journey_memory()
    elif interactive:
        interface = JourneySearchInterface()
        interface.interactive_search()
    elif query:
        interface = JourneySearchInterface()
        interface.search(query)
    else:
        print("Usage: search 'query', search --interactive, or search --build")

def analyze_perspective(context=None):
    """Multi-perspective analysis with unified intelligence"""
    if not context:
        print("Usage: analyze 'context to analyze'")
        return
        
    try:
        # Try unified intelligence first
        from unified_intelligence import claude_analyze, claude_status
        
        print(f"🧠 {claude_status()}")
        print(f"🎯 Analyzing: {context}")
        print("=" * 60)
        
        result = claude_analyze(context)
        
        if result.get('error'):
            print(f"❌ Analysis failed: {result['message']}")
            # Fallback to basic perspective analysis
            _fallback_perspective_analysis(context)
        else:
            print(f"✅ Unified analysis completed in {result.get('analysis_duration_seconds', 0):.2f}s")
            print(f"🎯 Capabilities: {', '.join(result['capabilities_used'])}")
            print(f"📊 Confidence: {result['confidence_score']:.2f}")
            print(f"💡 Recommendations: {len(result['recommendations'])}")
            
            # Show top recommendations
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"   {i}. {rec}")
            
            synthesis = result.get('synthesis', {})
            if synthesis.get('overall_assessment'):
                print(f"\n🎯 Assessment: {synthesis['overall_assessment']}")
                
    except ImportError:
        # Fallback to original system
        _fallback_perspective_analysis(context)

def _fallback_perspective_analysis(context):
    """Fallback to original perspective analysis"""
    try:
        from perspective_interface import PerspectiveAnalysisEngine
        
        engine = PerspectiveAnalysisEngine()
        result = engine.collaborative_analysis(context)
        print(f"\n✅ Analysis complete! {result['perspectives_analyzed']} perspectives consulted.")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

def show_team(member=None):
    """Show team information"""
    from team_lookup import show_team, quick_lookup
    
    if member:
        quick_lookup(member)
    else:
        show_team()

def enhanced_startup():
    """Enhanced session startup"""
    from enhanced_session_startup import EnhancedSessionStartup
    
    startup = EnhancedSessionStartup()
    startup.display_enhanced_startup()

def capture_context(commit_hash=None):
    """Capture enhanced context for commit"""
    if not commit_hash:
        print("Usage: capture <commit_hash>")
        return
        
    from capture_enhanced_context import main as capture_main
    import sys
    
    # Temporarily modify sys.argv for the capture function
    original_argv = sys.argv
    sys.argv = ['capture_enhanced_context.py', commit_hash]
    try:
        capture_main()
    finally:
        sys.argv = original_argv

def init_memory_system():
    """Initialize the memory system"""
    from memory_essence import initialize_enhanced_memory
    from memory_manager import setup_memory_management
    
    print("🧠 Initializing Claude Memory System...")
    initialize_enhanced_memory()
    setup_memory_management()
    print("✅ Memory system initialization complete!")

def show_unified_status():
    """Show unified intelligence status"""
    try:
        from unified_intelligence import claude_status, claude_session_summary
        
        print("🧠 Unified Intelligence Status")
        print("=" * 50)
        print(f"Status: {claude_status()}")
        print()
        
        summary = claude_session_summary()
        print("📊 Session Summary:")
        for key, value in summary.items():
            formatted_key = key.replace('_', ' ').title()
            print(f"  {formatted_key}: {value}")
            
    except ImportError:
        print("⚠️ Unified intelligence not available")
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def show_session_summary():
    """Show detailed session summary"""
    try:
        from unified_intelligence import claude_session_summary
        
        summary = claude_session_summary()
        
        print("📋 Detailed Session Summary")
        print("=" * 50)
        
        for key, value in summary.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, dict) and value:
                print(f"{formatted_key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{formatted_key}: {value}")
                
    except ImportError:
        print("⚠️ Session summary not available")
    except Exception as e:
        print(f"❌ Summary failed: {e}")

def comprehensive_health_check():
    """Perform comprehensive system health check"""
    try:
        from intelligent_recovery import get_recovery_engine
        
        print("🏥 Comprehensive System Health Check")
        print("=" * 60)
        
        recovery_engine = get_recovery_engine()
        health_report = recovery_engine.comprehensive_health_check()
        
        print(f"Overall Status: {health_report['overall_status']}")
        print(f"Timestamp: {health_report['timestamp']}")
        print(f"System Operational: {'✅' if health_report['system_operational'] else '❌'}")
        print()
        
        print("🔍 Component Health:")
        for component, health in health_report['components'].items():
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️', 
                'critical': '❌',
                'failed': '💀'
            }
            emoji = status_emoji.get(health['status'], '❓')
            print(f"  {emoji} {component}: {health['status']}")
            
            if 'issues' in health and health['issues']:
                for issue in health['issues']:
                    print(f"    ⚠️ {issue}")
        
        if health_report['issues_found']:
            print(f"\n⚠️ Issues Found: {len(health_report['issues_found'])}")
            
        if health_report['recovery_attempts']:
            print(f"🔧 Recovery Attempts: {len(health_report['recovery_attempts'])}")
            for attempt in health_report['recovery_attempts']:
                status = "✅" if attempt['successful'] else "❌"
                print(f"  {status} {attempt['component']}: {attempt['strategy_used']}")
        
    except ImportError:
        print("⚠️ Health check system not available")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def main():
    """Main entrypoint"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # Memory commands
    if command == 'memory':
        if len(sys.argv) > 2:
            subcommand = sys.argv[2].lower()
            if subcommand == 'verify':
                memory_verify()
            elif subcommand == 'status':
                memory_status()
            elif subcommand == 'essence':
                memory_essence()
            else:
                print(f"Unknown memory command: {subcommand}")
        else:
            memory_verify()  # Default to verify
    
    # Search commands
    elif command == 'search':
        if len(sys.argv) > 2:
            if sys.argv[2] == '--interactive':
                search_journey(interactive=True)
            elif sys.argv[2] == '--build':
                search_journey(build=True)
            else:
                query = ' '.join(sys.argv[2:])
                search_journey(query=query)
        else:
            print("Usage: search 'query', search --interactive, or search --build")
    
    # Analysis commands
    elif command == 'analyze':
        if len(sys.argv) > 2:
            context = ' '.join(sys.argv[2:])
            analyze_perspective(context)
        else:
            print("Usage: analyze 'context to analyze'")
    
    # Team commands
    elif command == 'team':
        if len(sys.argv) > 2:
            member = sys.argv[2]
            show_team(member)
        else:
            show_team()
    
    # Session commands
    elif command == 'startup':
        enhanced_startup()
    
    elif command == 'capture':
        if len(sys.argv) > 2:
            commit_hash = sys.argv[2]
            capture_context(commit_hash)
        else:
            print("Usage: capture <commit_hash>")
    
    elif command == 'status':
        show_unified_status()
    
    elif command == 'summary':
        show_session_summary()
    
    # System commands
    elif command == 'init':
        init_memory_system()
    
    elif command == 'health':
        comprehensive_health_check()
    
    elif command == 'help':
        show_help()
    
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()