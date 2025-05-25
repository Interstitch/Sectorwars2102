#!/usr/bin/env python3
"""
NEXUS Chat - Real-time Claude Code Chat Wrapper
A simple pass-through chat interface that pre-initializes Claude Code 
for instant responses with real-time streaming.
"""

import asyncio
import subprocess
import threading
import queue
import sys
import os
import signal
import time
from typing import Optional, Generator
import json

class ClaudeCodeProcess:
    """Manages Claude Code CLI calls for instant responses"""
    
    def __init__(self):
        self.is_running = False
        self.last_call_time = 0
        
    def start_background_process(self):
        """Initialize Claude Code - test that it's available"""
        print("🚀 Initializing Claude Code...")
        try:
            # Test Claude Code CLI availability
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                self.is_running = True
                print("✅ Claude Code ready for instant responses!")
            else:
                print(f"❌ Claude Code CLI error: {result.stderr}")
                self.is_running = False
        except Exception as e:
            print(f"❌ Failed to initialize Claude Code: {e}")
            self.is_running = False
    
    def send_message_and_get_response(self, message: str) -> Generator[str, None, None]:
        """Send message to Claude Code and stream response"""
        if not self.is_running:
            yield "❌ Claude Code is not running"
            return
            
        try:
            # Call Claude Code with --print flag for non-interactive output
            process = subprocess.Popen(
                ["claude", "--print", "--output-format", "stream-json", "--verbose", message],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.getcwd()
            )
            
            # Stream output in real-time
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Clean up the line and yield if it has content
                clean_line = line.rstrip()
                if clean_line:
                    # Try to parse JSON streaming format
                    try:
                        import json
                        data = json.loads(clean_line)
                        
                        # Handle different message types
                        if data.get('type') == 'assistant' and 'message' in data:
                            # Extract content from assistant message
                            message_data = data['message']
                            if 'content' in message_data:
                                for content_item in message_data['content']:
                                    if content_item.get('type') == 'text':
                                        yield content_item.get('text', '')
                        elif data.get('type') == 'system':
                            # Skip system messages (initialization)
                            continue
                        elif data.get('type') == 'result':
                            # Skip result summary messages
                            continue
                        else:
                            # For any other format, try to extract text
                            if 'content' in data:
                                yield str(data['content'])
                            elif 'text' in data:
                                yield str(data['text'])
                                
                    except json.JSONDecodeError:
                        # If not JSON, yield as is (might be plain text)
                        yield clean_line
            
            # Check for any errors
            stderr_output = process.stderr.read()
            if stderr_output:
                yield f"⚠️ Claude Code stderr: {stderr_output.strip()}"
            
            # Wait for process to complete
            process.wait()
            
        except Exception as e:
            yield f"❌ Error calling Claude Code: {e}"
    
    def send_message(self, message: str):
        """Legacy method for compatibility"""
        # This is now handled in send_message_and_get_response
        pass
    
    def get_response_stream(self) -> Generator[str, None, None]:
        """Legacy method for compatibility"""
        # This is now handled in send_message_and_get_response
        yield "⚠️ Using legacy response stream method"
    
    def shutdown(self):
        """Gracefully shutdown"""
        print("\n🔄 Shutting down NEXUS Chat...")
        self.is_running = False
        print("✅ Shutdown complete")

class NexusChat:
    """Main chat interface for NEXUS real-time Claude Code interaction"""
    
    def __init__(self):
        self.claude_process = ClaudeCodeProcess()
        self.running = True
        
    def start(self):
        """Start the NEXUS chat session"""
        print("🌟 NEXUS Chat - Real-time Claude Code Interface")
        print("=" * 50)
        
        # Start Claude Code in background
        self.claude_process.start_background_process()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        # Start interactive chat loop
        self._chat_loop()
    
    def _chat_loop(self):
        """Main interactive chat loop"""
        print("\n💬 Chat started! Type your questions below.")
        print("   Commands: 'exit', 'quit', 'help'")
        print("   Tip: Claude Code is already running in background for instant responses!\n")
        
        try:
            while self.running:
                try:
                    # Get user input
                    user_input = input("🤖 You: ").strip()
                    
                    if not user_input:
                        continue
                        
                    # Handle special commands
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        break
                    elif user_input.lower() in ['help', 'h']:
                        self._show_help()
                        continue
                    
                    # Send to Claude Code and stream response
                    print("🧠 NEXUS: ", end="", flush=True)
                    self._process_message(user_input)
                    print()  # New line after response
                    
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                    
        except Exception as e:
            print(f"❌ Chat error: {e}")
        finally:
            self._shutdown()
    
    def _process_message(self, message: str):
        """Process user message through Claude Code with real-time streaming"""
        if not self.claude_process.is_running:
            print("❌ Claude Code is not running. Please restart NEXUS Chat.")
            return
            
        # Send message to Claude Code and stream response
        response_received = False
        response_lines = []
        
        try:
            for response_line in self.claude_process.send_message_and_get_response(message):
                if response_line.strip():
                    print(response_line, flush=True)
                    response_lines.append(response_line)
                    response_received = True
                    
        except Exception as e:
            print(f"❌ Error while streaming response: {e}")
            
        if not response_received:
            print("⚠️  No response received from Claude Code")
        elif len(response_lines) > 0:
            # Add a subtle separator for better readability
            print("─" * 40)
    
    def _show_help(self):
        """Show help information"""
        print("""
🌟 NEXUS Chat Help
================

Commands:
  exit, quit, q  - Exit the chat
  help, h        - Show this help
  
Features:
  • Real-time streaming responses from Claude Code
  • Background process for instant response times
  • Pass-through interface to full Claude Code capabilities
  
Tips:
  • Ask about your codebase, request code changes, debugging help
  • Claude Code has full access to your project files and tools
  • Responses stream in real-time as they're generated
        """)
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🔄 Received signal {signum}, shutting down...")
        self.running = False
    
    def _shutdown(self):
        """Graceful shutdown"""
        print("\n👋 Goodbye! Thanks for using NEXUS Chat!")
        self.claude_process.shutdown()

def main():
    """Main entry point"""
    # Check if Claude Code CLI is available
    try:
        result = subprocess.run(["claude", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Claude Code CLI not found. Please install it first:")
            print("   curl -fsSL https://install.anthropic.com | sh")
            sys.exit(1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Claude Code CLI not found or not responding. Please install it first:")
        print("   curl -fsSL https://install.anthropic.com | sh")
        sys.exit(1)
    
    # Start NEXUS Chat
    chat = NexusChat()
    try:
        chat.start()
    except KeyboardInterrupt:
        print("\n🔄 Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()