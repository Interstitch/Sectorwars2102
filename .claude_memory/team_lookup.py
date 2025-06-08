#!/usr/bin/env python3
"""
Development Team Lookup - Easy reference for Claude's specialist team
====================================================================

Quick reference for the development team personalities that Claude can embody.
"""

def show_team():
    """Show the development team members"""
    
    team = {
        'alex': {
            'name': 'Alex',
            'role': 'Senior System Architect', 
            'emoji': '🏗️',
            'specialty': 'System design, architecture patterns, long-term planning'
        },
        'sam': {
            'name': 'Sam', 
            'role': 'Senior Debugging Specialist',
            'emoji': '🔍',
            'specialty': 'Bug hunting, edge cases, problem investigation'
        },
        'victor': {
            'name': 'Victor',
            'role': 'Performance Engineering Lead',
            'emoji': '⚡', 
            'specialty': 'Performance optimization, efficiency, speed improvements'
        },
        'grace': {
            'name': 'Grace',
            'role': 'Quality Assurance Lead',
            'emoji': '🛡️',
            'specialty': 'Testing strategies, quality validation, QA processes'
        },
        'sophia': {
            'name': 'Sophia',
            'role': 'Technical Documentation Lead', 
            'emoji': '📚',
            'specialty': 'Documentation, knowledge preservation, clarity'
        },
        'simon': {
            'name': 'Simon',
            'role': 'Security Engineering Lead',
            'emoji': '🔒',
            'specialty': 'Security analysis, threat assessment, protection'
        },
        'emma': {
            'name': 'Emma',
            'role': 'User Experience Lead',
            'emoji': '👤', 
            'specialty': 'User experience, accessibility, interface design'
        },
        'marcus': {
            'name': 'Marcus',
            'role': 'Senior Development Mentor',
            'emoji': '🎓',
            'specialty': 'Best practices, mentoring, process improvement'
        }
    }
    
    print("🎭 Claude's Development Team - Specialist Perspectives")
    print("=" * 60)
    
    for key, member in team.items():
        print(f"{member['emoji']} {member['name']} - {member['role']}")
        print(f"   Specialty: {member['specialty']}")
        print(f"   Usage: 'What would {member['name']} think about this?'")
        print()
    
    print("💡 Examples:")
    print("   'Claude, analyze this from Alex's architecture perspective'")
    print("   'What would Sam find wrong with this code?'") 
    print("   'How would Victor optimize this performance issue?'")
    print("   'Ask Grace about testing this feature'")
    print("   'Get Simon's security assessment'")

def quick_lookup(name=None):
    """Quick lookup for team member details"""
    
    team = {
        'alex': '🏗️ Alex - System Architect (design, patterns, architecture)',
        'sam': '🔍 Sam - Debug Specialist (bugs, edge cases, investigation)', 
        'victor': '⚡ Victor - Performance Lead (speed, optimization, efficiency)',
        'grace': '🛡️ Grace - QA Lead (testing, quality, validation)',
        'sophia': '📚 Sophia - Documentation Lead (docs, knowledge, clarity)',
        'simon': '🔒 Simon - Security Lead (security, threats, protection)',
        'emma': '👤 Emma - UX Lead (user experience, accessibility, design)',
        'marcus': '🎓 Marcus - Dev Mentor (best practices, mentoring, growth)'
    }
    
    if name:
        name_lower = name.lower()
        if name_lower in team:
            print(team[name_lower])
        else:
            print(f"Team member '{name}' not found. Available: {', '.join(team.keys())}")
    else:
        print("🎭 Quick Team Reference:")
        for member_info in team.values():
            print(f"   {member_info}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--lookup' and len(sys.argv) > 2:
            quick_lookup(sys.argv[2])
        elif sys.argv[1] == '--quick':
            quick_lookup()
        else:
            show_team()
    else:
        show_team()