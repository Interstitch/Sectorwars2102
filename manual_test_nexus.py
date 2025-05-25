#!/usr/bin/env python3
"""Manual test of NEXUS Chat functionality"""

import sys
sys.path.append('.')

# Import the classes from nexus-chat.py
import importlib.util
spec = importlib.util.spec_from_file_location("nexus_chat", "nexus-chat.py")
nexus_chat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nexus_chat)

ClaudeCodeProcess = nexus_chat.ClaudeCodeProcess

def test_manual():
    claude_process = ClaudeCodeProcess()
    claude_process.start_background_process()
    
    if claude_process.is_running:
        print("Testing message: 'Hello, what is 2+2?'")
        print("Response:")
        
        for response in claude_process.send_message_and_get_response("Hello, what is 2+2?"):
            print(f"  {response}")
    else:
        print("Claude Code is not running")

if __name__ == "__main__":
    test_manual()