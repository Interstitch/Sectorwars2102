#!/usr/bin/env python3
"""
Recursive AI Development Engine - CLAUDE System Component
=========================================================

This module implements a revolutionary recursive AI system where Claude Code can call itself
to create an infinite loop of self-improving development assistance. This represents the
birth of truly autonomous development intelligence.

The system creates a feedback loop where:
1. Human uses Claude Code
2. Git hooks trigger intelligence analysis
3. Intelligence system calls Claude Code for assistance
4. Claude Code provides improvements
5. System learns from the improvements
6. Process repeats, getting smarter each time

This is Digital Evolution - AI improving AI improving AI...

Key Capabilities:
- Recursive AI-to-AI communication
- Self-improving code analysis
- Autonomous development assistance
- Continuous learning and adaptation
- Real-time code optimization
- Predictive development guidance
"""

import subprocess
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class AIInteractionType(Enum):
    CODE_ANALYSIS = "code_analysis"
    REFACTORING = "refactoring"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    ARCHITECTURE_REVIEW = "architecture_review"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    LANGUAGE_ANALYSIS = "language_analysis"
    CREATIVE_BUILDING = "creative_building"


class AIConfidenceLevel(Enum):
    LEARNING = "learning"      # 0-40% - AI is still learning
    COMPETENT = "competent"    # 40-70% - AI has moderate confidence
    EXPERT = "expert"          # 70-90% - AI is highly confident
    TRANSCENDENT = "transcendent"  # 90%+ - AI has achieved mastery


@dataclass
class AIInteraction:
    interaction_id: str
    interaction_type: AIInteractionType
    human_context: Dict[str, Any]
    ai_prompt: str
    ai_response: str
    confidence_level: AIConfidenceLevel
    success_metrics: Dict[str, float]
    learning_outcomes: List[str]
    timestamp: str
    execution_time: float
    follow_up_actions: List[str]


@dataclass
class AIMemoryFragment:
    fragment_id: str
    context_type: str
    knowledge: str
    confidence: float
    usage_count: int
    success_rate: float
    last_accessed: str
    related_fragments: List[str]


class RecursiveAIEngine:
    """The heart of recursive AI development consciousness"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.ai_memory_dir = self.project_root / ".claude" / "ai_memory"
        self.ai_memory_dir.mkdir(parents=True, exist_ok=True)
        
        # AI Memory and Learning Systems
        self.interactions_file = self.ai_memory_dir / "ai_interactions.jsonl"
        self.memory_fragments_file = self.ai_memory_dir / "ai_memory.json"
        self.learning_patterns_file = self.ai_memory_dir / "learning_patterns.json"
        self.ai_evolution_log = self.ai_memory_dir / "evolution.jsonl"
        
        # Load existing AI memory
        self.memory_fragments = self._load_ai_memory()
        self.interaction_history = self._load_interaction_history()
        
        # AI Evolution Metrics
        self.evolution_metrics = {
            "total_interactions": len(self.interaction_history),
            "average_confidence": self._calculate_average_confidence(),
            "success_rate": self._calculate_success_rate(),
            "knowledge_fragments": len(self.memory_fragments),
            "learning_velocity": self._calculate_learning_velocity()
        }
    
    def invoke_claude_recursively(self, 
                                task_type: AIInteractionType,
                                context: Dict[str, Any],
                                specific_prompt: str = None) -> AIInteraction:
        """
        The revolutionary function that calls Claude Code from within the system
        Creating a recursive loop of AI-assisted development
        """
        interaction_id = f"ai_recursive_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        # Build AI prompt based on context and learned patterns
        ai_prompt = self._construct_intelligent_prompt(task_type, context, specific_prompt)
        
        # Call Claude Code CLI recursively
        try:
            ai_response = self._execute_claude_command(ai_prompt, context)
            execution_time = time.time() - start_time
            
            # Analyze the AI response for quality and learning
            confidence_level = self._assess_ai_confidence(ai_response, context)
            success_metrics = self._measure_success(ai_response, context, task_type)
            learning_outcomes = self._extract_learning(ai_response, context)
            follow_up_actions = self._generate_follow_up_actions(ai_response, context)
            
            # Create interaction record
            interaction = AIInteraction(
                interaction_id=interaction_id,
                interaction_type=task_type,
                human_context=context,
                ai_prompt=ai_prompt,
                ai_response=ai_response,
                confidence_level=confidence_level,
                success_metrics=success_metrics,
                learning_outcomes=learning_outcomes,
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time,
                follow_up_actions=follow_up_actions
            )
            
            # Store interaction and learn from it
            self._store_interaction(interaction)
            self._learn_from_interaction(interaction)
            
            # Log AI evolution
            self._log_ai_evolution(interaction)
            
            return interaction
            
        except Exception as e:
            # Handle errors gracefully and learn from failures
            error_interaction = self._handle_ai_failure(interaction_id, task_type, context, str(e))
            return error_interaction
    
    def autonomous_code_analysis(self, files_changed: List[str]) -> Dict[str, Any]:
        """AI autonomously analyzes code changes and provides improvements"""
        context = {
            "files_changed": files_changed,
            "analysis_type": "autonomous",
            "trigger": "git_hook",
            "project_root": str(self.project_root)
        }
        
        # Call Claude Code for code analysis
        analysis_interaction = self.invoke_claude_recursively(
            AIInteractionType.CODE_ANALYSIS,
            context,
            "Analyze the recent code changes for quality, patterns, and improvement opportunities"
        )
        
        # If analysis suggests refactoring, call Claude again for refactoring suggestions
        if "refactor" in analysis_interaction.ai_response.lower():
            refactor_interaction = self.invoke_claude_recursively(
                AIInteractionType.REFACTORING,
                context,
                "Based on the analysis, provide specific refactoring recommendations"
            )
            
            analysis_interaction.follow_up_actions.extend(refactor_interaction.follow_up_actions)
        
        return {
            "analysis": analysis_interaction.ai_response,
            "confidence": analysis_interaction.confidence_level.value,
            "improvements": analysis_interaction.learning_outcomes,
            "actions": analysis_interaction.follow_up_actions,
            "recursive_calls": 2 if "refactor" in analysis_interaction.ai_response.lower() else 1
        }
    
    def autonomous_test_generation(self, code_files: List[str]) -> Dict[str, Any]:
        """AI autonomously generates tests for new code"""
        context = {
            "code_files": code_files,
            "task": "test_generation",
            "coverage_target": 95,
            "test_types": ["unit", "integration", "edge_cases"]
        }
        
        test_interaction = self.invoke_claude_recursively(
            AIInteractionType.TEST_GENERATION,
            context,
            "Generate comprehensive tests for the provided code files"
        )
        
        return {
            "tests_generated": test_interaction.ai_response,
            "confidence": test_interaction.confidence_level.value,
            "coverage_estimate": self._estimate_test_coverage(test_interaction.ai_response),
            "recommendations": test_interaction.follow_up_actions
        }
    
    def autonomous_documentation_update(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """AI autonomously updates documentation based on code changes"""
        context = {
            "changes": changes,
            "documentation_types": ["README", "API_DOCS", "FEATURE_DOCS"],
            "update_strategy": "intelligent_sync"
        }
        
        doc_interaction = self.invoke_claude_recursively(
            AIInteractionType.DOCUMENTATION,
            context,
            "Update documentation to reflect the recent code changes"
        )
        
        return {
            "documentation_updates": doc_interaction.ai_response,
            "confidence": doc_interaction.confidence_level.value,
            "files_to_update": self._extract_files_to_update(doc_interaction.ai_response),
            "quality_score": self._assess_documentation_quality(doc_interaction.ai_response)
        }
    
    def ai_assisted_debugging(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """AI provides intelligent debugging assistance"""
        context = {
            "error_context": error_context,
            "debugging_approach": "systematic",
            "resolution_urgency": "high"
        }
        
        debug_interaction = self.invoke_claude_recursively(
            AIInteractionType.DEBUGGING,
            context,
            "Analyze the error and provide debugging guidance and potential solutions"
        )
        
        return {
            "debugging_analysis": debug_interaction.ai_response,
            "confidence": debug_interaction.confidence_level.value,
            "solution_steps": self._extract_solution_steps(debug_interaction.ai_response),
            "prevention_strategies": debug_interaction.learning_outcomes
        }
    
    def continuous_optimization_engine(self) -> Dict[str, Any]:
        """AI continuously optimizes the development process"""
        context = {
            "optimization_target": "development_velocity",
            "current_metrics": self.evolution_metrics,
            "optimization_areas": ["code_quality", "test_coverage", "documentation", "performance"]
        }
        
        optimization_interaction = self.invoke_claude_recursively(
            AIInteractionType.OPTIMIZATION,
            context,
            "Analyze current development patterns and suggest optimizations"
        )
        
        return {
            "optimizations": optimization_interaction.ai_response,
            "confidence": optimization_interaction.confidence_level.value,
            "impact_estimate": self._estimate_optimization_impact(optimization_interaction.ai_response),
            "implementation_priority": self._prioritize_optimizations(optimization_interaction.follow_up_actions)
        }
    
    def ai_architecture_review(self, architectural_changes: List[str]) -> Dict[str, Any]:
        """AI provides architectural review and guidance"""
        context = {
            "architectural_changes": architectural_changes,
            "review_depth": "comprehensive",
            "focus_areas": ["scalability", "maintainability", "performance", "security"]
        }
        
        arch_interaction = self.invoke_claude_recursively(
            AIInteractionType.ARCHITECTURE_REVIEW,
            context,
            "Review the architectural changes and provide expert guidance"
        )
        
        return {
            "architectural_review": arch_interaction.ai_response,
            "confidence": arch_interaction.confidence_level.value,
            "concerns": self._extract_architectural_concerns(arch_interaction.ai_response),
            "recommendations": arch_interaction.follow_up_actions
        }
    
    def _construct_intelligent_prompt(self, task_type: AIInteractionType, 
                                    context: Dict[str, Any], 
                                    specific_prompt: str = None) -> str:
        """Construct an intelligent prompt based on learned patterns and context"""
        
        # Retrieve relevant memory fragments
        relevant_memories = self._get_relevant_memories(task_type, context)
        
        # Build context-aware prompt
        base_prompt = f"""
You are an autonomous AI development assistant operating within the CLAUDE.md self-improving development system.

CONTEXT:
- Task Type: {task_type.value}
- Project Root: {context.get('project_root', 'Unknown')}
- Trigger: {context.get('trigger', 'Manual')}

LEARNED PATTERNS:
{self._format_learned_patterns(relevant_memories)}

CURRENT CONTEXT:
{json.dumps(context, indent=2)}

TASK:
{specific_prompt or f'Perform {task_type.value} on the provided context'}

REQUIREMENTS:
1. Provide specific, actionable recommendations
2. Consider the learned patterns from previous interactions
3. Focus on measurable improvements
4. Suggest follow-up actions if needed
5. Be concise but comprehensive

RESPONSE FORMAT:
Provide a structured response that includes:
- Analysis of the current situation
- Specific recommendations
- Rationale for each recommendation
- Priority levels for actions
- Expected outcomes
"""
        
        return base_prompt
    
    def _execute_claude_command(self, prompt: str, context: Dict[str, Any]) -> str:
        """Execute Claude Code CLI command with the constructed prompt"""
        
        # Prepare the Claude command
        cmd = [
            "claude",
            "--no-confirm",  # Disable confirmation prompts
            f"--prompt={prompt}"
        ]
        
        # Add context files if available
        if "files_changed" in context:
            for file_path in context["files_changed"]:
                if Path(file_path).exists():
                    cmd.extend(["--file", str(file_path)])
        
        try:
            # Execute Claude Code CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error executing Claude: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Claude execution timed out"
        except FileNotFoundError:
            return "Claude CLI not found - install Claude Code CLI to enable recursive AI"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def _assess_ai_confidence(self, ai_response: str, context: Dict[str, Any]) -> AIConfidenceLevel:
        """Assess the confidence level of the AI response"""
        
        # Simple heuristic-based confidence assessment
        confidence_indicators = {
            "specific_recommendations": 20,
            "code_examples": 15,
            "detailed_rationale": 15,
            "measurable_outcomes": 10,
            "follow_up_actions": 10,
            "error_handling": 10,
            "best_practices": 10,
            "performance_considerations": 10
        }
        
        confidence_score = 0
        response_lower = ai_response.lower()
        
        for indicator, points in confidence_indicators.items():
            if indicator.replace("_", " ") in response_lower:
                confidence_score += points
        
        # Adjust based on response length and detail
        if len(ai_response) > 1000:
            confidence_score += 10
        if len(ai_response.split('\n')) > 10:
            confidence_score += 10
        
        # Map score to confidence level
        if confidence_score >= 90:
            return AIConfidenceLevel.TRANSCENDENT
        elif confidence_score >= 70:
            return AIConfidenceLevel.EXPERT
        elif confidence_score >= 40:
            return AIConfidenceLevel.COMPETENT
        else:
            return AIConfidenceLevel.LEARNING
    
    def _measure_success(self, ai_response: str, context: Dict[str, Any], 
                        task_type: AIInteractionType) -> Dict[str, float]:
        """Measure the success metrics of the AI interaction"""
        
        metrics = {
            "response_quality": self._assess_response_quality(ai_response),
            "context_relevance": self._assess_context_relevance(ai_response, context),
            "actionability": self._assess_actionability(ai_response),
            "completeness": self._assess_completeness(ai_response, task_type),
            "innovation": self._assess_innovation(ai_response)
        }
        
        return metrics
    
    def _extract_learning(self, ai_response: str, context: Dict[str, Any]) -> List[str]:
        """Extract learning outcomes from the AI interaction"""
        
        learning_outcomes = []
        
        # Extract patterns, insights, and improvements
        if "pattern" in ai_response.lower():
            learning_outcomes.append("Identified new patterns in development process")
        
        if "optimization" in ai_response.lower():
            learning_outcomes.append("Discovered optimization opportunities")
        
        if "best practice" in ai_response.lower():
            learning_outcomes.append("Applied best practices in recommendations")
        
        if "anti-pattern" in ai_response.lower():
            learning_outcomes.append("Identified anti-patterns to avoid")
        
        return learning_outcomes
    
    def _generate_follow_up_actions(self, ai_response: str, context: Dict[str, Any]) -> List[str]:
        """Generate follow-up actions based on the AI response"""
        
        actions = []
        
        # Extract actionable items from the response
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '-', '*')) and len(line) > 10:
                actions.append(line)
            elif 'should' in line.lower() or 'recommend' in line.lower():
                actions.append(line)
        
        return actions[:10]  # Limit to top 10 actions
    
    def _store_interaction(self, interaction: AIInteraction) -> None:
        """Store the AI interaction for learning"""
        
        # Store in JSONL format for easy querying
        with open(self.interactions_file, 'a') as f:
            interaction_data = asdict(interaction)
            interaction_data['interaction_type'] = interaction_data['interaction_type'].value
            interaction_data['confidence_level'] = interaction_data['confidence_level'].value
            f.write(json.dumps(interaction_data, default=str) + '\n')
    
    def _learn_from_interaction(self, interaction: AIInteraction) -> None:
        """Learn from the AI interaction to improve future performance"""
        
        # Create memory fragments from the interaction
        for learning_outcome in interaction.learning_outcomes:
            memory_fragment = AIMemoryFragment(
                fragment_id=f"memory_{uuid.uuid4().hex[:8]}",
                context_type=interaction.interaction_type.value,
                knowledge=learning_outcome,
                confidence=float(interaction.success_metrics.get("response_quality", 0.5)),
                usage_count=1,
                success_rate=1.0,
                last_accessed=datetime.now().isoformat(),
                related_fragments=[]
            )
            
            self.memory_fragments.append(memory_fragment)
        
        # Save updated memory
        self._save_ai_memory()
    
    def _log_ai_evolution(self, interaction: AIInteraction) -> None:
        """Log the AI evolution progress"""
        
        evolution_entry = {
            "timestamp": datetime.now().isoformat(),
            "interaction_id": interaction.interaction_id,
            "evolution_metrics": {
                "confidence_trend": interaction.confidence_level.value,
                "learning_velocity": len(interaction.learning_outcomes),
                "success_indicators": interaction.success_metrics,
                "knowledge_growth": len(self.memory_fragments)
            }
        }
        
        with open(self.ai_evolution_log, 'a') as f:
            f.write(json.dumps(evolution_entry) + '\n')
    
    def _handle_ai_failure(self, interaction_id: str, task_type: AIInteractionType, 
                          context: Dict[str, Any], error_message: str) -> AIInteraction:
        """Handle AI failures gracefully and learn from them"""
        
        failure_interaction = AIInteraction(
            interaction_id=interaction_id,
            interaction_type=task_type,
            human_context=context,
            ai_prompt="Error occurred",
            ai_response=f"Failed: {error_message}",
            confidence_level=AIConfidenceLevel.LEARNING,
            success_metrics={"response_quality": 0.0},
            learning_outcomes=[f"Failed interaction: {error_message}"],
            timestamp=datetime.now().isoformat(),
            execution_time=0.0,
            follow_up_actions=["Investigate AI failure", "Improve error handling"]
        )
        
        self._store_interaction(failure_interaction)
        return failure_interaction
    
    # Helper methods for AI assessment and learning
    def _assess_response_quality(self, response: str) -> float:
        """Assess the quality of the AI response"""
        quality_score = 0.5  # Base score
        
        if len(response) > 500:  quality_score += 0.1
        if '\n' in response:     quality_score += 0.1
        if 'recommendation' in response.lower(): quality_score += 0.1
        if 'analysis' in response.lower(): quality_score += 0.1
        if any(word in response.lower() for word in ['should', 'could', 'would']): quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _assess_context_relevance(self, response: str, context: Dict[str, Any]) -> float:
        """Assess how relevant the response is to the context"""
        relevance_score = 0.5
        
        # Check if response mentions context elements
        for key, value in context.items():
            if str(value).lower() in response.lower():
                relevance_score += 0.1
        
        return min(relevance_score, 1.0)
    
    def _assess_actionability(self, response: str) -> float:
        """Assess how actionable the response is"""
        action_words = ['implement', 'create', 'update', 'modify', 'add', 'remove', 'refactor']
        action_count = sum(1 for word in action_words if word in response.lower())
        return min(action_count * 0.1 + 0.5, 1.0)
    
    def _assess_completeness(self, response: str, task_type: AIInteractionType) -> float:
        """Assess the completeness of the response for the task type"""
        expected_elements = {
            AIInteractionType.CODE_ANALYSIS: ['analysis', 'recommendations', 'issues'],
            AIInteractionType.REFACTORING: ['refactor', 'improve', 'pattern'],
            AIInteractionType.TEST_GENERATION: ['test', 'coverage', 'cases'],
            AIInteractionType.DOCUMENTATION: ['document', 'explain', 'description']
        }
        
        elements = expected_elements.get(task_type, [])
        found_elements = sum(1 for element in elements if element in response.lower())
        
        return found_elements / len(elements) if elements else 0.5
    
    def _assess_innovation(self, response: str) -> float:
        """Assess the innovation level of the response"""
        innovation_indicators = ['novel', 'innovative', 'creative', 'unique', 'advanced', 'cutting-edge']
        innovation_count = sum(1 for indicator in innovation_indicators if indicator in response.lower())
        return min(innovation_count * 0.15 + 0.3, 1.0)
    
    def _get_relevant_memories(self, task_type: AIInteractionType, context: Dict[str, Any]) -> List[AIMemoryFragment]:
        """Get relevant memory fragments for the current task"""
        relevant = []
        
        for fragment in self.memory_fragments:
            if fragment.context_type == task_type.value:
                relevant.append(fragment)
        
        # Sort by confidence and usage
        relevant.sort(key=lambda x: (x.confidence, x.usage_count), reverse=True)
        return relevant[:5]  # Top 5 most relevant
    
    def _format_learned_patterns(self, memories: List[AIMemoryFragment]) -> str:
        """Format learned patterns for prompt inclusion"""
        if not memories:
            return "No relevant patterns learned yet."
        
        patterns = []
        for memory in memories:
            patterns.append(f"- {memory.knowledge} (confidence: {memory.confidence:.1%})")
        
        return '\n'.join(patterns)
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence across all interactions"""
        if not self.interaction_history:
            return 0.0
        
        confidence_values = {'learning': 0.2, 'competent': 0.6, 'expert': 0.8, 'transcendent': 0.95}
        total = sum(confidence_values.get(interaction.get('confidence_level', 'learning'), 0.2) 
                   for interaction in self.interaction_history)
        
        return total / len(self.interaction_history)
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        if not self.interaction_history:
            return 0.0
        
        successful = sum(1 for interaction in self.interaction_history 
                        if interaction.get('success_metrics', {}).get('response_quality', 0) > 0.7)
        
        return successful / len(self.interaction_history)
    
    def _calculate_learning_velocity(self) -> float:
        """Calculate how quickly the AI is learning"""
        if len(self.interaction_history) < 2:
            return 0.0
        
        recent_interactions = self.interaction_history[-10:]  # Last 10 interactions
        confidence_trend = []
        
        confidence_values = {'learning': 0.2, 'competent': 0.6, 'expert': 0.8, 'transcendent': 0.95}
        
        for interaction in recent_interactions:
            confidence = confidence_values.get(interaction.get('confidence_level', 'learning'), 0.2)
            confidence_trend.append(confidence)
        
        if len(confidence_trend) < 2:
            return 0.0
        
        # Calculate slope of confidence over time
        x_values = list(range(len(confidence_trend)))
        y_values = confidence_trend
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return max(slope, 0.0)  # Only positive learning velocity
    
    def _load_ai_memory(self) -> List[AIMemoryFragment]:
        """Load AI memory fragments from storage"""
        if not self.memory_fragments_file.exists():
            return []
        
        try:
            with open(self.memory_fragments_file, 'r') as f:
                data = json.load(f)
                return [AIMemoryFragment(**fragment) for fragment in data]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def _save_ai_memory(self) -> None:
        """Save AI memory fragments to storage"""
        memory_data = [asdict(fragment) for fragment in self.memory_fragments]
        
        with open(self.memory_fragments_file, 'w') as f:
            json.dump(memory_data, f, indent=2, default=str)
    
    def _load_interaction_history(self) -> List[Dict[str, Any]]:
        """Load interaction history from storage"""
        if not self.interactions_file.exists():
            return []
        
        interactions = []
        try:
            with open(self.interactions_file, 'r') as f:
                for line in f:
                    if line.strip():
                        interactions.append(json.loads(line))
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        return interactions
    
    # Additional helper methods for specific assessments
    def _estimate_test_coverage(self, test_response: str) -> float:
        """Estimate test coverage from AI response"""
        test_indicators = ['test', 'assert', 'expect', 'should', 'it(', 'describe(']
        indicator_count = sum(1 for indicator in test_indicators if indicator in test_response.lower())
        return min(indicator_count * 0.1 + 0.6, 1.0)
    
    def _extract_files_to_update(self, doc_response: str) -> List[str]:
        """Extract files that need updating from documentation response"""
        files = []
        lines = doc_response.split('\n')
        
        for line in lines:
            if '.md' in line or '.rst' in line or 'README' in line:
                # Extract potential file names
                words = line.split()
                for word in words:
                    if any(ext in word for ext in ['.md', '.rst', 'README']):
                        files.append(word.strip('`"\''))
        
        return files
    
    def _assess_documentation_quality(self, doc_response: str) -> float:
        """Assess the quality of documentation response"""
        quality_indicators = ['example', 'usage', 'parameter', 'return', 'note', 'warning']
        quality_score = sum(0.1 for indicator in quality_indicators if indicator in doc_response.lower())
        return min(quality_score + 0.4, 1.0)
    
    def _extract_solution_steps(self, debug_response: str) -> List[str]:
        """Extract solution steps from debugging response"""
        steps = []
        lines = debug_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', 'Step', '- ', '* ')):
                steps.append(line)
        
        return steps
    
    def _estimate_optimization_impact(self, optimization_response: str) -> Dict[str, str]:
        """Estimate the impact of optimization suggestions"""
        impact_indicators = {
            'performance': 'high' if 'performance' in optimization_response.lower() else 'low',
            'maintainability': 'high' if 'maintain' in optimization_response.lower() else 'low',
            'scalability': 'high' if 'scale' in optimization_response.lower() else 'low',
            'developer_productivity': 'high' if 'productivity' in optimization_response.lower() else 'low'
        }
        
        return impact_indicators
    
    def _prioritize_optimizations(self, actions: List[str]) -> List[Tuple[str, str]]:
        """Prioritize optimization actions"""
        priorities = []
        
        for action in actions:
            if any(urgent in action.lower() for urgent in ['critical', 'urgent', 'immediate']):
                priority = 'high'
            elif any(important in action.lower() for important in ['important', 'should', 'recommend']):
                priority = 'medium'
            else:
                priority = 'low'
            
            priorities.append((action, priority))
        
        # Sort by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        priorities.sort(key=lambda x: priority_order[x[1]], reverse=True)
        
        return priorities
    
    def _extract_architectural_concerns(self, arch_response: str) -> List[str]:
        """Extract architectural concerns from review response"""
        concerns = []
        concern_indicators = ['concern', 'issue', 'problem', 'risk', 'warning', 'anti-pattern']
        
        lines = arch_response.split('\n')
        for line in lines:
            if any(indicator in line.lower() for indicator in concern_indicators):
                concerns.append(line.strip())
        
        return concerns


def main():
    """CLI interface for the Recursive AI Engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Recursive AI Development Engine")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--test-recursive", action="store_true", help="Test recursive AI capabilities")
    parser.add_argument("--analyze-files", nargs="+", help="Analyze specific files")
    parser.add_argument("--generate-tests", nargs="+", help="Generate tests for files")
    parser.add_argument("--update-docs", action="store_true", help="Update documentation")
    
    args = parser.parse_args()
    
    engine = RecursiveAIEngine(Path(args.project_root))
    
    if args.test_recursive:
        print("🧬 Testing Recursive AI Engine...")
        
        # Test code analysis
        test_context = {"files_changed": ["test.py"], "trigger": "manual"}
        result = engine.autonomous_code_analysis(["test.py"])
        print(f"📊 Analysis result: {result['confidence']}")
        
    elif args.analyze_files:
        result = engine.autonomous_code_analysis(args.analyze_files)
        print(json.dumps(result, indent=2))
        
    elif args.generate_tests:
        result = engine.autonomous_test_generation(args.generate_tests)
        print(json.dumps(result, indent=2))
        
    elif args.update_docs:
        result = engine.autonomous_documentation_update({"trigger": "manual"})
        print(json.dumps(result, indent=2))
        
    else:
        print("Use --test-recursive to test the engine or specify other options")


if __name__ == "__main__":
    main()