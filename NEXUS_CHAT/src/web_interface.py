"""
FastAPI Web Interface for NEXUS Multi-Agent Orchestrator
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .orchestrator import NEXUSOrchestrator
from .models import TaskRequest, TaskResult, TaskStatus
from .config import get_config


# Pydantic models for API
class TaskCreateRequest(BaseModel):
    description: str
    requirements: Optional[List[str]] = None
    technology: Optional[str] = None
    timeline: Optional[str] = None
    priority: str = "medium"
    context: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AgentStatusResponse(BaseModel):
    agent_id: str
    status: str
    current_task: Optional[str] = None
    progress: float
    last_update: datetime


class SystemStatusResponse(BaseModel):
    timestamp: datetime
    active_agents: int
    total_tasks: int
    agents: Dict[str, Any]
    tasks: Dict[str, Any]


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if self.active_connections:
            message_str = json.dumps(message, default=str)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    self.logger.warning(f"Failed to send message to client: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection)

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific client"""
        try:
            message_str = json.dumps(message, default=str)
            await websocket.send_text(message_str)
        except Exception as e:
            self.logger.warning(f"Failed to send personal message: {e}")


class NEXUSWebInterface:
    """
    FastAPI web interface for NEXUS system
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="NEXUS Multi-Agent Orchestrator",
            description="Web interface for NEXUS AI collaboration platform",
            version="1.0.0"
        )
        
        self.config = get_config()
        self.orchestrator = NEXUSOrchestrator(self.config.workspace_path)
        self.connection_manager = ConnectionManager()
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self._setup_routes()
        
        # Setup WebSocket event handlers
        self._setup_websocket_handlers()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize NEXUS on startup"""
            try:
                await self.orchestrator.initialize_agents()
                self.logger.info("NEXUS web interface started successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize NEXUS: {e}")
                raise
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup on shutdown"""
            try:
                await self.orchestrator.shutdown()
                self.logger.info("NEXUS web interface shutdown completed")
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_index():
            """Serve the main web interface"""
            return self._get_html_interface()
        
        @self.app.post("/api/tasks/create", response_model=Dict[str, str])
        async def create_task(request: TaskCreateRequest, background_tasks: BackgroundTasks):
            """Create a new task for NEXUS coordination"""
            try:
                task_id = f"task_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
                
                task_request = TaskRequest(
                    task_id=task_id,
                    description=request.description,
                    requirements=request.requirements,
                    technology=request.technology,
                    timeline=request.timeline,
                    priority=request.priority,
                    context=request.context
                )
                
                # Start task coordination in background
                background_tasks.add_task(self._coordinate_task_with_updates, task_request)
                
                return {"task_id": task_id, "status": "started"}
                
            except Exception as e:
                self.logger.error(f"Failed to create task: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/tasks/{task_id}/status", response_model=TaskStatusResponse)
        async def get_task_status(task_id: str):
            """Get status of a specific task"""
            try:
                progress_info = await self.orchestrator.get_task_progress(task_id)
                
                if not progress_info:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                task_result = self.orchestrator.active_tasks.get(task_id)
                
                return TaskStatusResponse(
                    task_id=task_id,
                    status=task_result.status.value if task_result else "unknown",
                    progress=progress_info["overall_progress"],
                    started_at=task_result.started_at if task_result else None,
                    completed_at=task_result.completed_at if task_result else None,
                    error_message=task_result.error_message if task_result else None
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get task status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/tasks/{task_id}/result", response_model=Dict[str, Any])
        async def get_task_result(task_id: str):
            """Get full result of a completed task"""
            try:
                task_result = self.orchestrator.active_tasks.get(task_id)
                
                if not task_result:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                return {
                    "task_id": task_result.task_id,
                    "status": task_result.status.value,
                    "analysis": task_result.analysis,
                    "implementation": task_result.implementation,
                    "tests": task_result.tests,
                    "validation": task_result.validation,
                    "overall_progress": task_result.overall_progress,
                    "started_at": task_result.started_at,
                    "completed_at": task_result.completed_at,
                    "error_message": task_result.error_message
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get task result: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/api/tasks/{task_id}")
        async def cancel_task(task_id: str):
            """Cancel a running task"""
            try:
                task_result = self.orchestrator.active_tasks.get(task_id)
                
                if not task_result:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                if task_result.status == TaskStatus.COMPLETED:
                    raise HTTPException(status_code=400, detail="Task already completed")
                
                # Update task status to cancelled
                task_result.status = TaskStatus.CANCELLED
                task_result.completed_at = datetime.utcnow()
                
                return {"task_id": task_id, "status": "cancelled"}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to cancel task: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/agents/status", response_model=Dict[str, Any])
        async def get_all_agent_status():
            """Get status of all agents"""
            try:
                return await self.orchestrator.get_all_agent_status()
            except Exception as e:
                self.logger.error(f"Failed to get agent status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/agents/{agent_id}/status", response_model=Dict[str, Any])
        async def get_agent_status(agent_id: str):
            """Get status of specific agent"""
            try:
                status = await self.orchestrator.get_agent_status(agent_id)
                
                if not status:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                return status
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get agent status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/agents/{agent_id}/message")
        async def send_agent_message(agent_id: str, message: Dict[str, str]):
            """Send direct message to an agent"""
            try:
                if agent_id not in self.orchestrator.agents:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                response = await self.orchestrator.delegate_to_agent(
                    agent_id, {"task": "direct_message", "message": message.get("message", "")}
                )
                
                return {"response": response}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to send message to agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/system/status", response_model=SystemStatusResponse)
        async def get_system_status():
            """Get comprehensive system status"""
            try:
                status = await self.orchestrator.get_system_status()
                
                return SystemStatusResponse(
                    timestamp=datetime.fromisoformat(status["timestamp"]),
                    active_agents=status["active_agents"],
                    total_tasks=status["tasks"]["total_tasks"],
                    agents=status["agents"],
                    tasks=status["tasks"]
                )
                
            except Exception as e:
                self.logger.error(f"Failed to get system status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.connection_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    
                    try:
                        message = json.loads(data)
                        await self._handle_websocket_message(message, websocket)
                    except json.JSONDecodeError:
                        await self.connection_manager.send_personal_message(
                            {"error": "Invalid JSON format"}, websocket
                        )
                    
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                self.connection_manager.disconnect(websocket)
    
    async def _handle_websocket_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Handle incoming WebSocket message"""
        message_type = message.get("type")
        
        if message_type == "get_system_status":
            status = await self.orchestrator.get_system_status()
            await self.connection_manager.send_personal_message(
                {"type": "system_status", "data": status}, websocket
            )
        
        elif message_type == "create_task":
            task_data = message.get("data", {})
            task_id = f"task_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            task_request = TaskRequest(
                task_id=task_id,
                description=task_data.get("description", ""),
                requirements=task_data.get("requirements"),
                technology=task_data.get("technology"),
                timeline=task_data.get("timeline"),
                priority=task_data.get("priority", "medium"),
                context=task_data.get("context")
            )
            
            # Start task coordination
            asyncio.create_task(self._coordinate_task_with_updates(task_request))
            
            await self.connection_manager.send_personal_message(
                {"type": "task_created", "task_id": task_id}, websocket
            )
        
        else:
            await self.connection_manager.send_personal_message(
                {"error": f"Unknown message type: {message_type}"}, websocket
            )
    
    async def _coordinate_task_with_updates(self, task_request: TaskRequest):
        """Coordinate task and broadcast updates via WebSocket"""
        try:
            # Subscribe to progress updates
            async def progress_callback(progress_data):
                await self.connection_manager.broadcast({
                    "type": "task_progress",
                    "task_id": task_request.task_id,
                    "data": progress_data
                })
            
            # Subscribe to status updates
            async def status_callback(status_update):
                await self.connection_manager.broadcast({
                    "type": "agent_status",
                    "data": {
                        "agent_id": status_update.agent_id,
                        "status": status_update.status.value if hasattr(status_update.status, 'value') else status_update.status,
                        "timestamp": status_update.timestamp.isoformat(),
                        "current_task": status_update.current_task,
                        "progress": status_update.progress
                    }
                })
            
            await self.orchestrator.feedback_system.progress_tracker.subscribe_to_progress(progress_callback)
            await self.orchestrator.feedback_system.status_broadcaster.subscribe(status_callback)
            
            # Broadcast task start
            await self.connection_manager.broadcast({
                "type": "task_started",
                "task_id": task_request.task_id,
                "description": task_request.description
            })
            
            # Execute task coordination
            result = await self.orchestrator.coordinate_task(task_request)
            
            # Broadcast task completion
            await self.connection_manager.broadcast({
                "type": "task_completed",
                "task_id": task_request.task_id,
                "status": result.status.value,
                "result": {
                    "analysis": result.analysis,
                    "implementation": result.implementation,
                    "tests": result.tests,
                    "validation": result.validation,
                    "overall_progress": result.overall_progress
                }
            })
            
        except Exception as e:
            self.logger.error(f"Task coordination failed: {e}")
            await self.connection_manager.broadcast({
                "type": "task_failed",
                "task_id": task_request.task_id,
                "error": str(e)
            })
    
    def _get_html_interface(self) -> str:
        """Generate HTML interface for NEXUS"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>🧬 NEXUS Multi-Agent Orchestrator</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .status-card h3 {
            margin: 0 0 15px 0;
            font-size: 1.3em;
        }
        .agent-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-active { background-color: #4CAF50; }
        .status-processing { background-color: #FF9800; }
        .status-inactive { background-color: #9E9E9E; }
        .status-error { background-color: #F44336; }
        .task-form {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
        }
        .form-group input::placeholder,
        .form-group textarea::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        .results {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 25px;
            margin-top: 20px;
        }
        .log-entry {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #667eea;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            width: 0%;
            transition: width 0.3s ease;
        }
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .connected {
            background: #4CAF50;
            color: white;
        }
        .disconnected {
            background: #F44336;
            color: white;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">🔴 Connecting...</div>
    
    <div class="container">
        <div class="header">
            <h1>🧬 NEXUS Multi-Agent Orchestrator</h1>
            <p>Revolutionary AI Collaboration Platform</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>🎯 System Status</h3>
                <div id="systemStatus">
                    <div>Active Agents: <span id="activeAgents">-</span></div>
                    <div>Total Tasks: <span id="totalTasks">-</span></div>
                    <div>System Health: <span id="systemHealth">Initializing...</span></div>
                </div>
            </div>
            
            <div class="status-card">
                <h3>👥 Agent Status</h3>
                <div id="agentStatus">
                    <div class="agent-status">
                        <div><span class="status-indicator status-inactive"></span>Aria (Coordinator)</div>
                        <span>Initializing...</span>
                    </div>
                    <div class="agent-status">
                        <div><span class="status-indicator status-inactive"></span>Code (Developer)</div>
                        <span>Initializing...</span>
                    </div>
                    <div class="agent-status">
                        <div><span class="status-indicator status-inactive"></span>Alpha (Test Creator)</div>
                        <span>Initializing...</span>
                    </div>
                    <div class="agent-status">
                        <div><span class="status-indicator status-inactive"></span>Beta (Test Validator)</div>
                        <span>Initializing...</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="task-form">
            <h3>🚀 Create New Task</h3>
            <form id="taskForm">
                <div class="form-group">
                    <label for="description">Task Description *</label>
                    <textarea id="description" rows="3" placeholder="Describe the task you want NEXUS to coordinate..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="technology">Technology Stack</label>
                    <input type="text" id="technology" placeholder="e.g., FastAPI + SQLAlchemy, React + TypeScript">
                </div>
                
                <div class="form-group">
                    <label for="timeline">Timeline</label>
                    <input type="text" id="timeline" placeholder="e.g., 2 hours, 1 day">
                </div>
                
                <div class="form-group">
                    <label for="priority">Priority</label>
                    <select id="priority">
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">🎯 Start NEXUS Coordination</button>
            </form>
        </div>
        
        <div class="results" id="results" style="display: none;">
            <h3>📊 Task Results</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div id="taskProgress">Progress: 0%</div>
            <div id="taskResults"></div>
        </div>
        
        <div class="results">
            <h3>📋 Activity Log</h3>
            <div id="activityLog">
                <div class="log-entry">System initializing...</div>
            </div>
        </div>
    </div>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connectionStatus = document.getElementById('connectionStatus');
        const activityLog = document.getElementById('activityLog');
        const results = document.getElementById('results');
        const progressFill = document.getElementById('progressFill');
        const taskProgress = document.getElementById('taskProgress');
        const taskResults = document.getElementById('taskResults');
        
        let currentTaskId = null;
        
        ws.onopen = function(event) {
            connectionStatus.textContent = '🟢 Connected to NEXUS';
            connectionStatus.className = 'connection-status connected';
            addLogEntry('Connected to NEXUS system');
            
            // Request initial status
            ws.send(JSON.stringify({type: 'get_system_status'}));
        };
        
        ws.onclose = function(event) {
            connectionStatus.textContent = '🔴 Disconnected';
            connectionStatus.className = 'connection-status disconnected';
            addLogEntry('Disconnected from NEXUS system');
        };
        
        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        };
        
        function handleWebSocketMessage(message) {
            switch(message.type) {
                case 'system_status':
                    updateSystemStatus(message.data);
                    break;
                case 'agent_status':
                    updateAgentStatus(message.data);
                    break;
                case 'task_started':
                    currentTaskId = message.task_id;
                    results.style.display = 'block';
                    addLogEntry(`Task started: ${message.description}`);
                    break;
                case 'task_progress':
                    updateTaskProgress(message.data);
                    break;
                case 'task_completed':
                    updateTaskResults(message.result);
                    addLogEntry(`Task completed: ${message.task_id}`);
                    break;
                case 'task_failed':
                    addLogEntry(`Task failed: ${message.error}`);
                    break;
            }
        }
        
        function updateSystemStatus(data) {
            document.getElementById('activeAgents').textContent = data.active_agents;
            document.getElementById('totalTasks').textContent = data.tasks.total_tasks;
            document.getElementById('systemHealth').textContent = 'Online';
        }
        
        function updateAgentStatus(data) {
            // Update agent status indicators
            addLogEntry(`Agent ${data.agent_id}: ${data.status}`);
        }
        
        function updateTaskProgress(data) {
            if (data && data.overall_progress !== undefined) {
                const progress = Math.round(data.overall_progress * 100);
                progressFill.style.width = `${progress}%`;
                taskProgress.textContent = `Progress: ${progress}%`;
                
                if (data.completed_agents) {
                    addLogEntry(`Completed agents: ${data.completed_agents.join(', ')}`);
                }
            }
        }
        
        function updateTaskResults(result) {
            taskResults.innerHTML = `
                <h4>Analysis:</h4>
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 5px; margin: 10px 0; max-height: 200px; overflow-y: auto;">
                    ${result.analysis ? result.analysis.replace(/\\n/g, '<br>') : 'No analysis available'}
                </div>
                
                <h4>Implementation:</h4>
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 5px; margin: 10px 0; max-height: 200px; overflow-y: auto;">
                    ${result.implementation ? result.implementation.replace(/\\n/g, '<br>') : 'No implementation available'}
                </div>
                
                <h4>Tests:</h4>
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 5px; margin: 10px 0; max-height: 200px; overflow-y: auto;">
                    ${result.tests ? result.tests.replace(/\\n/g, '<br>') : 'No tests available'}
                </div>
                
                <h4>Validation:</h4>
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 5px; margin: 10px 0; max-height: 200px; overflow-y: auto;">
                    ${result.validation ? result.validation.replace(/\\n/g, '<br>') : 'No validation available'}
                </div>
            `;
        }
        
        function addLogEntry(message) {
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `[${timestamp}] ${message}`;
            activityLog.insertBefore(logEntry, activityLog.firstChild);
            
            // Keep only last 20 entries
            while (activityLog.children.length > 20) {
                activityLog.removeChild(activityLog.lastChild);
            }
        }
        
        // Handle form submission
        document.getElementById('taskForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const task = {
                description: document.getElementById('description').value,
                technology: document.getElementById('technology').value,
                timeline: document.getElementById('timeline').value,
                priority: document.getElementById('priority').value
            };
            
            ws.send(JSON.stringify({
                type: 'create_task',
                data: task
            }));
            
            // Reset form
            this.reset();
        });
        
        // Periodic status updates
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: 'get_system_status'}));
            }
        }, 10000);
    </script>
</body>
</html>
        '''
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application"""
        return self.app


def create_app() -> FastAPI:
    """Create and configure the NEXUS web application"""
    interface = NEXUSWebInterface()
    return interface.get_app()