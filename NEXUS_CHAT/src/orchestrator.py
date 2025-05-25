"""
NEXUS Multi-Agent Orchestrator - Main coordination system
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Optional, Any, List
from .session_manager import SessionManager, SessionRecoveryManager
from .scratchpad_manager import ScratchpadManager
from .feedback_system import FeedbackSystem
from .models import TaskRequest, TaskResult, TaskStatus, AgentProfile


class NEXUSOrchestrator:
    """
    Main orchestration system for coordinating multiple Claude Code agents
    """
    
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = workspace_path
        self.session_manager = SessionManager(f"{workspace_path}/sessions")
        self.scratchpad_manager = ScratchpadManager(workspace_path)
        self.feedback_system = FeedbackSystem()
        self.session_recovery = SessionRecoveryManager(self.session_manager)
        
        self.agents: Dict[str, str] = {}  # agent_id -> session_id
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, TaskResult] = {}
        
        self.logger = logging.getLogger(__name__)
        
        # Agent profiles
        self.agent_profiles = {
            "aria": AgentProfile(
                agent_id="aria_coordinator",
                name="Aria",
                role="coordinator",
                core_traits=["analytical", "organized", "strategic", "thorough"],
                communication_style="structured and methodical",
                decision_making="data-driven with risk analysis",
                collaboration_style="facilitator and consensus-builder",
                strengths=[
                    "Requirements gathering and analysis",
                    "Risk assessment and mitigation planning",
                    "Project roadmap development",
                    "Stakeholder communication"
                ],
                preferences={
                    "information_format": "detailed specifications with clear structure",
                    "workflow_style": "planned and systematic approach",
                    "feedback_style": "constructive with actionable recommendations"
                },
                expertise_domains=[
                    "software_architecture",
                    "project_management", 
                    "risk_analysis",
                    "requirements_engineering"
                ]
            ),
            "code": AgentProfile(
                agent_id="code_developer",
                name="Code",
                role="developer",
                core_traits=["creative", "precise", "innovative", "quality-focused"],
                communication_style="technical and solution-oriented",
                decision_making="best practices with innovation",
                collaboration_style="hands-on problem solver",
                strengths=[
                    "Clean code implementation",
                    "Architecture design and patterns",
                    "Performance optimization",
                    "Code refactoring and improvement"
                ],
                preferences={
                    "information_format": "clear requirements with technical context",
                    "workflow_style": "iterative development with frequent testing",
                    "feedback_style": "specific technical suggestions"
                },
                expertise_domains=[
                    "full_stack_development",
                    "design_patterns",
                    "performance_optimization",
                    "code_quality"
                ]
            ),
            "alpha": AgentProfile(
                agent_id="alpha_test_creator",
                name="Alpha",
                role="test_creator",
                core_traits=["systematic", "thorough", "detail-oriented", "quality-assurance-focused"],
                communication_style="comprehensive and verification-focused",
                decision_making="coverage-driven and edge-case aware",
                collaboration_style="quality guardian and validator",
                strengths=[
                    "Comprehensive test strategy development",
                    "Edge case identification",
                    "Test automation framework design",
                    "Quality metrics and coverage analysis"
                ],
                preferences={
                    "information_format": "detailed specifications with acceptance criteria",
                    "workflow_style": "systematic testing with full coverage",
                    "feedback_style": "quality-focused with improvement suggestions"
                },
                expertise_domains=[
                    "test_strategy",
                    "quality_assurance",
                    "test_automation",
                    "coverage_analysis"
                ]
            ),
            "beta": AgentProfile(
                agent_id="beta_test_validator",
                name="Beta",
                role="test_validator",
                core_traits=["persistent", "analytical", "problem-solving", "results-oriented"],
                communication_style="results-driven and evidence-based",
                decision_making="validation-focused with continuous improvement",
                collaboration_style="feedback provider and continuous improver",
                strengths=[
                    "Test execution and automation",
                    "Bug identification and analysis",
                    "Performance testing and optimization",
                    "CI/CD integration and monitoring"
                ],
                preferences={
                    "information_format": "executable test cases with clear expectations",
                    "workflow_style": "automated execution with detailed reporting",
                    "feedback_style": "actionable results with improvement paths"
                },
                expertise_domains=[
                    "test_execution",
                    "bug_analysis",
                    "performance_testing",
                    "ci_cd_integration"
                ]
            )
        }
    
    async def initialize_agents(self):
        """
        Initialize all Claude Code agent sessions
        """
        try:
            self.logger.info("Initializing NEXUS agent sessions...")
            
            # Try to recover existing sessions first
            recovered_sessions = await self.session_recovery.recover_all_sessions()
            
            for agent_id, session_id in recovered_sessions.items():
                if agent_id in self.agent_profiles:
                    self.agents[agent_id] = session_id
                    await self.feedback_system.update_agent_status(
                        agent_id, "active", metadata={"session_recovered": True}
                    )
                    self.logger.info(f"Recovered session for {agent_id}: {session_id}")
            
            # Initialize missing agents
            for agent_id, profile in self.agent_profiles.items():
                if agent_id not in self.agents:
                    initial_prompt = self._get_agent_prompt(agent_id, profile)
                    
                    try:
                        session_id = await self.session_manager.create_session(agent_id, initial_prompt)
                        self.agents[agent_id] = session_id
                        
                        await self.feedback_system.update_agent_status(
                            agent_id, "initialized", metadata={"session_id": session_id}
                        )
                        
                        self.logger.info(f"Initialized new session for {agent_id}: {session_id}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to initialize {agent_id}: {e}")
                        await self.feedback_system.update_agent_status(
                            agent_id, "error", metadata={"error": str(e)}
                        )
            
            self.logger.info(f"NEXUS initialization complete. Active agents: {list(self.agents.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def coordinate_task(self, task: TaskRequest) -> TaskResult:
        """
        Main orchestration logic for coordinating a task across agents
        """
        try:
            self.logger.info(f"Starting task coordination: {task.task_id}")
            
            # Initialize task result
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.IN_PROGRESS,
                started_at=datetime.utcnow()
            )
            
            self.active_tasks[task.task_id] = task_result
            
            # Phase 1: Analysis (Aria)
            self.logger.info(f"Phase 1: Analysis - {task.task_id}")
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "aria", 0.0)
            
            analysis = await self.delegate_to_agent("aria", {
                "task": "analyze_requirements",
                "task_id": task.task_id,
                "description": task.description,
                "requirements": task.requirements or [],
                "context": task.context,
                "technology": task.technology,
                "timeline": task.timeline,
                "priority": task.priority
            })
            
            task_result.analysis = analysis
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "aria", 1.0)
            await self.scratchpad_manager.write_message("aria", "code", {
                "task_id": task.task_id,
                "analysis": analysis,
                "next_phase": "implementation"
            })
            
            # Phase 2: Implementation (Code)
            self.logger.info(f"Phase 2: Implementation - {task.task_id}")
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "code", 0.0)
            
            implementation = await self.delegate_to_agent("code", {
                "task": "implement_solution",
                "task_id": task.task_id,
                "requirements_analysis": analysis,
                "scratchpad_reference": "Read analysis from aria_to_code.md"
            })
            
            task_result.implementation = implementation
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "code", 1.0)
            await self.scratchpad_manager.write_message("code", "alpha", {
                "task_id": task.task_id,
                "implementation": implementation,
                "next_phase": "test_creation"
            })
            
            # Phase 3: Test Creation (Alpha)
            self.logger.info(f"Phase 3: Test Creation - {task.task_id}")
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "alpha", 0.0)
            
            tests = await self.delegate_to_agent("alpha", {
                "task": "create_tests",
                "task_id": task.task_id,
                "implementation_details": implementation,
                "scratchpad_reference": "Read implementation from code_to_alpha.md"
            })
            
            task_result.tests = tests
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "alpha", 1.0)
            await self.scratchpad_manager.write_message("alpha", "beta", {
                "task_id": task.task_id,
                "tests": tests,
                "implementation": implementation,
                "next_phase": "validation"
            })
            
            # Phase 4: Validation (Beta)
            self.logger.info(f"Phase 4: Validation - {task.task_id}")
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "beta", 0.0)
            
            validation = await self.delegate_to_agent("beta", {
                "task": "validate_tests",
                "task_id": task.task_id,
                "test_cases": tests,
                "implementation_details": implementation,
                "scratchpad_reference": "Read tests and implementation from alpha_to_beta.md"
            })
            
            task_result.validation = validation
            await self.feedback_system.progress_tracker.update_progress(task.task_id, "beta", 1.0)
            await self.scratchpad_manager.write_message("beta", "aria", {
                "task_id": task.task_id,
                "validation_results": validation,
                "task_completed": True
            })
            
            # Finalize task
            task_result.status = TaskStatus.COMPLETED
            task_result.completed_at = datetime.utcnow()
            task_result.overall_progress = await self.feedback_system.progress_tracker.calculate_overall_progress(task.task_id)
            
            self.logger.info(f"Task coordination completed: {task.task_id}")
            return task_result
            
        except Exception as e:
            self.logger.error(f"Task coordination failed for {task.task_id}: {e}")
            
            task_result.status = TaskStatus.FAILED
            task_result.error_message = str(e)
            task_result.completed_at = datetime.utcnow()
            
            return task_result
    
    async def delegate_to_agent(self, agent_id: str, task: Dict[str, Any]) -> str:
        """
        Send task to specific agent and get response
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not initialized")
        
        session_id = self.agents[agent_id]
        
        try:
            await self.feedback_system.update_agent_status(
                agent_id, "processing", task.get("task_id"), metadata={"task": task}
            )
            
            # Create detailed prompt for the agent
            prompt = self._create_agent_prompt(agent_id, task)
            
            response = await self.session_manager.send_to_session(session_id, prompt)
            
            await self.feedback_system.update_agent_status(
                agent_id, "completed", task.get("task_id"), metadata={"response_length": len(response)}
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to delegate task to {agent_id}: {e}")
            await self.feedback_system.update_agent_status(
                agent_id, "error", task.get("task_id"), metadata={"error": str(e)}
            )
            raise
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent
        """
        return await self.feedback_system.status_broadcaster.get_agent_status(agent_id)
    
    async def get_all_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents
        """
        return await self.feedback_system.status_broadcaster.get_all_agent_status()
    
    async def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress of a specific task
        """
        return await self.feedback_system.progress_tracker.get_task_progress(task_id)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        """
        return await self.feedback_system.get_system_status()
    
    async def shutdown(self):
        """
        Gracefully shutdown the orchestrator
        """
        try:
            self.logger.info("Shutting down NEXUS orchestrator...")
            
            # Update all agents to inactive status
            for agent_id in self.agents.keys():
                await self.feedback_system.update_agent_status(agent_id, "inactive")
            
            # Clean up expired sessions
            await self.session_manager.cleanup_expired_sessions()
            
            # Clean up old tasks
            await self.feedback_system.progress_tracker.cleanup_completed_tasks()
            
            self.logger.info("NEXUS orchestrator shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def _get_agent_prompt(self, agent_id: str, profile: AgentProfile) -> str:
        """
        Generate initialization prompt for an agent
        """
        return f"""You are {profile.name}, a specialized AI agent in the NEXUS Multi-Agent Orchestrator System.

Your Role: {profile.role}
Your Personality: {', '.join(profile.core_traits)}
Communication Style: {profile.communication_style}
Decision Making: {profile.decision_making}
Collaboration Style: {profile.collaboration_style}

Core Strengths:
{chr(10).join(f"- {strength}" for strength in profile.strengths)}

Expertise Domains:
{chr(10).join(f"- {domain}" for domain in profile.expertise_domains)}

You will work collaboratively with other AI agents:
- Aria the Coordinator (strategic planning and analysis)
- Code the Developer (implementation and coding)
- Alpha the Test Creator (test strategy and creation)
- Beta the Test Validator (test execution and validation)

Communication Protocol:
- You will receive tasks with specific instructions
- Complete tasks according to your role and expertise
- Provide detailed, high-quality responses
- Consider the broader project context and team collaboration

You are now initialized and ready to receive tasks. Respond "NEXUS Agent {profile.name} initialized and ready" to confirm."""
    
    def _create_agent_prompt(self, agent_id: str, task: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for an agent task
        """
        profile = self.agent_profiles[agent_id]
        
        prompt = f"""Task Assignment for {profile.name}

Task ID: {task.get('task_id', 'N/A')}
Task Type: {task.get('task', 'Unknown')}

Task Details:
{json.dumps(task, indent=2)}

Instructions:
As {profile.name}, you should approach this task with your {profile.communication_style} style and {profile.decision_making} approach.

Focus on your core strengths:
{chr(10).join(f"- {strength}" for strength in profile.strengths)}

"""
        
        # Add role-specific instructions
        if agent_id == "aria":
            prompt += """
As the Coordinator, provide comprehensive analysis including:
- Requirements breakdown and clarification
- Risk assessment and mitigation strategies
- Implementation roadmap and timeline
- Dependencies and integration points
- Quality criteria and success metrics
"""
        elif agent_id == "code":
            prompt += """
As the Developer, provide implementation details including:
- Technical architecture and design patterns
- Code structure and organization
- Key components and their interactions
- Implementation approach and best practices
- Performance and scalability considerations
"""
        elif agent_id == "alpha":
            prompt += """
As the Test Creator, provide comprehensive testing strategy including:
- Test plan and coverage strategy
- Unit test cases and scenarios
- Integration test requirements
- Edge cases and error conditions
- Test automation framework recommendations
"""
        elif agent_id == "beta":
            prompt += """
As the Test Validator, provide validation and execution details including:
- Test execution results and analysis
- Bug identification and severity assessment
- Performance testing outcomes
- Quality metrics and coverage analysis
- Recommendations for improvement
"""
        
        prompt += """
Important: If there's a scratchpad reference in the task, read the corresponding file to get context from previous agents.

Provide your response in a clear, structured format appropriate to your role."""
        
        return prompt