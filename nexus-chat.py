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
    """Manages the background Claude Code process for instant responses"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.is_ready = threading.Event()
        self.is_running = False
        self.background_thread: Optional[threading.Thread] = None
        
    def start_background_process(self):
        """Start Claude Code in background thread for instant availability"""
        print("🚀 Initializing Claude Code in background...")
        self.background_thread = threading.Thread(target=self._run_claude_code, daemon=True)
        self.background_thread.start()
        
        # Wait for initialization with timeout
        if self.is_ready.wait(timeout=30):
            print("✅ Claude Code ready for instant responses!")
        else:
            print("⚠️  Claude Code initialization taking longer than expected...")
    
    def _run_claude_code(self):
        """Run Claude Code process in interactive mode"""
        try:
            # Start Claude Code CLI - it's already interactive by default
            cmd = ["claude"]
            
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered for real-time streaming
                universal_newlines=True,
                cwd=os.getcwd()  # Use current working directory
            )
            
            self.is_running = True
            
            # Wait a moment for Claude to initialize
            time.sleep(2)
            self.is_ready.set()  # Signal that Claude Code is ready
            
            # Start output reader thread
            output_thread = threading.Thread(target=self._read_output, daemon=True)
            output_thread.start()
            
            # Process input queue
            while self.is_running and self.process and self.process.poll() is None:
                try:
                    message = self.input_queue.get(timeout=1)
                    if message is None:  # Shutdown signal
                        break
                    
                    # Send message to Claude Code
                    self.process.stdin.write(message + "\n")
                    self.process.stdin.flush()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"❌ Error sending to Claude Code: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Failed to start Claude Code: {e}")
            self.is_ready.set()  # Unblock waiting
        finally:
            self.is_running = False
    
    def _read_output(self):
        """Read output from Claude Code and queue it for streaming"""
        if not self.process:
            return
            
        try:
            while self.is_running and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    self.output_queue.put(line.rstrip())
                elif self.process.poll() is not None:
                    break
        except Exception as e:
            print(f"❌ Error reading Claude Code output: {e}")
    
    def send_message(self, message: str):
        """Send message to Claude Code"""
        if self.is_running:
            self.input_queue.put(message)
        else:
            print("❌ Claude Code is not running")
    
    def get_response_stream(self) -> Generator[str, None, None]:
        """Stream responses from Claude Code in real-time"""
        response_lines = []
        start_time = time.time()
        empty_count = 0
        
        while True:
            try:
                # Wait for output with timeout
                line = self.output_queue.get(timeout=0.5)
                response_lines.append(line)
                empty_count = 0  # Reset empty counter
                
                # Skip empty lines but still yield content
                if line.strip():
                    yield line
                
                # Check if response seems complete (improved heuristics)
                if len(response_lines) > 0:
                    # Look for Claude Code prompt patterns or completion indicators
                    if any(pattern in line.lower() for pattern in [
                        "human:", "user:", "assistant:", 
                        "would you like", "anything else",
                        "let me know", "i can help"
                    ]):
                        # Wait a bit more for any trailing content
                        time.sleep(0.5)
                        # Check if there's more content
                        try:
                            extra_line = self.output_queue.get_nowait()
                            if extra_line.strip():
                                yield extra_line
                                continue
                        except queue.Empty:
                            pass
                        break
                        
            except queue.Empty:
                empty_count += 1
                # If we've been waiting too long without output, assume complete
                if len(response_lines) > 0 and empty_count > 4:  # 2 seconds of no output
                    break
                # If we've waited very long with no response at all, timeout
                if time.time() - start_time > 30:
                    break
                continue
    
    def shutdown(self):
        """Gracefully shutdown Claude Code process"""
        print("\n🔄 Shutting down Claude Code...")
        self.is_running = False
        
        if self.process:
            try:
                self.input_queue.put(None)  # Shutdown signal
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
                
        print("✅ Claude Code shutdown complete")

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
            
        # Send message to Claude Code
        self.claude_process.send_message(message)
        
        # Stream response in real-time
        response_received = False
        response_lines = []
        
        try:
            for response_line in self.claude_process.get_response_stream():
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