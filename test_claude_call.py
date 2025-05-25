#!/usr/bin/env python3
"""Test Claude Code call directly"""

import subprocess
import sys

def test_claude_call():
    message = "Hello, what is 2+2?"
    print(f"Testing Claude call with message: {message}")
    
    try:
        process = subprocess.Popen(
            ["claude", "--print", "--output-format", "stream-json", "--verbose", message],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("Reading output:")
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            clean_line = line.rstrip()
            if clean_line:
                print(f"Raw line: {clean_line}")
                
                try:
                    import json
                    data = json.loads(clean_line)
                    print(f"Parsed JSON: {data}")
                    
                    if data.get('type') == 'assistant' and 'message' in data:
                        message_data = data['message']
                        if 'content' in message_data:
                            for content_item in message_data['content']:
                                if content_item.get('type') == 'text':
                                    print(f"RESPONSE: {content_item.get('text', '')}")
                                    
                except json.JSONDecodeError:
                    print(f"Not JSON, raw content: {clean_line}")
        
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"STDERR: {stderr_output}")
            
        process.wait()
        print(f"Process completed with return code: {process.returncode}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_claude_call()