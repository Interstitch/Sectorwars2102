#!/usr/bin/env python3
"""
Test the enhanced natural language processing capabilities
"""

import sys
from pathlib import Path

# Add the CLAUDE_SYSTEM to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from intelligence.autonomous_dev_assistant import AutonomousDevelopmentAssistant

def test_enhanced_nlp():
    """Test the enhanced NLP with various complex requests"""
    
    print("🚀 TESTING ENHANCED NATURAL LANGUAGE PROCESSING")
    print("=" * 60)
    
    # Initialize the assistant
    project_root = Path(__file__).parent.parent
    assistant = AutonomousDevelopmentAssistant(project_root)
    
    # Mock conversation context
    context = {
        "project_analyzed": False,
        "recent_files": [],
        "active_tasks": [],
        "user_preferences": {},
        "conversation_history": []
    }
    
    # Test complex creative requests
    test_requests = [
        "Show off what you are capable of. I want you to create a sub-directory called TEST-SITE/ and design into it a 5 page website with test cases.",
        "Build me a simple Python project structure for a web scraper",
        "Can you generate comprehensive test cases for API testing?",
        "I need you to create documentation for a REST API project",
        "Help me design a landing page with modern CSS and responsive design"
    ]
    
    print("🧪 TESTING COMPLEX CREATIVE REQUESTS:\n")
    
    for i, request in enumerate(test_requests, 1):
        print(f"📝 Test {i}: '{request}'")
        print("-" * 50)
        
        try:
            response = assistant._process_natural_language_request(request, context)
            print(f"🤖 NEXUS Response:")
            print(response)
        except Exception as e:
            print(f"❌ Error processing request: {e}")
        
        print("\n" + "=" * 60 + "\n")
    
    print("✨ ENHANCED NLP TESTING COMPLETE!")

if __name__ == "__main__":
    test_enhanced_nlp()