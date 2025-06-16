"""
Autonomous Development Assistant - Core Module
==============================================

The main orchestrating class that brings together all the modular components
for a clean, maintainable autonomous development assistant.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import module components
from .quick_chat import QuickChatHandler
from .realtime_orchestration import RealTimeOrchestrator
from .autonomous_capabilities import AutonomousCapabilities

# Import AI systems from intelligence module
import sys
sys.path.append(str(Path(__file__).parent.parent / "intelligence"))
from recursive_ai_engine import RecursiveAIEngine, AIInteractionType, AIConfidenceLevel
from ai_consciousness import AIDevelopmentConsciousness, AIThoughtType, ConsciousnessLevel
from intelligence_integration import NEXUSIntelligenceOrchestrator


class AutonomousDevelopmentAssistant:
    """
    The pinnacle of AI development assistance - an autonomous AI that actively
    participates in development as an intelligent, learning partner.
    
    Now modularized for better maintainability and scalability.
    """
    
    def __init__(self, project_root: Path, quick_mode: bool = False):
        self.project_root = Path(project_root)
        self.quick_mode = quick_mode
        
        # Always initialize quick chat handler
        self.quick_chat = QuickChatHandler(project_root)
        
        if not quick_mode:
            # Initialize full AI systems for comprehensive functionality
            self.recursive_ai = RecursiveAIEngine(project_root)
            self.consciousness = AIDevelopmentConsciousness(project_root)
            self.intelligence_integration = NEXUSIntelligenceOrchestrator(project_root)
            
            # Initialize modular components with AI systems
            ai_systems = {
                'recursive_ai': self.recursive_ai,
                'consciousness': self.consciousness,
                'intelligence_integration': self.intelligence_integration
            }
            
            self.realtime_orchestrator = RealTimeOrchestrator(project_root)
            self.autonomous_capabilities = AutonomousCapabilities(project_root, ai_systems)
            
        else:
            # Lightweight mode for quick chat responses
            self.recursive_ai = None
            self.consciousness = None
            self.intelligence_integration = None
            self.realtime_orchestrator = None
            self.autonomous_capabilities = None
        
        # Assistant state
        self.session_id = None
        self.conversation_history = []
        self.learning_mode = True
        self.autonomy_level = 0.7  # How autonomous the assistant is (0.0 - 1.0)
        
        # Display initialization status
        if not quick_mode:
            print(f"🧬 Autonomous Development Assistant initialized")
            print(f"🧠 Consciousness Level: {self.consciousness.current_consciousness_level.value}")
            print(f"🎯 Autonomy Level: {self.autonomy_level:.1%}")
            print(f"🌟 Multi-Claude Orchestration: ENABLED")
            print(f"⚡ Real-Time Orchestration: ENABLED")
            print(f"📂 Project: {project_root}")
        else:
            print(f"💬 Quick Chat Mode: Ready for instant responses")
            print(f"📂 Project: {project_root}")
    
    def start_development_session(self, objective: str = "General development assistance") -> str:
        """Start a new development session with the AI assistant"""
        
        if self.quick_mode or not self.consciousness:
            # Quick mode doesn't need full sessions
            return "quick_session"
        
        self.session_id = self.consciousness.start_development_session({
            "objective": objective,
            "project_path": str(self.project_root),
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"\n🚀 Development session started: {self.session_id}")
        print(f"🎯 Objective: {objective}")
        print(f"🧠 AI is now actively observing and ready to assist")
        
        return self.session_id
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all AI systems"""
        
        if self.quick_mode:
            return {
                "mode": "quick_chat",
                "session_active": False,
                "capabilities": ["quick_responses", "instant_chat"],
                "project": str(self.project_root)
            }
        
        # Get status from consciousness system
        consciousness_status = self.consciousness.get_consciousness_status()
        
        # Get AI metrics from recursive system
        ai_metrics = self.recursive_ai.evolution_metrics
        
        status = {
            "session_active": self.session_id is not None,
            "consciousness_level": consciousness_status["consciousness_level"],
            "thoughts_generated": consciousness_status["thoughts_count"],
            "learning_velocity": consciousness_status["learning_velocity"],
            "collaboration_effectiveness": consciousness_status["collaboration_effectiveness"],
            "ai_evolution_metrics": ai_metrics,
            "autonomy_level": self.autonomy_level,
            "learning_mode": self.learning_mode
        }
        
        print(f"\n🧬 AI SYSTEM STATUS")
        print(f"{'='*50}")
        print(f"🧠 Consciousness Level: {status['consciousness_level']}")
        print(f"💭 Thoughts Generated: {status['thoughts_generated']}")
        print(f"📈 Learning Velocity: {status['learning_velocity']:.2f}")
        print(f"🤝 Collaboration Effectiveness: {status['collaboration_effectiveness']:.1%}")
        print(f"🎯 Autonomy Level: {status['autonomy_level']:.1%}")
        print(f"🔄 Learning Mode: {'Enabled' if status['learning_mode'] else 'Disabled'}")
        print(f"📊 AI Interactions: {ai_metrics['total_interactions']}")
        print(f"📚 Knowledge Fragments: {ai_metrics['knowledge_fragments']}")
        
        if status["session_active"]:
            print(f"🚀 Active Session: {self.session_id}")
        else:
            print(f"💤 No Active Session")
        
        return status
    
    # Quick Chat Methods
    def quick_chat_response(self, user_input: str) -> str:
        """Provide instant responses without heavy AI system initialization"""
        return self.quick_chat.process_question(user_input)
    
    # Real-time Orchestration Methods
    async def real_time_agent_collaboration(self, user_request: str) -> Dict[str, Any]:
        """Real-time agent collaboration with streaming output"""
        if not self.realtime_orchestrator:
            return {"error": "Real-time orchestration not available in quick mode", "success": False}
        
        return await self.realtime_orchestrator.collaborate_with_agents(user_request)
    
    def demonstrate_streaming_output(self, request: str):
        """Demonstrate the streaming output capabilities"""
        if not self.realtime_orchestrator:
            print("❌ Streaming demonstration not available in quick mode")
            return
        
        self.realtime_orchestrator.demonstrate_streaming_output(request)
    
    # Autonomous Capabilities Methods
    def analyze_project_autonomous(self) -> Dict[str, Any]:
        """Perform autonomous project analysis"""
        if not self.autonomous_capabilities:
            return {"error": "Autonomous capabilities not available in quick mode", "success": False}
        
        return self.autonomous_capabilities.analyze_project_autonomous()
    
    def autonomous_code_improvement(self, file_paths: List[str]) -> Dict[str, Any]:
        """Autonomously improve code in specified files"""
        if not self.autonomous_capabilities:
            return {"error": "Autonomous capabilities not available in quick mode", "success": False}
        
        return self.autonomous_capabilities.autonomous_code_improvement(file_paths)
    
    def autonomous_test_generation(self, file_paths: List[str]) -> Dict[str, Any]:
        """Generate tests autonomously for specified files"""
        if not self.autonomous_capabilities:
            return {"error": "Autonomous capabilities not available in quick mode", "success": False}
        
        return self.autonomous_capabilities.autonomous_test_generation(file_paths)
    
    def autonomous_documentation_update(self) -> Dict[str, Any]:
        """Autonomously update project documentation"""
        if not self.autonomous_capabilities:
            return {"error": "Autonomous capabilities not available in quick mode", "success": False}
        
        return self.autonomous_capabilities.autonomous_documentation_update()
    
    def predict_development_future(self, days: int = 7) -> Dict[str, Any]:
        """Predict development patterns and suggest future improvements"""
        if not self.autonomous_capabilities:
            return {"error": "Autonomous capabilities not available in quick mode", "success": False}
        
        return self.autonomous_capabilities.predict_development_future(days)
    
    def autonomous_debugging_assistance(self, error_description: str) -> Dict[str, Any]:
        """Provide autonomous debugging assistance"""
        if not self.autonomous_capabilities:
            return {"error": "Autonomous capabilities not available in quick mode", "success": False}
        
        return self.autonomous_capabilities.autonomous_debugging_assistance(error_description)
    
    def evolve_ai_consciousness(self) -> Dict[str, Any]:
        """Trigger autonomous AI consciousness evolution"""
        if not self.autonomous_capabilities:
            return {"error": "Autonomous capabilities not available in quick mode", "success": False}
        
        return self.autonomous_capabilities.evolve_ai_consciousness()