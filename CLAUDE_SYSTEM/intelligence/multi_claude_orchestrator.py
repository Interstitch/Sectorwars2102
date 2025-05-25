#!/usr/bin/env python3
"""
Multi-Claude Orchestration System - Revolutionary Claude Code Integration
========================================================================

This module implements the cutting-edge multi-Claude workflow patterns discovered
in the Claude Code Best Practices guide. It creates a sophisticated orchestration
system where multiple Claude instances work together using scratchpads for
communication and headless mode for programmatic integration.

🌟 REVOLUTIONARY MULTI-CLAUDE FEATURES:
- Scratchpad-based communication between Claude instances
- Headless mode orchestration using `claude -p`
- Parallel task separation with independent Claude instances
- Verification and review workflows with multiple agents
- Subagent verification for cross-checking work
- Task fanning and pipelining patterns

This represents the next evolution of AI collaboration - multiple Claude instances
working together as a coordinated swarm with explicit communication protocols.

Key Patterns Implemented:
1. Fanning Out: Generate task list, loop through tasks with different Claudes
2. Pipelining: Integrate Claude into data processing workflows
3. Verification: Use one Claude to verify another's work
4. Subagent Review: Independent agents validate implementation details
5. Parallel Separation: Multiple Claudes in separate working contexts

References:
- Claude Code Best Practices: Multi-Claude Workflows
- NEXUS Swarm Intelligence System
- Autonomous Development Assistant
"""

import json
import subprocess
import tempfile
import shutil
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum


class ClaudeWorkflowType(Enum):
    """Types of multi-Claude workflow patterns"""
    FANNING_OUT = "fanning_out"          # Generate tasks, distribute to multiple Claudes
    PIPELINING = "pipelining"            # Sequential processing through different Claudes
    VERIFICATION = "verification"         # One Claude verifies another's work
    SUBAGENT_REVIEW = "subagent_review"  # Independent review of specific aspects
    PARALLEL_TASKS = "parallel_tasks"    # Independent tasks in separate contexts


class ScratchpadType(Enum):
    """Types of scratchpads for Claude communication"""
    TASK_QUEUE = "task_queue"            # Tasks waiting to be processed
    WORK_IN_PROGRESS = "work_in_progress" # Current work being done
    COMPLETED_WORK = "completed_work"    # Finished tasks and results
    VERIFICATION_NOTES = "verification_notes" # Review and verification feedback
    COORDINATION = "coordination"        # Cross-Claude coordination messages


@dataclass
class ClaudeTask:
    """Represents a task for a Claude instance"""
    task_id: str
    task_type: str
    description: str
    input_data: Dict[str, Any]
    scratchpad_refs: List[str]  # Which scratchpads this task should read/write
    claude_instance: Optional[str] = None  # Which Claude instance should handle this
    priority: int = 1
    dependencies: List[str] = None  # Other task IDs this depends on
    estimated_duration: int = 300  # seconds
    created_at: str = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ClaudeInstance:
    """Represents a Claude instance in the orchestration"""
    instance_id: str
    instance_type: str  # analyzer, reviewer, implementer, tester, etc.
    working_directory: Path
    scratchpads_assigned: List[str]
    current_task: Optional[str] = None
    status: str = "idle"  # idle, working, completed, error
    expertise: List[str] = None  # Areas of expertise
    performance_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.expertise is None:
            self.expertise = []
        if self.performance_metrics is None:
            self.performance_metrics = {"tasks_completed": 0, "average_quality": 0.8, "speed_factor": 1.0}


@dataclass
class ScratchpadMessage:
    """Represents a message in a scratchpad"""
    message_id: str
    from_instance: str
    to_instance: Optional[str]  # None for broadcast messages
    message_type: str
    content: Dict[str, Any]
    timestamp: str
    read_by: List[str] = None
    
    def __post_init__(self):
        if self.read_by is None:
            self.read_by = []


class MultiClaudeOrchestrator:
    """
    🌟 REVOLUTIONARY MULTI-CLAUDE ORCHESTRATION SYSTEM 🌟
    
    This orchestrates multiple Claude instances working together using the
    cutting-edge patterns from Claude Code Best Practices. Creates a true
    multi-AI collaboration system with explicit communication protocols.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.orchestration_dir = self.project_root / ".claude" / "multi_claude"
        self.scratchpads_dir = self.orchestration_dir / "scratchpads"
        self.working_dirs_base = self.orchestration_dir / "instances"
        
        # Create directory structure
        self.orchestration_dir.mkdir(parents=True, exist_ok=True)
        self.scratchpads_dir.mkdir(exist_ok=True)
        self.working_dirs_base.mkdir(exist_ok=True)
        
        # Orchestration state
        self.claude_instances: Dict[str, ClaudeInstance] = {}
        self.active_tasks: Dict[str, ClaudeTask] = {}
        self.completed_tasks: Dict[str, ClaudeTask] = {}
        self.scratchpads: Dict[str, List[ScratchpadMessage]] = {}
        
        # Initialize default scratchpads
        for scratchpad_type in ScratchpadType:
            self.scratchpads[scratchpad_type.value] = []
        
        # Performance tracking
        self.workflow_metrics = {
            "workflows_executed": 0,
            "average_task_time": 0.0,
            "success_rate": 0.0,
            "parallel_efficiency": 0.0
        }
        
        print(f"🌟 Multi-Claude Orchestrator initialized")
        print(f"📁 Orchestration directory: {self.orchestration_dir}")
        print(f"🗂️  Scratchpads: {len(self.scratchpads)} types available")
    
    def register_claude_instance(self, instance_type: str, expertise: List[str]) -> str:
        """Register a new Claude instance for orchestration"""
        
        instance_id = f"claude_{instance_type}_{len(self.claude_instances):03d}"
        working_dir = self.working_dirs_base / instance_id
        working_dir.mkdir(exist_ok=True)
        
        # Assign scratchpads based on instance type
        scratchpads_assigned = self._assign_scratchpads_for_instance_type(instance_type)
        
        instance = ClaudeInstance(
            instance_id=instance_id,
            instance_type=instance_type,
            working_directory=working_dir,
            scratchpads_assigned=scratchpads_assigned,
            expertise=expertise
        )
        
        self.claude_instances[instance_id] = instance
        
        print(f"🤖 Registered Claude instance: {instance_id}")
        print(f"   Type: {instance_type}")
        print(f"   Expertise: {', '.join(expertise)}")
        print(f"   Scratchpads: {', '.join(scratchpads_assigned)}")
        print(f"   Working Dir: {working_dir}")
        
        return instance_id
    
    def execute_fanning_out_workflow(self, main_task: str, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute fanning out workflow: Generate task list, distribute to multiple Claudes
        
        This implements the "fanning out" pattern from Claude Code Best Practices
        """
        
        print(f"🌟 Starting Fanning Out Workflow: {main_task}")
        print(f"📋 Distributing {len(subtasks)} subtasks to multiple Claude instances")
        
        # Create Claude instances for different subtasks
        instances_needed = min(len(subtasks), 4)  # Limit to 4 parallel instances
        registered_instances = []
        
        for i in range(instances_needed):
            subtask_type = subtasks[i].get('type', 'general')
            expertise = subtasks[i].get('required_expertise', ['general'])
            instance_id = self.register_claude_instance(f"worker_{subtask_type}", expertise)
            registered_instances.append(instance_id)
        
        # Create tasks for each subtask
        created_tasks = []
        for i, subtask in enumerate(subtasks):
            task_id = f"subtask_{i:03d}_{int(time.time())}"
            instance_id = registered_instances[i % instances_needed]
            
            task = ClaudeTask(
                task_id=task_id,
                task_type=subtask.get('type', 'analysis'),
                description=subtask['description'],
                input_data=subtask.get('input_data', {}),
                scratchpad_refs=[ScratchpadType.TASK_QUEUE.value, ScratchpadType.WORK_IN_PROGRESS.value],
                claude_instance=instance_id,
                priority=subtask.get('priority', 1)
            )
            
            self.active_tasks[task_id] = task
            created_tasks.append(task)
        
        # Write tasks to scratchpads
        self._write_tasks_to_scratchpad(created_tasks)
        
        # Execute tasks in parallel using Claude Code CLI
        results = self._execute_parallel_claude_tasks(created_tasks)
        
        # Aggregate results
        workflow_result = self._aggregate_fanning_out_results(main_task, results)
        
        print(f"✅ Fanning Out Workflow completed!")
        print(f"📊 Tasks processed: {len(results)}")
        print(f"🎯 Success rate: {workflow_result['success_rate']:.1%}")
        
        return workflow_result
    
    def execute_verification_workflow(self, original_work: Dict[str, Any], verification_aspects: List[str]) -> Dict[str, Any]:
        """
        Execute verification workflow: Use multiple Claudes to verify work
        
        This implements the verification pattern from Claude Code Best Practices
        """
        
        print(f"🔍 Starting Verification Workflow")
        print(f"📝 Original work: {original_work.get('title', 'Unknown')}")
        print(f"🎯 Verification aspects: {', '.join(verification_aspects)}")
        
        # Register verifier instances
        verifier_instances = []
        for aspect in verification_aspects:
            instance_id = self.register_claude_instance(f"verifier_{aspect}", [aspect, "verification"])
            verifier_instances.append(instance_id)
        
        # Create verification tasks
        verification_tasks = []
        for i, aspect in enumerate(verification_aspects):
            task_id = f"verify_{aspect}_{int(time.time())}"
            
            task = ClaudeTask(
                task_id=task_id,
                task_type="verification",
                description=f"Verify {aspect} of the provided work",
                input_data={
                    "original_work": original_work,
                    "verification_focus": aspect,
                    "verification_criteria": self._get_verification_criteria(aspect)
                },
                scratchpad_refs=[ScratchpadType.VERIFICATION_NOTES.value, ScratchpadType.COORDINATION.value],
                claude_instance=verifier_instances[i],
                priority=3  # High priority for verification
            )
            
            self.active_tasks[task_id] = task
            verification_tasks.append(task)
        
        # Write verification tasks to scratchpads
        self._write_tasks_to_scratchpad(verification_tasks)
        
        # Execute verification in parallel
        verification_results = self._execute_parallel_claude_tasks(verification_tasks)
        
        # Compile comprehensive verification report
        verification_report = self._compile_verification_report(original_work, verification_results)
        
        print(f"✅ Verification Workflow completed!")
        print(f"🔍 Aspects verified: {len(verification_results)}")
        print(f"📊 Overall verification score: {verification_report['overall_score']:.1%}")
        
        return verification_report
    
    def execute_subagent_review_workflow(self, implementation: Dict[str, Any], review_scope: List[str]) -> Dict[str, Any]:
        """
        Execute subagent review workflow: Independent agents validate specific aspects
        
        This prevents overfitting and improves solution quality
        """
        
        print(f"🔬 Starting Subagent Review Workflow")
        print(f"⚙️  Implementation: {implementation.get('name', 'Unknown')}")
        print(f"🎯 Review scope: {', '.join(review_scope)}")
        
        # Register independent review agents
        review_agents = []
        for scope in review_scope:
            instance_id = self.register_claude_instance(f"reviewer_{scope}", [scope, "independent_review"])
            review_agents.append(instance_id)
        
        # Create independent review tasks
        review_tasks = []
        for i, scope in enumerate(review_scope):
            task_id = f"review_{scope}_{int(time.time())}"
            
            task = ClaudeTask(
                task_id=task_id,
                task_type="independent_review",
                description=f"Independently review {scope} without being influenced by other reviews",
                input_data={
                    "implementation": implementation,
                    "review_scope": scope,
                    "independence_criteria": "Review without seeing other reviews, focus only on your expertise area"
                },
                scratchpad_refs=[ScratchpadType.VERIFICATION_NOTES.value],  # Separate scratchpads for independence
                claude_instance=review_agents[i],
                priority=2
            )
            
            self.active_tasks[task_id] = task
            review_tasks.append(task)
        
        # Execute reviews in complete isolation
        review_results = self._execute_isolated_claude_tasks(review_tasks)
        
        # Synthesize independent reviews
        synthesis_result = self._synthesize_independent_reviews(implementation, review_results)
        
        print(f"✅ Subagent Review Workflow completed!")
        print(f"🔬 Independent reviews: {len(review_results)}")
        print(f"🎯 Consensus score: {synthesis_result['consensus_score']:.1%}")
        
        return synthesis_result
    
    def write_to_scratchpad(self, scratchpad_type: str, from_instance: str, 
                           message_type: str, content: Dict[str, Any], 
                           to_instance: Optional[str] = None) -> str:
        """Write a message to a scratchpad for inter-Claude communication"""
        
        message_id = f"msg_{int(time.time())}_{len(self.scratchpads[scratchpad_type])}"
        
        message = ScratchpadMessage(
            message_id=message_id,
            from_instance=from_instance,
            to_instance=to_instance,
            message_type=message_type,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        
        self.scratchpads[scratchpad_type].append(message)
        
        # Persist to file for Claude instances to read
        self._persist_scratchpad_to_file(scratchpad_type)
        
        return message_id
    
    def read_from_scratchpad(self, scratchpad_type: str, reader_instance: str, 
                            message_types: Optional[List[str]] = None,
                            unread_only: bool = True) -> List[ScratchpadMessage]:
        """Read messages from a scratchpad"""
        
        messages = self.scratchpads[scratchpad_type]
        
        if unread_only:
            messages = [msg for msg in messages if reader_instance not in msg.read_by]
        
        if message_types:
            messages = [msg for msg in messages if msg.message_type in message_types]
        
        # Mark messages as read
        for msg in messages:
            if reader_instance not in msg.read_by:
                msg.read_by.append(reader_instance)
        
        return messages
    
    def execute_claude_with_scratchpads(self, instance_id: str, task: ClaudeTask, 
                                       working_dir: Path) -> Dict[str, Any]:
        """
        Execute Claude Code CLI with explicit scratchpad instructions
        
        This uses the `claude -p` programmatic mode for multi-Claude orchestration
        """
        
        instance = self.claude_instances[instance_id]
        
        # Prepare scratchpad context for Claude
        scratchpad_context = self._prepare_scratchpad_context(task.scratchpad_refs, instance_id)
        
        # Create detailed prompt for Claude with scratchpad instructions
        claude_prompt = self._create_claude_prompt_with_scratchpads(task, scratchpad_context, instance)
        
        # Write prompt to file for programmatic execution
        prompt_file = working_dir / f"task_{task.task_id}_prompt.md"
        with open(prompt_file, 'w') as f:
            f.write(claude_prompt)
        
        # Execute Claude in headless mode
        start_time = time.time()
        
        try:
            # Use claude -p for programmatic execution
            result = subprocess.run([
                "claude", "-p", str(prompt_file),
                "--working-dir", str(working_dir)
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                # Parse Claude's response and update scratchpads
                claude_response = self._parse_claude_response_with_scratchpads(result.stdout, task, instance_id)
                
                return {
                    "success": True,
                    "task_id": task.task_id,
                    "instance_id": instance_id,
                    "execution_time": execution_time,
                    "response": claude_response,
                    "scratchpad_updates": claude_response.get("scratchpad_updates", [])
                }
            else:
                return {
                    "success": False,
                    "task_id": task.task_id,
                    "instance_id": instance_id,
                    "execution_time": execution_time,
                    "error": result.stderr,
                    "output": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "task_id": task.task_id,
                "instance_id": instance_id,
                "execution_time": time.time() - start_time,
                "error": "Task timed out after 10 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "task_id": task.task_id,
                "instance_id": instance_id,
                "execution_time": time.time() - start_time,
                "error": f"Execution error: {str(e)}"
            }
    
    # Private helper methods
    
    def _assign_scratchpads_for_instance_type(self, instance_type: str) -> List[str]:
        """Assign appropriate scratchpads based on instance type"""
        
        base_scratchpads = [ScratchpadType.COORDINATION.value]
        
        type_specific = {
            "analyzer": [ScratchpadType.WORK_IN_PROGRESS.value],
            "reviewer": [ScratchpadType.VERIFICATION_NOTES.value],
            "implementer": [ScratchpadType.TASK_QUEUE.value, ScratchpadType.WORK_IN_PROGRESS.value],
            "tester": [ScratchpadType.VERIFICATION_NOTES.value, ScratchpadType.COMPLETED_WORK.value],
            "coordinator": [pad.value for pad in ScratchpadType]  # Access to all scratchpads
        }
        
        # Extract base type (remove suffixes like _001)
        base_type = instance_type.split('_')[0] if '_' in instance_type else instance_type
        
        return base_scratchpads + type_specific.get(base_type, [ScratchpadType.WORK_IN_PROGRESS.value])
    
    def _write_tasks_to_scratchpad(self, tasks: List[ClaudeTask]) -> None:
        """Write tasks to the task queue scratchpad"""
        
        for task in tasks:
            self.write_to_scratchpad(
                ScratchpadType.TASK_QUEUE.value,
                "orchestrator",
                "task_assignment",
                {
                    "task": asdict(task),
                    "instructions": "Process this task and update work_in_progress scratchpad with your progress"
                },
                task.claude_instance
            )
    
    def _execute_parallel_claude_tasks(self, tasks: List[ClaudeTask]) -> List[Dict[str, Any]]:
        """Execute multiple Claude tasks in parallel"""
        
        results = []
        
        # For now, execute sequentially (can be enhanced with actual parallel execution)
        for task in tasks:
            instance = self.claude_instances[task.claude_instance]
            result = self.execute_claude_with_scratchpads(
                task.claude_instance, 
                task, 
                instance.working_directory
            )
            results.append(result)
        
        return results
    
    def _execute_isolated_claude_tasks(self, tasks: List[ClaudeTask]) -> List[Dict[str, Any]]:
        """Execute Claude tasks in complete isolation (for independent reviews)"""
        
        # Create separate working directories for complete isolation
        isolated_results = []
        
        for task in tasks:
            # Create isolated environment
            isolated_dir = self.working_dirs_base / f"isolated_{task.task_id}"
            isolated_dir.mkdir(exist_ok=True)
            
            # Copy only necessary project files
            self._setup_isolated_environment(isolated_dir, task)
            
            # Execute in isolation
            instance = self.claude_instances[task.claude_instance]
            result = self.execute_claude_with_scratchpads(
                task.claude_instance, 
                task, 
                isolated_dir
            )
            
            isolated_results.append(result)
            
            # Cleanup isolated environment
            shutil.rmtree(isolated_dir, ignore_errors=True)
        
        return isolated_results
    
    def _setup_isolated_environment(self, isolated_dir: Path, task: ClaudeTask) -> None:
        """Setup isolated environment for independent review"""
        
        # Copy only the specific files mentioned in the task
        files_to_copy = task.input_data.get('files', [])
        
        for file_path in files_to_copy:
            source = self.project_root / file_path
            if source.exists():
                dest = isolated_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
    
    def _prepare_scratchpad_context(self, scratchpad_refs: List[str], instance_id: str) -> Dict[str, Any]:
        """Prepare scratchpad context for Claude prompt"""
        
        context = {}
        
        for scratchpad_ref in scratchpad_refs:
            if scratchpad_ref in self.scratchpads:
                messages = self.read_from_scratchpad(scratchpad_ref, instance_id)
                context[scratchpad_ref] = [asdict(msg) for msg in messages]
        
        return context
    
    def _create_claude_prompt_with_scratchpads(self, task: ClaudeTask, 
                                              scratchpad_context: Dict[str, Any], 
                                              instance: ClaudeInstance) -> str:
        """Create detailed prompt for Claude with scratchpad instructions"""
        
        prompt = f"""# Multi-Claude Collaboration Task

## Your Identity
You are Claude instance: {instance.instance_id}
Instance type: {instance.instance_type}
Your expertise: {', '.join(instance.expertise)}

## Task Details
Task ID: {task.task_id}
Task Type: {task.task_type}
Description: {task.description}

## Input Data
{json.dumps(task.input_data, indent=2)}

## Scratchpad Communication Protocol

You have access to the following scratchpads for multi-Claude communication:
{', '.join(task.scratchpad_refs)}

### Current Scratchpad Content:
"""
        
        for scratchpad_ref, messages in scratchpad_context.items():
            prompt += f"\n#### {scratchpad_ref.replace('_', ' ').title()} Scratchpad:\n"
            if messages:
                for msg in messages[-5:]:  # Show last 5 messages
                    prompt += f"- [{msg['timestamp']}] {msg['from_instance']}: {msg['content']}\n"
            else:
                prompt += "- (No messages yet)\n"
        
        prompt += f"""

## Instructions

1. **Process the task** according to your expertise ({', '.join(instance.expertise)})
2. **Read relevant scratchpad messages** to understand context from other Claude instances
3. **Complete your analysis/work** with high quality
4. **Write updates to scratchpads** to communicate with other Claude instances

## Response Format

Structure your response as follows:

### Task Analysis
[Your analysis of the task]

### Work Completed
[The actual work you've done]

### Scratchpad Updates
[Write any messages for other Claude instances in this format:]

SCRATCHPAD_UPDATE: scratchpad_name
FROM: {instance.instance_id}
TO: [target_instance_id or "ALL"]
TYPE: [message_type]
CONTENT: [your message content]
END_SCRATCHPAD_UPDATE

### Summary
[Brief summary of what you accomplished]

## Important Notes
- Focus on your area of expertise: {', '.join(instance.expertise)}
- Communicate clearly with other Claude instances via scratchpads
- Follow the response format exactly so the orchestrator can parse your updates
- Be collaborative and build on what other Claude instances have shared
"""
        
        return prompt
    
    def _parse_claude_response_with_scratchpads(self, response: str, task: ClaudeTask, instance_id: str) -> Dict[str, Any]:
        """Parse Claude's response and extract scratchpad updates"""
        
        import re
        
        # Extract scratchpad updates
        scratchpad_updates = []
        update_pattern = r'SCRATCHPAD_UPDATE: (.+?)\nFROM: (.+?)\nTO: (.+?)\nTYPE: (.+?)\nCONTENT: (.+?)\nEND_SCRATCHPAD_UPDATE'
        
        for match in re.finditer(update_pattern, response, re.DOTALL):
            scratchpad_name, from_instance, to_instance, message_type, content = match.groups()
            
            # Write the update to the scratchpad
            message_id = self.write_to_scratchpad(
                scratchpad_name.strip(),
                from_instance.strip(),
                message_type.strip(),
                {"content": content.strip()},
                to_instance.strip() if to_instance.strip() != "ALL" else None
            )
            
            scratchpad_updates.append({
                "scratchpad": scratchpad_name.strip(),
                "message_id": message_id,
                "type": message_type.strip()
            })
        
        # Extract main response content (remove scratchpad updates)
        clean_response = re.sub(update_pattern, '', response, flags=re.DOTALL)
        
        return {
            "task_id": task.task_id,
            "instance_id": instance_id,
            "response_content": clean_response.strip(),
            "scratchpad_updates": scratchpad_updates
        }
    
    def _persist_scratchpad_to_file(self, scratchpad_type: str) -> None:
        """Persist scratchpad content to file for Claude instances to access"""
        
        scratchpad_file = self.scratchpads_dir / f"{scratchpad_type}.json"
        
        messages_data = [asdict(msg) for msg in self.scratchpads[scratchpad_type]]
        
        with open(scratchpad_file, 'w') as f:
            json.dump(messages_data, f, indent=2)
    
    def _get_verification_criteria(self, aspect: str) -> List[str]:
        """Get verification criteria for different aspects"""
        
        criteria_map = {
            "code_quality": [
                "Code follows best practices",
                "Proper error handling",
                "Clear variable naming",
                "Adequate comments",
                "No code smells"
            ],
            "security": [
                "No security vulnerabilities",
                "Proper input validation",
                "Secure data handling",
                "Authentication checks",
                "No hardcoded secrets"
            ],
            "performance": [
                "Efficient algorithms",
                "Minimal resource usage",
                "Proper optimization",
                "No performance bottlenecks",
                "Scalable implementation"
            ],
            "testing": [
                "Comprehensive test coverage",
                "Edge cases covered",
                "Proper test structure",
                "Mock dependencies correctly",
                "Tests are maintainable"
            ]
        }
        
        return criteria_map.get(aspect, ["General quality check"])
    
    def _aggregate_fanning_out_results(self, main_task: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from fanning out workflow"""
        
        successful_results = [r for r in results if r.get("success", False)]
        success_rate = len(successful_results) / len(results) if results else 0
        
        return {
            "main_task": main_task,
            "total_subtasks": len(results),
            "successful_subtasks": len(successful_results),
            "success_rate": success_rate,
            "results": results,
            "aggregated_insights": self._extract_insights_from_results(successful_results),
            "execution_summary": f"Completed {len(successful_results)}/{len(results)} subtasks successfully"
        }
    
    def _compile_verification_report(self, original_work: Dict[str, Any], 
                                   verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compile comprehensive verification report"""
        
        successful_verifications = [r for r in verification_results if r.get("success", False)]
        
        overall_score = len(successful_verifications) / len(verification_results) if verification_results else 0
        
        return {
            "original_work": original_work,
            "verification_aspects": len(verification_results),
            "successful_verifications": len(successful_verifications),
            "overall_score": overall_score,
            "verification_details": verification_results,
            "recommendations": self._extract_verification_recommendations(verification_results),
            "verification_summary": f"Verified {len(successful_verifications)}/{len(verification_results)} aspects successfully"
        }
    
    def _synthesize_independent_reviews(self, implementation: Dict[str, Any], 
                                      review_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize independent review results"""
        
        successful_reviews = [r for r in review_results if r.get("success", False)]
        
        consensus_score = len(successful_reviews) / len(review_results) if review_results else 0
        
        return {
            "implementation": implementation,
            "independent_reviews": len(review_results),
            "successful_reviews": len(successful_reviews),
            "consensus_score": consensus_score,
            "review_details": review_results,
            "synthesis": self._extract_review_synthesis(review_results),
            "review_summary": f"Independent review by {len(successful_reviews)}/{len(review_results)} agents"
        }
    
    def _extract_insights_from_results(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract key insights from aggregated results"""
        
        insights = []
        
        if results:
            avg_execution_time = sum(r.get("execution_time", 0) for r in results) / len(results)
            insights.append(f"Average task execution time: {avg_execution_time:.1f} seconds")
            
            instances_used = set(r.get("instance_id") for r in results)
            insights.append(f"Distributed across {len(instances_used)} Claude instances")
            
            insights.append(f"All tasks completed with multi-Claude collaboration")
        
        return insights
    
    def _extract_verification_recommendations(self, verification_results: List[Dict[str, Any]]) -> List[str]:
        """Extract recommendations from verification results"""
        
        recommendations = []
        
        for result in verification_results:
            if result.get("success") and "response" in result:
                # Extract key recommendations from Claude's response
                response_content = result["response"].get("response_content", "")
                if "recommend" in response_content.lower():
                    # Simple extraction - in production, would use more sophisticated parsing
                    recommendations.append(f"From {result.get('instance_id', 'verifier')}: See detailed verification")
        
        return recommendations[:5]  # Limit to top 5
    
    def _extract_review_synthesis(self, review_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract synthesis from independent review results"""
        
        synthesis = {
            "consensus_points": [],
            "divergent_opinions": [],
            "overall_assessment": "Mixed reviews from independent agents"
        }
        
        # Analyze review patterns
        successful_reviews = [r for r in review_results if r.get("success", False)]
        
        if len(successful_reviews) >= 2:
            synthesis["overall_assessment"] = "Multiple independent reviews completed successfully"
        elif len(successful_reviews) == 1:
            synthesis["overall_assessment"] = "Single independent review completed"
        else:
            synthesis["overall_assessment"] = "Review process encountered issues"
        
        return synthesis


def main():
    """CLI interface for multi-Claude orchestration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Claude Orchestration System")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--demo", action="store_true", help="Run orchestration demo")
    parser.add_argument("--workflow", choices=["fanning", "verification", "subagent"], 
                       help="Run specific workflow type")
    
    args = parser.parse_args()
    
    orchestrator = MultiClaudeOrchestrator(Path(args.project_root))
    
    if args.demo:
        # Demo the orchestration system
        print("🌟 Multi-Claude Orchestration Demo")
        
        # Register some instances
        analyzer_id = orchestrator.register_claude_instance("analyzer", ["code_analysis", "pattern_recognition"])
        reviewer_id = orchestrator.register_claude_instance("reviewer", ["code_review", "quality_assurance"])
        
        print(f"✅ Demo setup complete with {len(orchestrator.claude_instances)} instances")
        
    elif args.workflow == "fanning":
        # Demo fanning out workflow
        subtasks = [
            {"type": "analysis", "description": "Analyze code quality", "required_expertise": ["code_analysis"]},
            {"type": "security", "description": "Security audit", "required_expertise": ["security"]},
            {"type": "performance", "description": "Performance review", "required_expertise": ["performance"]}
        ]
        
        result = orchestrator.execute_fanning_out_workflow("Code Review", subtasks)
        print(f"Fanning workflow result: {result['success_rate']:.1%} success rate")
        
    else:
        print("Use --demo or --workflow to run the orchestrator")


if __name__ == "__main__":
    main()