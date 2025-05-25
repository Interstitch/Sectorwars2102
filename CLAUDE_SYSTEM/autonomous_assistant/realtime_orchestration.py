"""
Real-Time Orchestration Handler
===============================

Handles real-time multi-Claude orchestration and streaming output.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Import the orchestration systems from the intelligence module
import sys
sys.path.append(str(Path(__file__).parent.parent / "intelligence"))
from multi_claude_orchestrator import MultiClaudeOrchestrator
from realtime_multi_claude_orchestrator import RealTimeMultiClaudeOrchestrator, RealTimeMessage, MessageType


class RealTimeOrchestrator:
    """Handles real-time multi-Claude orchestration"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.multi_claude = MultiClaudeOrchestrator(project_root)
        self.realtime_orchestrator = RealTimeMultiClaudeOrchestrator(project_root)
    
    async def collaborate_with_agents(self, user_request: str) -> Dict[str, Any]:
        """
        🌟 REVOLUTIONARY: Real-time agent collaboration with streaming output
        
        This shows all 8 NEXUS agents working in parallel with live updates,
        agent selection by Claude Code, and back-and-forth conversations.
        """
        
        print(f"\n🌟 REAL-TIME AGENT COLLABORATION")
        print(f"📝 Request: {user_request}")
        print(f"🚀 Activating live orchestration with streaming output...")
        print("=" * 80)
        
        try:
            # Execute real-time orchestration with live streaming
            result = await self.realtime_orchestrator.real_time_orchestrate(user_request)
            
            print("=" * 80)
            print(f"🎉 REAL-TIME COLLABORATION COMPLETE!")
            print(f"⚡ Total Time: {result.get('execution_time', 'Unknown')} seconds")
            print(f"🤖 Agents Involved: {result.get('agents_count', 0)}")
            print(f"✅ Success Rate: {result.get('success_rate', 'Unknown')}")
            print("=" * 80)
            
            return result
            
        except Exception as e:
            print(f"❌ Real-time collaboration error: {e}")
            return {"error": str(e), "success": False}
    
    def demonstrate_streaming_output(self, request: str):
        """Demonstrate the streaming output capabilities"""
        
        print(f"\n💫 STREAMING OUTPUT DEMONSTRATION")
        print(f"📝 Request: {request}")
        print("=" * 80)
        
        # Custom output handler for demonstration
        def demo_output_handler(message: RealTimeMessage):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] {message.message_type.value.upper()}: {message.content}")
            if message.metadata:
                for key, value in message.metadata.items():
                    print(f"    └─ {key}: {value}")
        
        # Initialize with custom handler
        from realtime_multi_claude_orchestrator import RealTimeOutputHandler
        demo_handler = RealTimeOutputHandler(demo_output_handler)
        
        # Simulate real-time messages
        import time
        
        messages = [
            (MessageType.ORCHESTRATOR, "orchestrator", "🎯 Analyzing request complexity...", {"phase": "analysis"}),
            (MessageType.ORCHESTRATOR, "orchestrator", "🧠 Selecting optimal agents...", {"agents_considered": 8}),
            (MessageType.AGENT_START, "atlas", "🏗️ Atlas starting architectural analysis", {"expertise": ["architecture"]}),
            (MessageType.AGENT_START, "sherlock", "🔍 Sherlock beginning investigation", {"expertise": ["analysis"]}),
            (MessageType.AGENT_UPDATE, "atlas", "Designing system structure...", {"status": "working"}),
            (MessageType.AGENT_UPDATE, "sherlock", "Analyzing code patterns...", {"status": "working"}),
            (MessageType.CONVERSATION, "atlas", "Sherlock, I need your analysis of this design", {"response_to": "sherlock"}),
            (MessageType.CONVERSATION, "sherlock", "Atlas, the design looks solid but needs optimization", {"response_to": "velocity"}),
            (MessageType.AGENT_COMPLETE, "atlas", "Architectural analysis complete", {"insights": 5}),
            (MessageType.AGENT_COMPLETE, "sherlock", "Investigation complete with findings", {"recommendations": 3}),
            (MessageType.ORCHESTRATOR, "orchestrator", "✅ All agents completed successfully", {"success_rate": "100%"})
        ]
        
        for msg_type, agent_id, content, metadata in messages:
            message = RealTimeMessage(
                timestamp=datetime.now().isoformat(),
                message_type=msg_type,
                agent_id=agent_id,
                content=content,
                metadata=metadata
            )
            demo_handler.emit(message)
            time.sleep(0.3)  # Simulate real-time delay
        
        print("=" * 80)
        print("💫 STREAMING DEMONSTRATION COMPLETE!")
        print("🎯 This shows how you'll see live output during real execution")
        print("=" * 80)