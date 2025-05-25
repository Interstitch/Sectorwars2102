"""
Real-time feedback system for NEXUS Multi-Agent Orchestrator
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from .models import AgentStatusUpdate, TaskStatus


class StatusBroadcaster:
    """
    Handles real-time status broadcasting for agents
    """
    
    def __init__(self):
        self.status_channel = "agent_status"
        self.subscribers: List[Callable] = []
        self.current_status: Dict[str, AgentStatusUpdate] = {}
        self.logger = logging.getLogger(__name__)
    
    async def broadcast_status(self, agent_id: str, status: Dict[str, Any]):
        """
        Broadcast status update for an agent
        """
        try:
            status_update = AgentStatusUpdate(
                agent_id=agent_id,
                timestamp=datetime.utcnow(),
                status=status.get("status", "unknown"),
                current_task=status.get("current_task"),
                progress=status.get("progress", 0.0),
                metadata=status.get("metadata", {})
            )
            
            self.current_status[agent_id] = status_update
            
            # Broadcast to all subscribers
            for subscriber in self.subscribers:
                try:
                    await subscriber(status_update)
                except Exception as e:
                    self.logger.error(f"Error notifying subscriber: {e}")
            
            self.logger.debug(f"Broadcasted status for {agent_id}: {status}")
            
        except Exception as e:
            self.logger.error(f"Failed to broadcast status for {agent_id}: {e}")
    
    async def subscribe(self, callback: Callable):
        """
        Subscribe to status updates
        """
        self.subscribers.append(callback)
        self.logger.info("New subscriber added to status broadcaster")
    
    def unsubscribe(self, callback: Callable):
        """
        Unsubscribe from status updates
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            self.logger.info("Subscriber removed from status broadcaster")
    
    async def get_all_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current status of all agents
        """
        return {
            agent_id: {
                "status": update.status.value if hasattr(update.status, 'value') else update.status,
                "timestamp": update.timestamp.isoformat(),
                "current_task": update.current_task,
                "progress": update.progress,
                "metadata": update.metadata
            }
            for agent_id, update in self.current_status.items()
        }
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent
        """
        update = self.current_status.get(agent_id)
        if update:
            return {
                "status": update.status.value if hasattr(update.status, 'value') else update.status,
                "timestamp": update.timestamp.isoformat(),
                "current_task": update.current_task,
                "progress": update.progress,
                "metadata": update.metadata
            }
        return None
    
    def get_active_agents(self) -> List[str]:
        """
        Get list of agents that have reported status
        """
        return list(self.current_status.keys())


class ProgressTracker:
    """
    Tracks progress of tasks across multiple agents
    """
    
    def __init__(self):
        self.task_progress: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.milestones: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger(__name__)
        self.progress_subscribers: List[Callable] = []
    
    async def update_progress(self, task_id: str, agent_id: str, progress: float, metadata: Optional[Dict[str, Any]] = None):
        """
        Update progress for a specific task and agent
        """
        try:
            if task_id not in self.task_progress:
                self.task_progress[task_id] = {}
            
            self.task_progress[task_id][agent_id] = {
                "progress": max(0.0, min(1.0, progress)),  # Clamp between 0 and 1
                "timestamp": datetime.utcnow().isoformat(),
                "status": "in_progress" if progress < 1.0 else "completed",
                "metadata": metadata or {}
            }
            
            # Broadcast progress update
            await self.broadcast_progress_update(task_id)
            
            self.logger.debug(f"Updated progress for task {task_id}, agent {agent_id}: {progress}")
            
        except Exception as e:
            self.logger.error(f"Failed to update progress for task {task_id}, agent {agent_id}: {e}")
    
    async def calculate_overall_progress(self, task_id: str) -> float:
        """
        Calculate overall progress for a task across all agents
        """
        if task_id not in self.task_progress:
            return 0.0
        
        agent_progress = self.task_progress[task_id]
        if not agent_progress:
            return 0.0
        
        total_progress = sum(data["progress"] for data in agent_progress.values())
        return total_progress / len(agent_progress)
    
    async def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed progress information for a task
        """
        if task_id not in self.task_progress:
            return None
        
        agent_progress = self.task_progress[task_id]
        overall_progress = await self.calculate_overall_progress(task_id)
        
        return {
            "task_id": task_id,
            "overall_progress": overall_progress,
            "agent_progress": agent_progress,
            "completed_agents": [
                agent_id for agent_id, data in agent_progress.items()
                if data["progress"] >= 1.0
            ],
            "active_agents": [
                agent_id for agent_id, data in agent_progress.items()
                if 0 < data["progress"] < 1.0
            ],
            "pending_agents": [
                agent_id for agent_id, data in agent_progress.items()
                if data["progress"] == 0.0
            ]
        }
    
    async def add_milestone(self, task_id: str, milestone: str, agent_id: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a milestone for a task
        """
        try:
            if task_id not in self.milestones:
                self.milestones[task_id] = []
            
            milestone_data = {
                "milestone": milestone,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.milestones[task_id].append(milestone_data)
            
            self.logger.info(f"Added milestone for task {task_id}: {milestone} (by {agent_id})")
            
        except Exception as e:
            self.logger.error(f"Failed to add milestone for task {task_id}: {e}")
    
    async def get_task_milestones(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all milestones for a task
        """
        return self.milestones.get(task_id, [])
    
    async def subscribe_to_progress(self, callback: Callable):
        """
        Subscribe to progress updates
        """
        self.progress_subscribers.append(callback)
        self.logger.info("New subscriber added to progress tracker")
    
    def unsubscribe_from_progress(self, callback: Callable):
        """
        Unsubscribe from progress updates
        """
        if callback in self.progress_subscribers:
            self.progress_subscribers.remove(callback)
            self.logger.info("Subscriber removed from progress tracker")
    
    async def broadcast_progress_update(self, task_id: str):
        """
        Broadcast progress update to all subscribers
        """
        try:
            progress_data = await self.get_task_progress(task_id)
            
            for subscriber in self.progress_subscribers:
                try:
                    await subscriber(progress_data)
                except Exception as e:
                    self.logger.error(f"Error notifying progress subscriber: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to broadcast progress update for task {task_id}: {e}")
    
    def get_all_tasks(self) -> List[str]:
        """
        Get list of all tracked tasks
        """
        return list(self.task_progress.keys())
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """
        Get overview of all tasks and their progress
        """
        overview = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tasks": len(self.task_progress),
            "tasks": {}
        }
        
        for task_id in self.task_progress.keys():
            task_progress = await self.get_task_progress(task_id)
            if task_progress:
                overview["tasks"][task_id] = {
                    "overall_progress": task_progress["overall_progress"],
                    "completed_agents": len(task_progress["completed_agents"]),
                    "active_agents": len(task_progress["active_agents"]),
                    "pending_agents": len(task_progress["pending_agents"]),
                    "milestones": len(await self.get_task_milestones(task_id))
                }
        
        return overview
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """
        Clean up completed tasks older than specified hours
        """
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        tasks_to_remove = []
        
        for task_id, agent_data in self.task_progress.items():
            # Check if task is completed and old
            all_completed = all(data["progress"] >= 1.0 for data in agent_data.values())
            
            if all_completed:
                # Check if all timestamps are old enough
                oldest_timestamp = min(
                    datetime.fromisoformat(data["timestamp"]).timestamp()
                    for data in agent_data.values()
                )
                
                if oldest_timestamp < cutoff_time:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.task_progress[task_id]
            if task_id in self.milestones:
                del self.milestones[task_id]
        
        if tasks_to_remove:
            self.logger.info(f"Cleaned up {len(tasks_to_remove)} completed tasks")


class FeedbackSystem:
    """
    Combined feedback system integrating status broadcasting and progress tracking
    """
    
    def __init__(self):
        self.status_broadcaster = StatusBroadcaster()
        self.progress_tracker = ProgressTracker()
        self.logger = logging.getLogger(__name__)
    
    async def update_agent_status(self, agent_id: str, status: str, task_id: Optional[str] = None, progress: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Update both agent status and task progress
        """
        # Update agent status
        status_data = {
            "status": status,
            "current_task": task_id,
            "progress": progress or 0.0,
            "metadata": metadata or {}
        }
        
        await self.status_broadcaster.broadcast_status(agent_id, status_data)
        
        # Update task progress if provided
        if task_id and progress is not None:
            await self.progress_tracker.update_progress(task_id, agent_id, progress, metadata)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        """
        agent_status = await self.status_broadcaster.get_all_agent_status()
        system_overview = await self.progress_tracker.get_system_overview()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "agents": agent_status,
            "tasks": system_overview,
            "active_agents": len(agent_status),
            "total_tasks": system_overview["total_tasks"]
        }