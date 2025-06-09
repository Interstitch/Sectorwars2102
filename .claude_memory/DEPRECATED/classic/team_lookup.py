#!/usr/bin/env python3
"""
Development Team Lookup - Easy reference for Claude's specialist team
====================================================================

Quick reference for the development team personalities that Claude can embody.
"""

def show_team():
    """Show the development team members"""
    
    team = {
        'arthur': {
            'name': 'Arthur',
            'role': 'Senior System Architect', 
            'emoji': '🏗️',
            'specialty': 'System design, architecture patterns, long-term planning'
        },
        'dexter': {
            'name': 'Dexter', 
            'role': 'Senior Debugging Specialist',
            'emoji': '🔍',
            'specialty': 'Bug hunting, edge cases, problem investigation'
        },
        'perry': {
            'name': 'Perry',
            'role': 'Performance Engineering Lead',
            'emoji': '⚡', 
            'specialty': 'Performance optimization, efficiency, speed improvements'
        },
        'tessa': {
            'name': 'Tessa',
            'role': 'Quality Assurance Lead',
            'emoji': '🛡️',
            'specialty': 'Testing strategies, quality validation, QA processes'
        },
        'dora': {
            'name': 'Dora',
            'role': 'Technical Documentation Lead', 
            'emoji': '📚',
            'specialty': 'Documentation, knowledge preservation, clarity'
        },
        'sergio': {
            'name': 'Sergio',
            'role': 'Security Engineering Lead',
            'emoji': '🔒',
            'specialty': 'Security analysis, threat assessment, protection'
        },
        'uxana': {
            'name': 'Uxana',
            'role': 'User Experience Lead',
            'emoji': '👤', 
            'specialty': 'User experience, accessibility, interface design'
        },
        'devara': {
            'name': 'Devara',
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
    print("   'Claude, analyze this from Arthur's architecture perspective'")
    print("   'What would Dexter find wrong with this code?'") 
    print("   'How would Perry optimize this performance issue?'")
    print("   'Ask Tessa about testing this feature'")
    print("   'Get Sergio's security assessment'")

def quick_lookup(name=None):
    """Quick lookup for team member details"""
    
    team = {
        'arthur': '🏗️ Arthur - System Architect (design, patterns, architecture)',
        'dexter': '🔍 Dexter - Debug Specialist (bugs, edge cases, investigation)', 
        'perry': '⚡ Perry - Performance Lead (speed, optimization, efficiency)',
        'tessa': '🛡️ Tessa - QA Lead (testing, quality, validation)',
        'dora': '📚 Dora - Documentation Lead (docs, knowledge, clarity)',
        'sergio': '🔒 Sergio - Security Lead (security, threats, protection)',
        'uxana': '👤 Uxana - UX Lead (user experience, accessibility, design)',
        'devara': '🎓 Devara - Dev Mentor (best practices, mentoring, growth)'
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