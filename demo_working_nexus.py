#!/usr/bin/env python3
"""
Demonstrate NEXUS Chat working with real Claude Code calls
"""

import subprocess
import sys

def demo_nexus_chat():
    """Show NEXUS Chat working with actual Claude Code"""
    print("🌟 NEXUS Chat - Working Demo")
    print("=" * 40)
    
    questions = [
        "Hello, what is 2+2?",
        "What files are in the current directory?",
        "What is the purpose of this project?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Demo {i}: {question}")
        print("─" * 40)
        
        # Use echo to pipe the question to NEXUS Chat
        try:
            result = subprocess.run(
                f'echo "{question}" | python nexus-chat.py',
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Extract the NEXUS response from the output
                lines = result.stdout.strip().split('\n')
                response_started = False
                
                for line in lines:
                    if "🧠 NEXUS:" in line:
                        response_started = True
                        # Print the response part
                        response = line.split("🧠 NEXUS:", 1)[1].strip()
                        if response:
                            print(f"🤖 Response: {response}")
                    elif response_started and line.strip() and not line.startswith("🤖") and not line.startswith("👋"):
                        print(f"           {line.strip()}")
                    elif "────────" in line:
                        break
                        
                if not response_started:
                    print("⚠️  No clear response found in output")
                    
            else:
                print(f"❌ Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout - Claude Code took too long")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Demo complete!")
    print("\nTo use NEXUS Chat interactively:")
    print("  python nexus-chat.py")

if __name__ == "__main__":
    demo_nexus_chat()