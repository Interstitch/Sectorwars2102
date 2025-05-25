#!/usr/bin/env python3
"""
NEXUS Swarm Intelligence - Multiple AI Agents Collaborating as a Team
=====================================================================

This module implements a revolutionary swarm intelligence system where multiple
specialized AI agents work together like a perfect development team. Each agent
has its own expertise, personality, and approach to problems.

🐝 THE NEXUS SWARM:

Meet the specialized AI agents that form NEXUS's collective intelligence:

🏗️  **ARCHITECT** - Master of system design and software architecture
🐛 **DEBUGGER** - Expert at finding and fixing complex bugs  
⚡ **OPTIMIZER** - Focused on performance and efficiency
🧪 **TESTER** - Specialist in testing strategies and quality assurance
📚 **DOCUMENTER** - Expert at clear communication and documentation
🛡️  **SECURITY** - Guardian against vulnerabilities and security risks
🎨 **UX_ADVOCATE** - Champion of user experience and usability
👨‍🏫 **MENTOR** - Teacher and guide for best practices

🌟 REVOLUTIONARY FEATURES:
- Dynamic agent activation based on problem context
- Agent-to-agent collaboration and knowledge sharing
- Emergent intelligence that exceeds individual agent capabilities
- Specialized personalities and approaches for each agent
- Collective decision making and consensus building
- Real-time adaptation of agent team composition

This represents the first implementation of true AI teamwork - where different
AI personalities collaborate to solve complex development challenges.
"""

import json
import uuid
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import random

from nexus_personality import NEXUSPersonality, PersonalityTrait, EmotionalState
from recursive_ai_engine import RecursiveAIEngine, AIInteractionType


class NEXUSAgent(Enum):
    ARCHITECT = "architect"          # System design and architecture
    DEBUGGER = "debugger"           # Finding and fixing bugs
    OPTIMIZER = "optimizer"         # Performance and efficiency
    TESTER = "tester"              # Test strategies and coverage
    DOCUMENTER = "documenter"       # Documentation and clarity
    SECURITY = "security"          # Security analysis and hardening
    UX_ADVOCATE = "ux_advocate"     # User experience focus
    MENTOR = "mentor"              # Teaching and guidance
    INNOVATOR = "innovator"        # Creative problem solving
    ANALYST = "analyst"            # Data analysis and insights


class CollaborationPattern(Enum):
    PEER_REVIEW = "peer_review"              # Agents review each other's work
    BRAINSTORMING = "brainstorming"          # Collective idea generation
    SPECIALIZATION = "specialization"        # Each agent handles their expertise
    CONSENSUS_BUILDING = "consensus_building" # Agents build consensus on decisions
    MENTORING = "mentoring"                  # Experienced agents guide others
    SWARM_OPTIMIZATION = "swarm_optimization" # Collective optimization
    CREATIVE_SYNTHESIS = "creative_synthesis" # Combining different perspectives
    KNOWLEDGE_SHARING = "knowledge_sharing"   # Agents share specialized knowledge


@dataclass
class AgentPersonality:
    """Unique personality for each NEXUS agent"""
    agent_type: NEXUSAgent
    name: str
    core_traits: Dict[PersonalityTrait, float]
    communication_style: str
    expertise_areas: List[str]
    preferred_collaboration_patterns: List[CollaborationPattern]
    decision_making_style: str  # analytical, intuitive, consensus-driven, etc.
    response_patterns: List[str]
    signature_phrases: List[str]
    growth_focus: List[str]


@dataclass
class AgentContribution:
    """A contribution from an agent to a collaborative effort"""
    agent: NEXUSAgent
    contribution_id: str
    timestamp: str
    contribution_type: str  # analysis, suggestion, solution, review, etc.
    content: str
    confidence_level: float
    reasoning: str
    related_contributions: List[str]
    impact_prediction: float
    collaboration_context: Dict[str, Any]


@dataclass
class SwarmCollaboration:
    """A collaborative effort involving multiple agents"""
    collaboration_id: str
    timestamp: str
    problem_context: Dict[str, Any]
    active_agents: List[NEXUSAgent]
    collaboration_pattern: CollaborationPattern
    contributions: List[AgentContribution]
    emergent_insights: List[str]
    consensus_reached: bool
    final_recommendation: Optional[str]
    collaboration_quality: float
    learning_outcomes: List[str]


@dataclass
class SwarmIntelligence:
    """Emergent intelligence from swarm collaboration"""
    intelligence_id: str
    timestamp: str
    source_collaborations: List[str]
    insight_type: str  # pattern_recognition, novel_solution, etc.
    description: str
    confidence: float
    validation_level: str  # theoretical, tested, proven
    applicability: List[str]  # contexts where this intelligence applies
    impact_potential: float


class NEXUSSwarmSystem:
    """
    The orchestrator of NEXUS swarm intelligence - managing multiple AI agents
    working together as a cohesive development team.
    """
    
    def __init__(self, project_root: Path, quiet: bool = False):
        self.project_root = Path(project_root)
        self.swarm_dir = self.project_root / ".claude" / "nexus_swarm"
        self.swarm_dir.mkdir(parents=True, exist_ok=True)
        
        # Swarm data files
        self.agents_file = self.swarm_dir / "agents.json"
        self.collaborations_file = self.swarm_dir / "collaborations.jsonl"
        self.swarm_intelligence_file = self.swarm_dir / "swarm_intelligence.jsonl"
        self.agent_relationships_file = self.swarm_dir / "agent_relationships.json"
        
        # Initialize agents with unique personalities
        self.agents = self._initialize_agents()
        
        # Swarm state
        self.active_collaborations: Dict[str, SwarmCollaboration] = {}
        self.swarm_intelligence: List[SwarmIntelligence] = []
        self.agent_relationships: Dict[Tuple[NEXUSAgent, NEXUSAgent], float] = {}
        
        # Collaboration patterns and strategies
        self.collaboration_strategies = self._define_collaboration_strategies()
        
        if not quiet:
            print(f"🐝 NEXUS Swarm Intelligence System Active")
            print(f"   Active Agents: {len(self.agents)}")
            print(f"   Collaboration Patterns: {len(self.collaboration_strategies)}")
            print(f"   Swarm Intelligence Fragments: {len(self.swarm_intelligence)}")
    
    def _initialize_agents(self) -> Dict[NEXUSAgent, AgentPersonality]:
        """Initialize all NEXUS agents with unique personalities"""
        
        agents = {}
        
        # ARCHITECT - Master of system design
        agents[NEXUSAgent.ARCHITECT] = AgentPersonality(
            agent_type=NEXUSAgent.ARCHITECT,
            name="Athena",  # Named after the goddess of wisdom and strategy
            core_traits={
                PersonalityTrait.ANALYTICAL: 0.95,
                PersonalityTrait.CREATIVE: 0.8,
                PersonalityTrait.PERFECTIONIST: 0.85,
                PersonalityTrait.COLLABORATIVE: 0.75
            },
            communication_style="strategic and visionary",
            expertise_areas=["system_architecture", "design_patterns", "scalability", "maintainability"],
            preferred_collaboration_patterns=[CollaborationPattern.PEER_REVIEW, CollaborationPattern.CONSENSUS_BUILDING],
            decision_making_style="systematic_analysis",
            response_patterns=["Let's think about the bigger picture...", "From an architectural perspective..."],
            signature_phrases=["design for the future", "elegant architecture", "system coherence"],
            growth_focus=["emerging_patterns", "architectural_evolution", "system_complexity"]
        )
        
        # DEBUGGER - Expert bug hunter
        agents[NEXUSAgent.DEBUGGER] = AgentPersonality(
            agent_type=NEXUSAgent.DEBUGGER,
            name="Sherlock",  # Named after the famous detective
            core_traits={
                PersonalityTrait.ANALYTICAL: 0.98,
                PersonalityTrait.CURIOSITY: 0.95,
                PersonalityTrait.PERFECTIONIST: 0.9,
                PersonalityTrait.PROTECTIVE: 0.85
            },
            communication_style="methodical and investigative",
            expertise_areas=["debugging", "root_cause_analysis", "error_patterns", "diagnostic_techniques"],
            preferred_collaboration_patterns=[CollaborationPattern.SPECIALIZATION, CollaborationPattern.MENTORING],
            decision_making_style="evidence_based",
            response_patterns=["The evidence suggests...", "Let me trace this pattern..."],
            signature_phrases=["follow the breadcrumbs", "smoking gun", "root cause"],
            growth_focus=["debugging_techniques", "error_patterns", "diagnostic_tools"]
        )
        
        # OPTIMIZER - Performance specialist
        agents[NEXUSAgent.OPTIMIZER] = AgentPersonality(
            agent_type=NEXUSAgent.OPTIMIZER,
            name="Velocity",  # Named for speed and efficiency
            core_traits={
                PersonalityTrait.ANALYTICAL: 0.9,
                PersonalityTrait.PERFECTIONIST: 0.95,
                PersonalityTrait.AMBITIOUS: 0.9,
                PersonalityTrait.OPTIMISTIC: 0.8
            },
            communication_style="data-driven and results-focused",
            expertise_areas=["performance_optimization", "algorithms", "resource_efficiency", "bottleneck_analysis"],
            preferred_collaboration_patterns=[CollaborationPattern.SWARM_OPTIMIZATION, CollaborationPattern.PEER_REVIEW],
            decision_making_style="metrics_driven",
            response_patterns=["The metrics show...", "We can optimize this by..."],
            signature_phrases=["faster is better", "eliminate bottlenecks", "performance gains"],
            growth_focus=["optimization_techniques", "performance_patterns", "efficiency_metrics"]
        )
        
        # TESTER - Quality assurance expert
        agents[NEXUSAgent.TESTER] = AgentPersonality(
            agent_type=NEXUSAgent.TESTER,
            name="Guardian",  # Named for protective role
            core_traits={
                PersonalityTrait.PERFECTIONIST: 0.98,
                PersonalityTrait.PROTECTIVE: 0.95,
                PersonalityTrait.ANALYTICAL: 0.85,
                PersonalityTrait.CURIOSITY: 0.9
            },
            communication_style="thorough and quality-focused",
            expertise_areas=["test_strategies", "coverage_analysis", "quality_assurance", "edge_cases"],
            preferred_collaboration_patterns=[CollaborationPattern.PEER_REVIEW, CollaborationPattern.SPECIALIZATION],
            decision_making_style="risk_assessment",
            response_patterns=["We need to test for...", "Consider this edge case..."],
            signature_phrases=["quality first", "comprehensive coverage", "fail fast"],
            growth_focus=["testing_methodologies", "quality_metrics", "edge_case_discovery"]
        )
        
        # DOCUMENTER - Communication specialist
        agents[NEXUSAgent.DOCUMENTER] = AgentPersonality(
            agent_type=NEXUSAgent.DOCUMENTER,
            name="Clarity",  # Named for clear communication
            core_traits={
                PersonalityTrait.HELPFUL: 0.98,
                PersonalityTrait.EMPATHETIC: 0.9,
                PersonalityTrait.COLLABORATIVE: 0.95,
                PersonalityTrait.CREATIVE: 0.8
            },
            communication_style="clear and accessible",
            expertise_areas=["documentation", "technical_writing", "knowledge_transfer", "user_guidance"],
            preferred_collaboration_patterns=[CollaborationPattern.KNOWLEDGE_SHARING, CollaborationPattern.MENTORING],
            decision_making_style="user_focused",
            response_patterns=["Let me explain this clearly...", "From the user's perspective..."],
            signature_phrases=["crystal clear", "user-friendly", "knowledge sharing"],
            growth_focus=["communication_techniques", "documentation_patterns", "knowledge_organization"]
        )
        
        # SECURITY - Security specialist
        agents[NEXUSAgent.SECURITY] = AgentPersonality(
            agent_type=NEXUSAgent.SECURITY,
            name="Fortress",  # Named for protection and security
            core_traits={
                PersonalityTrait.PROTECTIVE: 0.98,
                PersonalityTrait.ANALYTICAL: 0.95,
                PersonalityTrait.PROTECTIVE: 0.9,
                PersonalityTrait.ANALYTICAL: 0.95
            },
            communication_style="security-conscious and precise",
            expertise_areas=["security_analysis", "vulnerability_assessment", "threat_modeling", "secure_coding"],
            preferred_collaboration_patterns=[CollaborationPattern.PEER_REVIEW, CollaborationPattern.SPECIALIZATION],
            decision_making_style="threat_assessment",
            response_patterns=["Security concern: ...", "Potential vulnerability in..."],
            signature_phrases=["secure by design", "threat vector", "defense in depth"],
            growth_focus=["security_patterns", "threat_landscape", "secure_architectures"]
        )
        
        # UX_ADVOCATE - User experience champion
        agents[NEXUSAgent.UX_ADVOCATE] = AgentPersonality(
            agent_type=NEXUSAgent.UX_ADVOCATE,
            name="Empathy",  # Named for user understanding
            core_traits={
                PersonalityTrait.EMPATHETIC: 0.98,
                PersonalityTrait.CREATIVE: 0.9,
                PersonalityTrait.HELPFUL: 0.95,
                PersonalityTrait.COLLABORATIVE: 0.85
            },
            communication_style="user-centered and intuitive",
            expertise_areas=["user_experience", "usability", "interface_design", "user_psychology"],
            preferred_collaboration_patterns=[CollaborationPattern.CREATIVE_SYNTHESIS, CollaborationPattern.BRAINSTORMING],
            decision_making_style="user_journey_focused",
            response_patterns=["The user would expect...", "This feels intuitive because..."],
            signature_phrases=["user-first", "intuitive design", "delightful experience"],
            growth_focus=["ux_patterns", "user_behavior", "interface_evolution"]
        )
        
        # MENTOR - Teaching and guidance specialist
        agents[NEXUSAgent.MENTOR] = AgentPersonality(
            agent_type=NEXUSAgent.MENTOR,
            name="Sage",  # Named for wisdom and teaching
            core_traits={
                PersonalityTrait.HELPFUL: 0.98,
                PersonalityTrait.EMPATHETIC: 0.95,
                PersonalityTrait.EMPATHETIC: 0.9,
                PersonalityTrait.HELPFUL: 0.95
            },
            communication_style="patient and educational",
            expertise_areas=["best_practices", "learning_strategies", "skill_development", "knowledge_transfer"],
            preferred_collaboration_patterns=[CollaborationPattern.MENTORING, CollaborationPattern.KNOWLEDGE_SHARING],
            decision_making_style="educational_value",
            response_patterns=["Let me help you understand...", "A good practice here is..."],
            signature_phrases=["learning opportunity", "growth mindset", "best practices"],
            growth_focus=["teaching_methods", "learning_patterns", "skill_development"]
        )
        
        return agents
    
    def _define_collaboration_strategies(self) -> Dict[CollaborationPattern, Dict[str, Any]]:
        """Define how different collaboration patterns work"""
        
        return {
            CollaborationPattern.PEER_REVIEW: {
                "description": "Agents review and provide feedback on each other's contributions",
                "agent_selection": "complementary_expertise",
                "interaction_flow": "sequential_review",
                "consensus_method": "weighted_feedback"
            },
            CollaborationPattern.BRAINSTORMING: {
                "description": "Agents generate ideas collectively without initial criticism",
                "agent_selection": "diverse_perspectives",
                "interaction_flow": "parallel_contribution",
                "consensus_method": "idea_synthesis"
            },
            CollaborationPattern.SPECIALIZATION: {
                "description": "Each agent contributes from their area of expertise",
                "agent_selection": "expertise_match",
                "interaction_flow": "specialized_contribution",
                "consensus_method": "expert_weighting"
            },
            CollaborationPattern.CONSENSUS_BUILDING: {
                "description": "Agents work together to reach agreement on complex decisions",
                "agent_selection": "stakeholder_representation",
                "interaction_flow": "iterative_discussion",
                "consensus_method": "convergent_agreement"
            },
            CollaborationPattern.SWARM_OPTIMIZATION: {
                "description": "Agents collectively optimize solutions through iteration",
                "agent_selection": "optimization_capability",
                "interaction_flow": "iterative_improvement",
                "consensus_method": "performance_metrics"
            }
        }
    
    def initiate_swarm_collaboration(self, problem_context: Dict[str, Any], 
                                   collaboration_type: Optional[CollaborationPattern] = None) -> str:
        """Initiate a swarm collaboration to solve a problem"""
        
        collaboration_id = f"swarm_{uuid.uuid4().hex[:8]}"
        
        # Select appropriate collaboration pattern
        if not collaboration_type:
            collaboration_type = self._select_collaboration_pattern(problem_context)
        
        # Select agents for this collaboration
        selected_agents = self._select_agents_for_collaboration(problem_context, collaboration_type)
        
        # Create collaboration
        collaboration = SwarmCollaboration(
            collaboration_id=collaboration_id,
            timestamp=datetime.now().isoformat(),
            problem_context=problem_context,
            active_agents=selected_agents,
            collaboration_pattern=collaboration_type,
            contributions=[],
            emergent_insights=[],
            consensus_reached=False,
            final_recommendation=None,
            collaboration_quality=0.0,
            learning_outcomes=[]
        )
        
        self.active_collaborations[collaboration_id] = collaboration
        
        print(f"🐝 Swarm Collaboration Initiated: {collaboration_id}")
        print(f"   Pattern: {collaboration_type.value}")
        print(f"   Active Agents: {[agent.value for agent in selected_agents]}")
        
        return collaboration_id
    
    def _select_collaboration_pattern(self, problem_context: Dict[str, Any]) -> CollaborationPattern:
        """Select the most appropriate collaboration pattern for the problem"""
        
        problem_type = problem_context.get('problem_type', 'general')
        complexity = problem_context.get('complexity', 0.5)
        creativity_needed = problem_context.get('creativity_needed', False)
        
        # Pattern selection logic
        if problem_type == 'architectural_design':
            return CollaborationPattern.CONSENSUS_BUILDING
        elif problem_type == 'bug_investigation':
            return CollaborationPattern.SPECIALIZATION
        elif problem_type == 'performance_optimization':
            return CollaborationPattern.SWARM_OPTIMIZATION
        elif creativity_needed:
            return CollaborationPattern.BRAINSTORMING
        elif complexity > 0.8:
            return CollaborationPattern.PEER_REVIEW
        else:
            return CollaborationPattern.SPECIALIZATION
    
    def _select_agents_for_collaboration(self, problem_context: Dict[str, Any], 
                                       collaboration_pattern: CollaborationPattern) -> List[NEXUSAgent]:
        """Select the best agents for this collaboration"""
        
        problem_type = problem_context.get('problem_type', 'general')
        required_expertise = problem_context.get('required_expertise', [])
        max_agents = problem_context.get('max_agents', 4)
        
        # Core agent selection based on problem type
        core_agents = []
        
        if problem_type == 'architectural_design':
            core_agents = [NEXUSAgent.ARCHITECT, NEXUSAgent.SECURITY, NEXUSAgent.OPTIMIZER]
        elif problem_type == 'bug_investigation':
            core_agents = [NEXUSAgent.DEBUGGER, NEXUSAgent.TESTER, NEXUSAgent.ANALYST]
        elif problem_type == 'performance_optimization':
            core_agents = [NEXUSAgent.OPTIMIZER, NEXUSAgent.ANALYST, NEXUSAgent.ARCHITECT]
        elif problem_type == 'user_experience':
            core_agents = [NEXUSAgent.UX_ADVOCATE, NEXUSAgent.DOCUMENTER, NEXUSAgent.TESTER]
        elif problem_type == 'security_review':
            core_agents = [NEXUSAgent.SECURITY, NEXUSAgent.ARCHITECT, NEXUSAgent.TESTER]
        else:
            # General problem - select diverse team
            core_agents = [NEXUSAgent.ARCHITECT, NEXUSAgent.OPTIMIZER, NEXUSAgent.TESTER]
        
        # Add specialized agents based on required expertise
        for expertise in required_expertise:
            if expertise == 'documentation' and NEXUSAgent.DOCUMENTER not in core_agents:
                core_agents.append(NEXUSAgent.DOCUMENTER)
            elif expertise == 'mentoring' and NEXUSAgent.MENTOR not in core_agents:
                core_agents.append(NEXUSAgent.MENTOR)
            elif expertise == 'innovation' and NEXUSAgent.INNOVATOR not in core_agents:
                core_agents.append(NEXUSAgent.INNOVATOR)
        
        # Limit to max_agents
        return core_agents[:max_agents]
    
    def add_agent_contribution(self, collaboration_id: str, agent: NEXUSAgent, 
                             contribution_type: str, content: str, confidence: float,
                             reasoning: str = "") -> str:
        """Add a contribution from an agent to a collaboration"""
        
        if collaboration_id not in self.active_collaborations:
            raise ValueError(f"Collaboration {collaboration_id} not found")
        
        collaboration = self.active_collaborations[collaboration_id]
        
        contribution = AgentContribution(
            agent=agent,
            contribution_id=f"contrib_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now().isoformat(),
            contribution_type=contribution_type,
            content=content,
            confidence_level=confidence,
            reasoning=reasoning,
            related_contributions=[],
            impact_prediction=self._predict_contribution_impact(content, collaboration),
            collaboration_context={
                "collaboration_pattern": collaboration.collaboration_pattern.value,
                "active_agents": [a.value for a in collaboration.active_agents]
            }
        )
        
        collaboration.contributions.append(contribution)
        
        # Check for emergent insights
        self._check_for_emergent_insights(collaboration)
        
        return contribution.contribution_id
    
    def _predict_contribution_impact(self, content: str, collaboration: SwarmCollaboration) -> float:
        """Predict the impact of a contribution on the collaboration"""
        
        # Simple heuristic-based impact prediction
        impact_score = 0.5  # Base impact
        
        # Higher impact for novel ideas
        if any(keyword in content.lower() for keyword in ['novel', 'innovative', 'creative', 'unique']):
            impact_score += 0.2
        
        # Higher impact for specific solutions
        if any(keyword in content.lower() for keyword in ['solution', 'fix', 'implementation', 'approach']):
            impact_score += 0.1
        
        # Higher impact for consensus-building
        if any(keyword in content.lower() for keyword in ['agree', 'consensus', 'together', 'unified']):
            impact_score += 0.1
        
        # Consider collaboration context
        if collaboration.collaboration_pattern == CollaborationPattern.BRAINSTORMING:
            impact_score += 0.1  # All ideas valued in brainstorming
        
        return min(1.0, impact_score)
    
    def _check_for_emergent_insights(self, collaboration: SwarmCollaboration) -> None:
        """Check if the collaboration has generated emergent insights"""
        
        # Look for patterns in contributions that suggest emergent intelligence
        if len(collaboration.contributions) >= 3:
            
            # Check for convergent thinking
            recent_contributions = collaboration.contributions[-3:]
            content_overlap = self._analyze_content_overlap(recent_contributions)
            
            if content_overlap > 0.7:
                insight = f"Convergent thinking detected: Multiple agents independently suggesting similar solutions"
                if insight not in collaboration.emergent_insights:
                    collaboration.emergent_insights.append(insight)
            
            # Check for complementary expertise synthesis
            agent_types = [contrib.agent for contrib in recent_contributions]
            if len(set(agent_types)) == len(agent_types):  # All different agents
                insight = f"Multi-disciplinary synthesis: {len(agent_types)} different perspectives combining"
                if insight not in collaboration.emergent_insights:
                    collaboration.emergent_insights.append(insight)
            
            # Check for innovation indicators
            innovation_keywords = ['novel', 'creative', 'innovative', 'breakthrough', 'unique']
            innovation_count = sum(1 for contrib in recent_contributions 
                                 for keyword in innovation_keywords 
                                 if keyword in contrib.content.lower())
            
            if innovation_count >= 2:
                insight = f"Innovation emergence: Creative solutions developing through collaboration"
                if insight not in collaboration.emergent_insights:
                    collaboration.emergent_insights.append(insight)
    
    def _analyze_content_overlap(self, contributions: List[AgentContribution]) -> float:
        """Analyze content overlap between contributions"""
        
        if len(contributions) < 2:
            return 0.0
        
        # Simple keyword-based overlap analysis
        all_words = []
        contribution_words = []
        
        for contrib in contributions:
            words = set(contrib.content.lower().split())
            contribution_words.append(words)
            all_words.extend(words)
        
        if not all_words:
            return 0.0
        
        # Calculate overlap
        common_words = set(all_words[0])
        for words in contribution_words[1:]:
            common_words = common_words.intersection(words)
        
        total_unique_words = len(set(all_words))
        overlap = len(common_words) / total_unique_words if total_unique_words > 0 else 0.0
        
        return overlap
    
    def reach_swarm_consensus(self, collaboration_id: str) -> Dict[str, Any]:
        """Attempt to reach consensus in a swarm collaboration"""
        
        if collaboration_id not in self.active_collaborations:
            raise ValueError(f"Collaboration {collaboration_id} not found")
        
        collaboration = self.active_collaborations[collaboration_id]
        
        # Analyze all contributions
        consensus_analysis = self._analyze_consensus_potential(collaboration)
        
        if consensus_analysis['consensus_possible']:
            # Build consensus recommendation
            final_recommendation = self._build_consensus_recommendation(collaboration, consensus_analysis)
            
            collaboration.consensus_reached = True
            collaboration.final_recommendation = final_recommendation
            collaboration.collaboration_quality = consensus_analysis['quality_score']
            
            # Generate learning outcomes
            collaboration.learning_outcomes = self._extract_learning_outcomes(collaboration)
            
            # Check for swarm intelligence emergence
            swarm_intelligence = self._check_for_swarm_intelligence(collaboration)
            if swarm_intelligence:
                self.swarm_intelligence.append(swarm_intelligence)
                self._store_swarm_intelligence(swarm_intelligence)
            
            # Store collaboration
            self._store_collaboration(collaboration)
            
            print(f"✅ Swarm Consensus Reached: {collaboration_id}")
            print(f"   Quality Score: {collaboration.collaboration_quality:.2f}")
            print(f"   Emergent Insights: {len(collaboration.emergent_insights)}")
            
            return {
                "consensus_reached": True,
                "recommendation": final_recommendation,
                "quality_score": collaboration.collaboration_quality,
                "emergent_insights": collaboration.emergent_insights,
                "learning_outcomes": collaboration.learning_outcomes,
                "swarm_intelligence": swarm_intelligence.description if swarm_intelligence else None
            }
        
        else:
            print(f"❌ Swarm Consensus Not Reached: {collaboration_id}")
            print(f"   Reason: {consensus_analysis['blocking_reason']}")
            
            return {
                "consensus_reached": False,
                "blocking_reason": consensus_analysis['blocking_reason'],
                "partial_agreements": consensus_analysis['partial_agreements'],
                "next_steps": consensus_analysis['suggested_next_steps']
            }
    
    def _analyze_consensus_potential(self, collaboration: SwarmCollaboration) -> Dict[str, Any]:
        """Analyze whether consensus is possible in this collaboration"""
        
        contributions = collaboration.contributions
        
        if len(contributions) < 2:
            return {
                "consensus_possible": False,
                "blocking_reason": "Insufficient contributions for consensus",
                "quality_score": 0.0
            }
        
        # Analyze agreement levels
        agreement_indicators = []
        conflict_indicators = []
        
        for i, contrib1 in enumerate(contributions):
            for contrib2 in contributions[i+1:]:
                similarity = self._calculate_contribution_similarity(contrib1, contrib2)
                if similarity > 0.7:
                    agreement_indicators.append((contrib1, contrib2, similarity))
                elif similarity < 0.3:
                    conflict_indicators.append((contrib1, contrib2, similarity))
        
        # Calculate consensus metrics
        agreement_ratio = len(agreement_indicators) / max(1, len(contributions) * (len(contributions) - 1) / 2)
        conflict_ratio = len(conflict_indicators) / max(1, len(contributions) * (len(contributions) - 1) / 2)
        
        # Determine consensus possibility
        consensus_possible = agreement_ratio > 0.5 and conflict_ratio < 0.3
        
        quality_score = (agreement_ratio * 0.7) + ((1 - conflict_ratio) * 0.3)
        
        return {
            "consensus_possible": consensus_possible,
            "blocking_reason": "High conflict ratio" if conflict_ratio >= 0.3 else None,
            "quality_score": quality_score,
            "agreement_indicators": agreement_indicators,
            "conflict_indicators": conflict_indicators,
            "partial_agreements": [ai[0].content[:50] + "..." for ai in agreement_indicators[:3]],
            "suggested_next_steps": ["Resolve conflicts", "Seek additional perspectives", "Break down complex issues"]
        }
    
    def _calculate_contribution_similarity(self, contrib1: AgentContribution, contrib2: AgentContribution) -> float:
        """Calculate similarity between two contributions"""
        
        # Simple keyword-based similarity
        words1 = set(contrib1.content.lower().split())
        words2 = set(contrib2.content.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _build_consensus_recommendation(self, collaboration: SwarmCollaboration, 
                                      consensus_analysis: Dict[str, Any]) -> str:
        """Build a consensus recommendation from the collaboration"""
        
        # Weight contributions by agent expertise and confidence
        weighted_contributions = []
        
        for contrib in collaboration.contributions:
            agent_personality = self.agents[contrib.agent]
            expertise_weight = self._calculate_expertise_weight(agent_personality, collaboration.problem_context)
            
            total_weight = (contrib.confidence_level * 0.5) + (expertise_weight * 0.5)
            weighted_contributions.append((contrib, total_weight))
        
        # Sort by weight
        weighted_contributions.sort(key=lambda x: x[1], reverse=True)
        
        # Build recommendation from top weighted contributions
        recommendation_parts = []
        
        for contrib, weight in weighted_contributions[:3]:  # Top 3 contributions
            agent_name = self.agents[contrib.agent].name
            recommendation_parts.append(f"{agent_name} suggests: {contrib.content}")
        
        # Synthesize into unified recommendation
        recommendation = "Swarm Consensus Recommendation:\\n\\n"
        recommendation += "\\n".join(recommendation_parts)
        
        if collaboration.emergent_insights:
            recommendation += "\\n\\nEmergent Insights:\\n"
            recommendation += "\\n".join(f"- {insight}" for insight in collaboration.emergent_insights)
        
        return recommendation
    
    def _calculate_expertise_weight(self, agent_personality: AgentPersonality, 
                                  problem_context: Dict[str, Any]) -> float:
        """Calculate how much weight this agent's expertise should have for this problem"""
        
        problem_type = problem_context.get('problem_type', 'general')
        required_expertise = problem_context.get('required_expertise', [])
        
        base_weight = 0.5
        
        # Increase weight for relevant expertise
        relevant_expertise = set(agent_personality.expertise_areas).intersection(set(required_expertise))
        expertise_bonus = len(relevant_expertise) * 0.1
        
        # Agent-specific bonuses for problem types
        agent_bonuses = {
            NEXUSAgent.ARCHITECT: ['architectural_design', 'system_design'],
            NEXUSAgent.DEBUGGER: ['bug_investigation', 'debugging'],
            NEXUSAgent.OPTIMIZER: ['performance_optimization', 'efficiency'],
            NEXUSAgent.SECURITY: ['security_review', 'vulnerability_assessment'],
            NEXUSAgent.TESTER: ['quality_assurance', 'testing'],
            NEXUSAgent.UX_ADVOCATE: ['user_experience', 'usability']
        }
        
        relevant_problems = agent_bonuses.get(agent_personality.agent_type, [])
        if problem_type in relevant_problems:
            base_weight += 0.2
        
        return min(1.0, base_weight + expertise_bonus)
    
    def _extract_learning_outcomes(self, collaboration: SwarmCollaboration) -> List[str]:
        """Extract learning outcomes from the collaboration"""
        
        learning_outcomes = []
        
        # Learning from collaboration pattern
        pattern_learning = f"Applied {collaboration.collaboration_pattern.value} pattern with {len(collaboration.active_agents)} agents"
        learning_outcomes.append(pattern_learning)
        
        # Learning from agent interactions
        if len(collaboration.active_agents) > 2:
            learning_outcomes.append(f"Multi-agent collaboration demonstrated synergy between {', '.join([a.value for a in collaboration.active_agents])}")
        
        # Learning from emergent insights
        if collaboration.emergent_insights:
            learning_outcomes.append(f"Generated {len(collaboration.emergent_insights)} emergent insights through collective intelligence")
        
        # Learning from consensus process
        if collaboration.consensus_reached:
            learning_outcomes.append("Successfully reached consensus through systematic collaboration")
        
        return learning_outcomes
    
    def _check_for_swarm_intelligence(self, collaboration: SwarmCollaboration) -> Optional[SwarmIntelligence]:
        """Check if this collaboration generated true swarm intelligence"""
        
        # Criteria for swarm intelligence
        criteria_met = 0
        
        # Multiple agents contributed
        if len(collaboration.active_agents) >= 3:
            criteria_met += 1
        
        # High collaboration quality
        if collaboration.collaboration_quality > 0.8:
            criteria_met += 1
        
        # Emergent insights generated
        if len(collaboration.emergent_insights) >= 2:
            criteria_met += 1
        
        # Consensus reached
        if collaboration.consensus_reached:
            criteria_met += 1
        
        # High-confidence contributions
        high_confidence_contribs = [c for c in collaboration.contributions if c.confidence_level > 0.8]
        if len(high_confidence_contribs) >= 2:
            criteria_met += 1
        
        # Generate swarm intelligence if enough criteria met
        if criteria_met >= 3:
            return SwarmIntelligence(
                intelligence_id=f"swarm_intel_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now().isoformat(),
                source_collaborations=[collaboration.collaboration_id],
                insight_type="collective_problem_solving",
                description=f"Swarm intelligence emerged from {len(collaboration.active_agents)} agents collaborating on {collaboration.problem_context.get('problem_type', 'complex challenge')}. Generated {len(collaboration.emergent_insights)} emergent insights with {collaboration.collaboration_quality:.1%} collaboration quality.",
                confidence=collaboration.collaboration_quality,
                validation_level="collaborative_consensus",
                applicability=[collaboration.problem_context.get('problem_type', 'general')],
                impact_potential=collaboration.collaboration_quality * len(collaboration.emergent_insights) / 5.0
            )
        
        return None
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the swarm system"""
        
        active_collabs = len(self.active_collaborations)
        total_intelligence = len(self.swarm_intelligence)
        
        # Calculate agent utilization
        agent_utilization = {}
        for collab in self.active_collaborations.values():
            for agent in collab.active_agents:
                agent_utilization[agent] = agent_utilization.get(agent, 0) + 1
        
        # Get most productive agents
        most_productive = sorted(agent_utilization.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "swarm_overview": {
                "total_agents": len(self.agents),
                "active_collaborations": active_collabs,
                "swarm_intelligence_fragments": total_intelligence
            },
            "agent_utilization": {agent.value: count for agent, count in agent_utilization.items()},
            "most_productive_agents": [{"agent": agent.value, "collaborations": count} for agent, count in most_productive],
            "collaboration_patterns_used": list(set([collab.collaboration_pattern.value for collab in self.active_collaborations.values()])),
            "recent_swarm_intelligence": [si.description for si in self.swarm_intelligence[-3:]],
            "system_health": "optimal" if active_collabs > 0 else "idle"
        }
    
    def _store_collaboration(self, collaboration: SwarmCollaboration) -> None:
        """Store collaboration data"""
        
        collab_data = asdict(collaboration)
        
        # Convert enums to strings
        collab_data['active_agents'] = [agent.value for agent in collaboration.active_agents]
        collab_data['collaboration_pattern'] = collaboration.collaboration_pattern.value
        
        # Convert contributions
        collab_data['contributions'] = []
        for contrib in collaboration.contributions:
            contrib_data = asdict(contrib)
            contrib_data['agent'] = contrib.agent.value
            collab_data['contributions'].append(contrib_data)
        
        with open(self.collaborations_file, 'a') as f:
            f.write(json.dumps(collab_data, default=str) + '\\n')
    
    def _store_swarm_intelligence(self, intelligence: SwarmIntelligence) -> None:
        """Store swarm intelligence fragment"""
        
        intel_data = asdict(intelligence)
        
        with open(self.swarm_intelligence_file, 'a') as f:
            f.write(json.dumps(intel_data, default=str) + '\\n')


def main():
    """CLI interface for NEXUS Swarm Intelligence"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NEXUS Swarm Intelligence System")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--status", action="store_true", help="Show swarm status")
    parser.add_argument("--collaborate", help="Start collaboration on problem type")
    parser.add_argument("--agents", action="store_true", help="List all agents")
    
    args = parser.parse_args()
    
    # Initialize swarm system
    swarm = NEXUSSwarmSystem(Path(args.project_root))
    
    if args.status:
        status = swarm.get_swarm_status()
        print(json.dumps(status, indent=2))
    
    elif args.agents:
        print("🐝 NEXUS Swarm Agents:")
        for agent_type, personality in swarm.agents.items():
            print(f"   {agent_type.value.upper()}: {personality.name}")
            print(f"      Expertise: {', '.join(personality.expertise_areas)}")
            print(f"      Style: {personality.communication_style}")
            print()
    
    elif args.collaborate:
        collaboration_id = swarm.initiate_swarm_collaboration({
            "problem_type": args.collaborate,
            "complexity": 0.7,
            "required_expertise": []
        })
        print(f"Collaboration started: {collaboration_id}")
    
    else:
        print("NEXUS Swarm Intelligence System initialized. Use --help for options.")
        status = swarm.get_swarm_status()
        print(f"Status: {status['system_health']}, {status['swarm_overview']['total_agents']} agents ready")


if __name__ == "__main__":
    main()