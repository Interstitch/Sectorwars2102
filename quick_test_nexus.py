#!/usr/bin/env python3
"""Quick interactive test for NEXUS Chat"""

import subprocess
import time

def test_interactive():
    print("🧪 Testing NEXUS Chat interactively...")
    
    # Start NEXUS Chat process
    process = subprocess.Popen(
        ["python", "nexus-chat.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Send a test question
    test_question = "Hello, what is 2+2?\n"
    process.stdin.write(test_question)
    process.stdin.flush()
    
    # Read output for a few seconds
    time.sleep(3)
    
    # Send exit command
    process.stdin.write("exit\n")
    process.stdin.flush()
    
    # Read all output
    output, _ = process.communicate(timeout=5)
    
    print("Output:")
    print(output)
    
    return "4" in output and "NEXUS:" in output

if __name__ == "__main__":
    success = test_interactive()
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")