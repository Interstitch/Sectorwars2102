#!/usr/bin/env python3
"""
NEXUS Quick Chat - Instant Development Assistant
===============================================

This provides instant responses for common development questions without
the 30+ second initialization delay of the full NEXUS system.

For complex tasks requiring the full AI agent orchestration, it automatically
routes to the complete system.
"""

import sys
import subprocess
from pathlib import Path

def quick_chat(question: str) -> str:
    """Get a quick response without heavy AI initialization"""
    
    # Path to the autonomous dev assistant
    assistant_path = Path(__file__).parent / "intelligence" / "autonomous_dev_assistant.py"
    
    try:
        # Run quick chat mode
        result = subprocess.run([
            sys.executable, str(assistant_path), 
            "--quick-chat", question
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"❌ Error: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return "⏱️ Quick chat timed out - the response is taking too long"
    except Exception as e:
        return f"❌ Failed to get quick response: {e}"

def route_to_full_system(question: str) -> str:
    """Route complex questions to the full NEXUS agent system"""
    
    assistant_path = Path(__file__).parent / "intelligence" / "autonomous_dev_assistant.py"
    
    print("🚀 Routing to full NEXUS agent system...")
    print("⚡ This will take 30-60 seconds for complete AI initialization")
    print("🤖 Activating 8 specialized agents with streaming output...")
    print()
    
    try:
        # Run real-time orchestration
        result = subprocess.run([
            sys.executable, str(assistant_path),
            "--realtime", question  
        ], timeout=300)  # 5 minute timeout
        
        return "✅ Full system analysis complete"
        
    except subprocess.TimeoutExpired:
        return "⏱️ Full system analysis timed out"
    except Exception as e:
        return f"❌ Full system error: {e}"

def interactive_chat():
    """Interactive chat session"""
    
    print("💬 NEXUS Quick Chat - Interactive Mode")
    print("=" * 50)
    print("Ask me about:")
    print("• File paths and routes")  
    print("• Project structure")
    print("• Component locations")
    print("• System status")
    print()
    print("For complex tasks, I'll route to the full agent system.")
    print("Type 'exit' or 'quit' to end, 'full:' prefix for full system.")
    print()
    
    while True:
        try:
            question = input("🤖 Question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("👋 Thanks for chatting with NEXUS!")
                break
                
            if question.startswith('full:'):
                # Route to full system
                full_question = question[5:].strip()
                response = route_to_full_system(full_question)
                print(response)
            else:
                # Quick response
                response = quick_chat(question)
                print(response)
                
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for chatting with NEXUS!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main CLI interface"""
    
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_chat()
    elif len(sys.argv) == 2:
        # Single question mode
        question = sys.argv[1]
        
        if question.startswith('full:'):
            # Route to full system
            full_question = question[5:].strip()
            response = route_to_full_system(full_question)
            print(response)
        else:
            # Quick response
            response = quick_chat(question)
            print(response)
    else:
        print("Usage:")
        print("  python nexus-chat.py                    # Interactive mode")
        print("  python nexus-chat.py \"your question\"    # Quick response")
        print("  python nexus-chat.py \"full:question\"    # Route to full system")

if __name__ == "__main__":
    main()