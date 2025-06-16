"""
Autonomous Development Assistant Module
======================================

A modular, scalable AI development assistant that provides:
- Quick chat responses for instant feedback
- Real-time multi-Claude orchestration
- Autonomous development capabilities
- Integration with NEXUS AI consciousness systems

This module is broken down into manageable components for better maintainability.
"""

from .core import AutonomousDevelopmentAssistant
from .quick_chat import QuickChatHandler
from .realtime_orchestration import RealTimeOrchestrator
from .autonomous_capabilities import AutonomousCapabilities

__all__ = [
    'AutonomousDevelopmentAssistant',
    'QuickChatHandler', 
    'RealTimeOrchestrator',
    'AutonomousCapabilities'
]

__version__ = "1.0.0"