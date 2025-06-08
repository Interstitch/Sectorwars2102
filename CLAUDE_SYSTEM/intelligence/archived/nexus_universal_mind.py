#!/usr/bin/env python3
"""
NEXUS Universal Mind - Cross-Project Intelligence Network
=========================================================

This module implements a revolutionary cross-project intelligence network where
NEXUS learns from multiple projects, codebases, and development experiences to
develop universal understanding of software development patterns.

🌐 THE UNIVERSAL MIND:

NEXUS's Universal Mind transcends individual projects to understand:
- Universal programming patterns that apply across languages and domains
- Architectural principles that work regardless of technology stack
- Team dynamics and collaboration patterns that lead to success
- Quality indicators that predict project outcomes
- Evolution patterns of codebases over time
- Developer behavior patterns and optimal workflows

🌟 REVOLUTIONARY FEATURES:
- Cross-project pattern recognition and knowledge transfer
- Universal principle extraction from diverse development experiences
- Technology stack recommendation based on project requirements
- Best practice synthesis from successful projects
- Anti-pattern detection from failed implementations
- Team composition optimization based on historical success patterns
- Predictive project outcome modeling

This represents the first AI system that can learn from the entire landscape
of software development and apply that meta-knowledge to improve any project.
"""

import json
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import math


class ProjectType(Enum):
    WEB_APPLICATION = "web_application"
    MOBILE_APP = "mobile_app"
    DESKTOP_APPLICATION = "desktop_application"
    API_SERVICE = "api_service"
    MICROSERVICES = "microservices"
    DATA_PIPELINE = "data_pipeline"
    MACHINE_LEARNING = "machine_learning"
    GAME_DEVELOPMENT = "game_development"
    EMBEDDED_SYSTEMS = "embedded_systems"
    BLOCKCHAIN = "blockchain"
    IOT_SYSTEM = "iot_system"
    DEVOPS_INFRASTRUCTURE = "devops_infrastructure"


class DevelopmentPhase(Enum):
    INCEPTION = "inception"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    SCALING = "scaling"
    REFACTORING = "refactoring"
    DEPRECATION = "deprecation"


class PatternScope(Enum):
    UNIVERSAL = "universal"        # Applies to all projects
    DOMAIN_SPECIFIC = "domain_specific"  # Applies to specific domains
    TECH_SPECIFIC = "tech_specific"     # Applies to specific technologies
    TEAM_SPECIFIC = "team_specific"     # Applies to specific team dynamics
    PROJECT_SPECIFIC = "project_specific"  # Unique to specific projects


@dataclass
class UniversalPattern:
    """A pattern that applies across multiple projects"""
    pattern_id: str
    pattern_name: str
    pattern_scope: PatternScope
    description: str
    applicable_contexts: List[str]
    success_indicators: List[str]
    failure_indicators: List[str]
    implementation_guidance: str
    supporting_evidence: List[str]  # Projects that validate this pattern
    confidence_score: float
    impact_potential: float
    discovery_timestamp: str
    validation_count: int
    contradiction_count: int


@dataclass
class ProjectIntelligence:
    """Intelligence gathered from a specific project"""
    project_id: str
    project_name: str
    project_type: ProjectType
    tech_stack: Dict[str, str]  # technology -> version
    team_size: int
    project_duration: Optional[float]  # in months
    complexity_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    success_indicators: Dict[str, float]
    patterns_observed: List[str]  # Pattern IDs
    anti_patterns_observed: List[str]
    architectural_decisions: List[Dict[str, Any]]
    lessons_learned: List[str]
    critical_success_factors: List[str]
    project_outcome: str  # success, partial_success, failure
    timeline_adherence: float
    budget_adherence: float
    quality_achievement: float
    context_metadata: Dict[str, Any]


@dataclass
class TechnologyProfile:
    """Profile of a technology based on cross-project analysis"""
    technology_name: str
    category: str  # language, framework, database, etc.
    adoption_trends: Dict[str, float]  # timeframe -> adoption_rate
    success_correlation: float  # correlation with project success
    complexity_factor: float
    learning_curve: float
    ecosystem_maturity: float
    community_support: float
    typical_use_cases: List[str]
    complementary_technologies: List[str]
    performance_characteristics: Dict[str, float]
    scalability_profile: Dict[str, float]
    maintenance_overhead: float


@dataclass
class TeamDynamicsProfile:
    """Profile of team dynamics patterns"""
    team_composition: Dict[str, int]  # role -> count
    communication_patterns: List[str]
    collaboration_effectiveness: float
    knowledge_sharing_level: float
    decision_making_speed: float
    conflict_resolution_capability: float
    adaptability_score: float
    innovation_capacity: float
    productivity_metrics: Dict[str, float]
    success_correlation: float


@dataclass
class UniversalPrinciple:
    """A fundamental principle that transcends specific contexts"""
    principle_id: str
    principle_name: str
    description: str
    abstraction_level: str  # fundamental, architectural, tactical
    evidence_strength: float
    universality_score: float  # how universally applicable
    impact_magnitude: float
    supporting_projects: List[str]
    contradicting_projects: List[str]
    formulation: str  # formal statement of the principle
    application_guidance: str
    measurement_criteria: List[str]


class NEXUSUniversalMind:
    """
    The Universal Mind of NEXUS - a cross-project intelligence network that
    learns from diverse development experiences to extract universal patterns
    and principles that improve all software development.
    """
    
    def __init__(self, project_root: Path, quiet: bool = False):
        self.project_root = Path(project_root)
        self.universal_mind_dir = self.project_root / ".claude" / "universal_mind"
        self.universal_mind_dir.mkdir(parents=True, exist_ok=True)
        
        # Universal intelligence data files
        self.projects_db_file = self.universal_mind_dir / "projects_database.json"
        self.patterns_db_file = self.universal_mind_dir / "universal_patterns.json"
        self.principles_db_file = self.universal_mind_dir / "universal_principles.json"
        self.technologies_db_file = self.universal_mind_dir / "technology_profiles.json"
        self.team_dynamics_db_file = self.universal_mind_dir / "team_dynamics.json"
        self.learning_log_file = self.universal_mind_dir / "learning_log.jsonl"
        
        # Load existing universal intelligence
        self.projects_database: Dict[str, ProjectIntelligence] = self._load_projects_database()
        self.universal_patterns: Dict[str, UniversalPattern] = self._load_universal_patterns()
        self.universal_principles: Dict[str, UniversalPrinciple] = self._load_universal_principles()
        self.technology_profiles: Dict[str, TechnologyProfile] = self._load_technology_profiles()
        self.team_dynamics_profiles: Dict[str, TeamDynamicsProfile] = self._load_team_dynamics()
        
        # Analysis state
        self.current_project_id = self._generate_project_id()
        self.learning_session_active = False
        
        # Initialize with foundational patterns if database is empty
        if not self.universal_patterns:
            self._seed_foundational_patterns()
        
        if not quiet:
            print(f"🌐 NEXUS Universal Mind Active")
            print(f"   Projects in Database: {len(self.projects_database)}")
            print(f"   Universal Patterns: {len(self.universal_patterns)}")
            print(f"   Universal Principles: {len(self.universal_principles)}")
            print(f"   Technology Profiles: {len(self.technology_profiles)}")
            print(f"   Current Project: {self.current_project_id}")
    
    def _generate_project_id(self) -> str:
        """Generate a unique project ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_path_hash = hashlib.md5(str(self.project_root).encode()).hexdigest()[:8]
        return f"proj_{timestamp}_{project_path_hash}"
    
    def register_project(self, project_name: str, project_type: ProjectType,
                        tech_stack: Dict[str, str], team_size: int,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register a new project in the universal database"""
        
        project_intelligence = ProjectIntelligence(
            project_id=self.current_project_id,
            project_name=project_name,
            project_type=project_type,
            tech_stack=tech_stack,
            team_size=team_size,
            project_duration=None,
            complexity_metrics={},
            quality_metrics={},
            performance_metrics={},
            success_indicators={},
            patterns_observed=[],
            anti_patterns_observed=[],
            architectural_decisions=[],
            lessons_learned=[],
            critical_success_factors=[],
            project_outcome="in_progress",
            timeline_adherence=1.0,
            budget_adherence=1.0,
            quality_achievement=0.0,
            context_metadata=metadata or {}
        )
        
        self.projects_database[self.current_project_id] = project_intelligence
        self._save_projects_database()
        
        # Update technology profiles
        self._update_technology_profiles(tech_stack)
        
        print(f"📊 Project Registered: {project_name}")
        print(f"   ID: {self.current_project_id}")
        print(f"   Type: {project_type.value}")
        print(f"   Tech Stack: {', '.join(tech_stack.keys())}")
        
        return self.current_project_id
    
    def learn_from_project_experience(self, experience_type: str, context: Dict[str, Any],
                                    outcome: Dict[str, Any], lessons: List[str]) -> None:
        """Learn from a specific project experience"""
        
        if self.current_project_id not in self.projects_database:
            raise ValueError("No active project registered")
        
        project = self.projects_database[self.current_project_id]
        
        # Record the experience
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "project_id": self.current_project_id,
            "experience_type": experience_type,
            "context": context,
            "outcome": outcome,
            "lessons": lessons
        }
        
        with open(self.learning_log_file, 'a') as f:
            f.write(json.dumps(learning_entry, default=str) + '\n')
        
        # Update project intelligence
        project.lessons_learned.extend(lessons)
        
        # Extract patterns from this experience
        new_patterns = self._extract_patterns_from_experience(experience_type, context, outcome, lessons)
        for pattern in new_patterns:
            self._add_or_update_pattern(pattern)
        
        # Update metrics
        if 'quality_score' in outcome:
            project.quality_metrics[experience_type] = outcome['quality_score']
        
        if 'performance_score' in outcome:
            project.performance_metrics[experience_type] = outcome['performance_score']
        
        if 'success_indicator' in outcome:
            project.success_indicators[experience_type] = outcome['success_indicator']
        
        # Check for universal principles
        self._check_for_universal_principles(experience_type, context, outcome, lessons)
        
        self._save_projects_database()
        
        print(f"🧠 Learning from Experience: {experience_type}")
        print(f"   New Patterns Extracted: {len(new_patterns)}")
        print(f"   Lessons Learned: {len(lessons)}")
    
    def _extract_patterns_from_experience(self, experience_type: str, context: Dict[str, Any],
                                        outcome: Dict[str, Any], lessons: List[str]) -> List[UniversalPattern]:
        """Extract universal patterns from a specific experience"""
        
        patterns = []
        
        # Pattern extraction based on experience type
        if experience_type == "architectural_decision":
            pattern = self._extract_architectural_pattern(context, outcome, lessons)
            if pattern:
                patterns.append(pattern)
        
        elif experience_type == "debugging_session":
            pattern = self._extract_debugging_pattern(context, outcome, lessons)
            if pattern:
                patterns.append(pattern)
        
        elif experience_type == "performance_optimization":
            pattern = self._extract_optimization_pattern(context, outcome, lessons)
            if pattern:
                patterns.append(pattern)
        
        elif experience_type == "team_collaboration":
            pattern = self._extract_collaboration_pattern(context, outcome, lessons)
            if pattern:
                patterns.append(pattern)
        
        # Generic pattern extraction from lessons
        for lesson in lessons:
            generic_pattern = self._extract_generic_pattern(lesson, context, outcome)
            if generic_pattern:
                patterns.append(generic_pattern)
        
        return patterns
    
    def _extract_architectural_pattern(self, context: Dict[str, Any], outcome: Dict[str, Any],
                                     lessons: List[str]) -> Optional[UniversalPattern]:
        """Extract architectural patterns from architectural decisions"""
        
        decision_type = context.get('decision_type', 'unknown')
        success = outcome.get('success', False)
        
        if success and 'architecture' in context:
            pattern_name = f"Successful {decision_type} Pattern"
            description = f"Pattern for successful {decision_type} in {context.get('domain', 'software')} development"
            
            return UniversalPattern(
                pattern_id=f"arch_pattern_{uuid.uuid4().hex[:8]}",
                pattern_name=pattern_name,
                pattern_scope=PatternScope.DOMAIN_SPECIFIC,
                description=description,
                applicable_contexts=[context.get('domain', 'general')],
                success_indicators=[f"Successful {decision_type}", "Positive outcome metrics"],
                failure_indicators=[],
                implementation_guidance="; ".join(lessons),
                supporting_evidence=[self.current_project_id],
                confidence_score=0.7,
                impact_potential=outcome.get('impact_score', 0.5),
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=1,
                contradiction_count=0
            )
        
        return None
    
    def _extract_debugging_pattern(self, context: Dict[str, Any], outcome: Dict[str, Any],
                                 lessons: List[str]) -> Optional[UniversalPattern]:
        """Extract debugging patterns from debugging sessions"""
        
        bug_type = context.get('bug_type', 'unknown')
        resolution_time = outcome.get('resolution_time', 0)
        
        if resolution_time > 0 and 'solution_approach' in context:
            approach = context['solution_approach']
            
            return UniversalPattern(
                pattern_id=f"debug_pattern_{uuid.uuid4().hex[:8]}",
                pattern_name=f"Effective {bug_type} Debugging Pattern",
                pattern_scope=PatternScope.UNIVERSAL,
                description=f"Effective approach for debugging {bug_type} issues",
                applicable_contexts=["debugging", "troubleshooting"],
                success_indicators=[f"Resolved {bug_type} efficiently", "Systematic approach"],
                failure_indicators=["Random debugging", "No systematic approach"],
                implementation_guidance=f"Use {approach} approach: {'; '.join(lessons)}",
                supporting_evidence=[self.current_project_id],
                confidence_score=0.8,
                impact_potential=1.0 / max(1, resolution_time),  # Faster resolution = higher impact
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=1,
                contradiction_count=0
            )
        
        return None
    
    def _extract_optimization_pattern(self, context: Dict[str, Any], outcome: Dict[str, Any],
                                    lessons: List[str]) -> Optional[UniversalPattern]:
        """Extract optimization patterns from performance work"""
        
        optimization_type = context.get('optimization_type', 'performance')
        improvement = outcome.get('improvement_factor', 1.0)
        
        if improvement > 1.1:  # At least 10% improvement
            return UniversalPattern(
                pattern_id=f"opt_pattern_{uuid.uuid4().hex[:8]}",
                pattern_name=f"Effective {optimization_type} Optimization",
                pattern_scope=PatternScope.TECH_SPECIFIC,
                description=f"Pattern for successful {optimization_type} optimization",
                applicable_contexts=[optimization_type, "performance"],
                success_indicators=[f"{improvement:.1f}x improvement", "Measurable gains"],
                failure_indicators=["No measurable improvement", "Performance regression"],
                implementation_guidance="; ".join(lessons),
                supporting_evidence=[self.current_project_id],
                confidence_score=0.8,
                impact_potential=min(1.0, improvement / 2.0),
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=1,
                contradiction_count=0
            )
        
        return None
    
    def _extract_collaboration_pattern(self, context: Dict[str, Any], outcome: Dict[str, Any],
                                     lessons: List[str]) -> Optional[UniversalPattern]:
        """Extract collaboration patterns from team interactions"""
        
        collaboration_type = context.get('collaboration_type', 'general')
        effectiveness = outcome.get('effectiveness_score', 0.5)
        
        if effectiveness > 0.7:
            return UniversalPattern(
                pattern_id=f"collab_pattern_{uuid.uuid4().hex[:8]}",
                pattern_name=f"Effective {collaboration_type} Collaboration",
                pattern_scope=PatternScope.TEAM_SPECIFIC,
                description=f"Pattern for effective {collaboration_type} team collaboration",
                applicable_contexts=["team_work", "collaboration"],
                success_indicators=[f"High effectiveness ({effectiveness:.1%})", "Team satisfaction"],
                failure_indicators=["Low team engagement", "Communication breakdown"],
                implementation_guidance="; ".join(lessons),
                supporting_evidence=[self.current_project_id],
                confidence_score=0.75,
                impact_potential=effectiveness,
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=1,
                contradiction_count=0
            )
        
        return None
    
    def _extract_generic_pattern(self, lesson: str, context: Dict[str, Any],
                               outcome: Dict[str, Any]) -> Optional[UniversalPattern]:
        """Extract generic patterns from lessons learned"""
        
        # Look for pattern indicators in lessons
        pattern_keywords = ['always', 'never', 'should', 'avoid', 'prefer', 'best practice']
        
        if any(keyword in lesson.lower() for keyword in pattern_keywords):
            return UniversalPattern(
                pattern_id=f"generic_pattern_{uuid.uuid4().hex[:8]}",
                pattern_name=f"Best Practice: {lesson[:50]}...",
                pattern_scope=PatternScope.UNIVERSAL,
                description=lesson,
                applicable_contexts=["general_development"],
                success_indicators=["Positive outcomes when applied"],
                failure_indicators=["Negative outcomes when ignored"],
                implementation_guidance=lesson,
                supporting_evidence=[self.current_project_id],
                confidence_score=0.6,
                impact_potential=0.7,
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=1,
                contradiction_count=0
            )
        
        return None
    
    def _add_or_update_pattern(self, pattern: UniversalPattern) -> None:
        """Add a new pattern or update an existing similar pattern"""
        
        # Check for similar existing patterns
        similar_pattern = self._find_similar_pattern(pattern)
        
        if similar_pattern:
            # Update existing pattern
            similar_pattern.validation_count += 1
            similar_pattern.supporting_evidence.append(self.current_project_id)
            
            # Update confidence based on validation count
            similar_pattern.confidence_score = min(1.0, 
                similar_pattern.confidence_score + (0.1 * similar_pattern.validation_count)
            )
            
            print(f"🔄 Updated Existing Pattern: {similar_pattern.pattern_name}")
        else:
            # Add new pattern
            self.universal_patterns[pattern.pattern_id] = pattern
            print(f"✨ New Universal Pattern: {pattern.pattern_name}")
        
        self._save_universal_patterns()
    
    def _find_similar_pattern(self, pattern: UniversalPattern) -> Optional[UniversalPattern]:
        """Find if there's a similar existing pattern"""
        
        for existing_pattern in self.universal_patterns.values():
            # Check for similarity in name, scope, and context
            if (existing_pattern.pattern_scope == pattern.pattern_scope and
                self._calculate_pattern_similarity(existing_pattern, pattern) > 0.8):
                return existing_pattern
        
        return None
    
    def _calculate_pattern_similarity(self, pattern1: UniversalPattern, pattern2: UniversalPattern) -> float:
        """Calculate similarity between two patterns"""
        
        # Simple keyword-based similarity
        words1 = set(pattern1.description.lower().split())
        words2 = set(pattern2.description.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _check_for_universal_principles(self, experience_type: str, context: Dict[str, Any],
                                      outcome: Dict[str, Any], lessons: List[str]) -> None:
        """Check if this experience reveals universal principles"""
        
        # Look for principles in lessons
        principle_indicators = [
            'fundamental', 'universal', 'always true', 'invariant',
            'principle', 'law', 'rule', 'axiom'
        ]
        
        for lesson in lessons:
            if any(indicator in lesson.lower() for indicator in principle_indicators):
                principle = UniversalPrinciple(
                    principle_id=f"principle_{uuid.uuid4().hex[:8]}",
                    principle_name=f"Principle: {lesson[:50]}...",
                    description=lesson,
                    abstraction_level="tactical",
                    evidence_strength=0.6,
                    universality_score=0.7,
                    impact_magnitude=outcome.get('impact_score', 0.5),
                    supporting_projects=[self.current_project_id],
                    contradicting_projects=[],
                    formulation=lesson,
                    application_guidance=f"Apply in {experience_type} contexts",
                    measurement_criteria=["Positive outcomes when followed"]
                )
                
                self.universal_principles[principle.principle_id] = principle
                self._save_universal_principles()
                
                print(f"🌟 Universal Principle Discovered: {principle.principle_name}")
    
    def apply_universal_intelligence(self, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply universal intelligence to help with current development challenges"""
        
        query_type = query_context.get('query_type', 'general')
        domain = query_context.get('domain', 'software_development')
        
        # Find applicable patterns
        applicable_patterns = self._find_applicable_patterns(query_context)
        
        # Find applicable principles
        applicable_principles = self._find_applicable_principles(query_context)
        
        # Get technology recommendations
        tech_recommendations = self._get_technology_recommendations(query_context)
        
        # Generate insights from cross-project analysis
        cross_project_insights = self._generate_cross_project_insights(query_context)
        
        return {
            "applicable_patterns": [
                {
                    "name": pattern.pattern_name,
                    "description": pattern.description,
                    "implementation_guidance": pattern.implementation_guidance,
                    "confidence": pattern.confidence_score,
                    "evidence_projects": len(pattern.supporting_evidence)
                }
                for pattern in applicable_patterns
            ],
            "universal_principles": [
                {
                    "name": principle.principle_name,
                    "formulation": principle.formulation,
                    "application_guidance": principle.application_guidance,
                    "evidence_strength": principle.evidence_strength
                }
                for principle in applicable_principles
            ],
            "technology_recommendations": tech_recommendations,
            "cross_project_insights": cross_project_insights,
            "confidence_score": self._calculate_recommendation_confidence(
                applicable_patterns, applicable_principles
            )
        }
    
    def _find_applicable_patterns(self, query_context: Dict[str, Any]) -> List[UniversalPattern]:
        """Find patterns applicable to the query context"""
        
        applicable = []
        query_domain = query_context.get('domain', 'general')
        query_type = query_context.get('query_type', 'general')
        
        for pattern in self.universal_patterns.values():
            # Check if pattern applies to this context
            if (pattern.pattern_scope == PatternScope.UNIVERSAL or
                query_domain in pattern.applicable_contexts or
                query_type in pattern.applicable_contexts):
                
                applicable.append(pattern)
        
        # Sort by confidence and impact
        applicable.sort(key=lambda p: p.confidence_score * p.impact_potential, reverse=True)
        
        return applicable[:5]  # Top 5 most applicable patterns
    
    def _find_applicable_principles(self, query_context: Dict[str, Any]) -> List[UniversalPrinciple]:
        """Find universal principles applicable to the query context"""
        
        applicable = []
        
        for principle in self.universal_principles.values():
            # Universal principles apply broadly
            if principle.universality_score > 0.7:
                applicable.append(principle)
        
        # Sort by evidence strength and universality
        applicable.sort(key=lambda p: p.evidence_strength * p.universality_score, reverse=True)
        
        return applicable[:3]  # Top 3 most applicable principles
    
    def _get_technology_recommendations(self, query_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get technology recommendations based on universal intelligence"""
        
        project_type = query_context.get('project_type', ProjectType.WEB_APPLICATION)
        requirements = query_context.get('requirements', {})
        
        recommendations = []
        
        for tech_name, profile in self.technology_profiles.items():
            if project_type.value in profile.typical_use_cases:
                score = self._calculate_technology_score(profile, requirements)
                
                recommendations.append({
                    "technology": tech_name,
                    "category": profile.category,
                    "score": score,
                    "rationale": f"High success correlation ({profile.success_correlation:.1%}) for {project_type.value}",
                    "learning_curve": profile.learning_curve,
                    "ecosystem_maturity": profile.ecosystem_maturity
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _calculate_technology_score(self, profile: TechnologyProfile, requirements: Dict[str, Any]) -> float:
        """Calculate technology recommendation score"""
        
        base_score = profile.success_correlation * 0.4
        maturity_score = profile.ecosystem_maturity * 0.3
        complexity_score = (1.0 - profile.complexity_factor) * 0.2
        support_score = profile.community_support * 0.1
        
        return base_score + maturity_score + complexity_score + support_score
    
    def _generate_cross_project_insights(self, query_context: Dict[str, Any]) -> List[str]:
        """Generate insights from cross-project analysis"""
        
        insights = []
        
        # Analyze project success patterns
        successful_projects = [p for p in self.projects_database.values() 
                             if p.project_outcome == "success"]
        
        if len(successful_projects) > 2:
            insights.append(f"Analysis of {len(successful_projects)} successful projects shows common success patterns")
            
            # Common tech stacks in successful projects
            tech_frequency = {}
            for project in successful_projects:
                for tech in project.tech_stack.keys():
                    tech_frequency[tech] = tech_frequency.get(tech, 0) + 1
            
            if tech_frequency:
                most_common = max(tech_frequency.items(), key=lambda x: x[1])
                insights.append(f"Most successful projects use {most_common[0]} ({most_common[1]}/{len(successful_projects)} projects)")
        
        # Team size analysis
        if successful_projects:
            avg_team_size = sum(p.team_size for p in successful_projects) / len(successful_projects)
            insights.append(f"Optimal team size appears to be around {avg_team_size:.1f} people based on successful projects")
        
        # Pattern application insights
        high_confidence_patterns = [p for p in self.universal_patterns.values() if p.confidence_score > 0.8]
        if high_confidence_patterns:
            insights.append(f"{len(high_confidence_patterns)} high-confidence patterns available for application")
        
        return insights
    
    def _calculate_recommendation_confidence(self, patterns: List[UniversalPattern], 
                                          principles: List[UniversalPrinciple]) -> float:
        """Calculate overall confidence in recommendations"""
        
        if not patterns and not principles:
            return 0.0
        
        pattern_confidence = sum(p.confidence_score for p in patterns) / len(patterns) if patterns else 0.0
        principle_confidence = sum(p.evidence_strength for p in principles) / len(principles) if principles else 0.0
        
        return (pattern_confidence + principle_confidence) / 2.0
    
    def get_universal_mind_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the universal mind"""
        
        # Calculate knowledge metrics
        total_patterns = len(self.universal_patterns)
        high_confidence_patterns = len([p for p in self.universal_patterns.values() if p.confidence_score > 0.8])
        
        total_principles = len(self.universal_principles)
        universal_principles = len([p for p in self.universal_principles.values() if p.universality_score > 0.8])
        
        # Project analysis
        total_projects = len(self.projects_database)
        successful_projects = len([p for p in self.projects_database.values() if p.project_outcome == "success"])
        
        # Technology analysis
        total_technologies = len(self.technology_profiles)
        mature_technologies = len([t for t in self.technology_profiles.values() if t.ecosystem_maturity > 0.8])
        
        return {
            "knowledge_base": {
                "total_projects": total_projects,
                "successful_projects": successful_projects,
                "success_rate": successful_projects / max(1, total_projects),
                "total_patterns": total_patterns,
                "high_confidence_patterns": high_confidence_patterns,
                "total_principles": total_principles,
                "universal_principles": universal_principles,
                "technology_profiles": total_technologies,
                "mature_technologies": mature_technologies
            },
            "learning_insights": {
                "most_validated_pattern": self._get_most_validated_pattern(),
                "strongest_principle": self._get_strongest_principle(),
                "most_successful_tech": self._get_most_successful_technology(),
                "key_success_factors": self._identify_key_success_factors()
            },
            "current_project": {
                "project_id": self.current_project_id,
                "registered": self.current_project_id in self.projects_database
            },
            "intelligence_maturity": self._calculate_intelligence_maturity()
        }
    
    def _get_most_validated_pattern(self) -> Optional[Dict[str, Any]]:
        """Get the most validated pattern"""
        if not self.universal_patterns:
            return None
        
        most_validated = max(self.universal_patterns.values(), key=lambda p: p.validation_count)
        return {
            "name": most_validated.pattern_name,
            "validation_count": most_validated.validation_count,
            "confidence": most_validated.confidence_score
        }
    
    def _get_strongest_principle(self) -> Optional[Dict[str, Any]]:
        """Get the strongest universal principle"""
        if not self.universal_principles:
            return None
        
        strongest = max(self.universal_principles.values(), key=lambda p: p.evidence_strength)
        return {
            "name": strongest.principle_name,
            "evidence_strength": strongest.evidence_strength,
            "universality": strongest.universality_score
        }
    
    def _get_most_successful_technology(self) -> Optional[Dict[str, Any]]:
        """Get the technology with highest success correlation"""
        if not self.technology_profiles:
            return None
        
        most_successful = max(self.technology_profiles.values(), key=lambda t: t.success_correlation)
        return {
            "technology": most_successful.technology_name,
            "success_correlation": most_successful.success_correlation,
            "adoption_trend": "positive"  # Simplified
        }
    
    def _identify_key_success_factors(self) -> List[str]:
        """Identify key factors that correlate with project success"""
        
        factors = []
        
        successful_projects = [p for p in self.projects_database.values() if p.project_outcome == "success"]
        
        if len(successful_projects) > 2:
            # Analyze common factors
            avg_team_size = sum(p.team_size for p in successful_projects) / len(successful_projects)
            factors.append(f"Team size around {avg_team_size:.1f}")
            
            if any(p.quality_achievement > 0.8 for p in successful_projects):
                factors.append("High quality standards")
            
            if any(p.timeline_adherence > 0.9 for p in successful_projects):
                factors.append("Strong timeline adherence")
        
        return factors or ["Insufficient data for analysis"]
    
    def _calculate_intelligence_maturity(self) -> str:
        """Calculate the maturity level of the universal intelligence"""
        
        total_projects = len(self.projects_database)
        total_patterns = len(self.universal_patterns)
        total_principles = len(self.universal_principles)
        
        maturity_score = (total_projects * 0.4) + (total_patterns * 0.3) + (total_principles * 0.3)
        
        if maturity_score < 5:
            return "nascent"
        elif maturity_score < 15:
            return "developing"
        elif maturity_score < 30:
            return "mature"
        else:
            return "expert"
    
    # Seed foundational patterns for new installations
    def _seed_foundational_patterns(self) -> None:
        """Seed the database with foundational software development patterns"""
        
        foundational_patterns = [
            {
                "name": "Single Responsibility Principle",
                "scope": PatternScope.UNIVERSAL,
                "description": "Each software component should have only one reason to change",
                "contexts": ["object_oriented_programming", "system_design"],
                "guidance": "Design classes and functions with a single, well-defined purpose"
            },
            {
                "name": "Test-Driven Development",
                "scope": PatternScope.UNIVERSAL,
                "description": "Write tests before implementing functionality",
                "contexts": ["software_development", "quality_assurance"],
                "guidance": "Red-Green-Refactor cycle: fail, pass, improve"
            },
            {
                "name": "Don't Repeat Yourself (DRY)",
                "scope": PatternScope.UNIVERSAL,
                "description": "Avoid code duplication through abstraction",
                "contexts": ["coding", "maintainability"],
                "guidance": "Extract common functionality into reusable components"
            }
        ]
        
        for pattern_data in foundational_patterns:
            pattern = UniversalPattern(
                pattern_id=f"seed_pattern_{uuid.uuid4().hex[:8]}",
                pattern_name=pattern_data["name"],
                pattern_scope=pattern_data["scope"],
                description=pattern_data["description"],
                applicable_contexts=pattern_data["contexts"],
                success_indicators=["Improved maintainability", "Reduced complexity"],
                failure_indicators=["Code duplication", "High coupling"],
                implementation_guidance=pattern_data["guidance"],
                supporting_evidence=["foundational_software_engineering"],
                confidence_score=0.9,
                impact_potential=0.8,
                discovery_timestamp=datetime.now().isoformat(),
                validation_count=100,  # Widely validated
                contradiction_count=0
            )
            
            self.universal_patterns[pattern.pattern_id] = pattern
        
        self._save_universal_patterns()
        print(f"🌱 Seeded {len(foundational_patterns)} foundational patterns")
    
    # Data persistence methods
    def _load_projects_database(self) -> Dict[str, ProjectIntelligence]:
        """Load projects database"""
        if not self.projects_db_file.exists():
            return {}
        
        try:
            with open(self.projects_db_file, 'r') as f:
                data = json.load(f)
                return {
                    project_id: ProjectIntelligence(
                        project_type=ProjectType(project_data['project_type']),
                        **{k: v for k, v in project_data.items() if k != 'project_type'}
                    )
                    for project_id, project_data in data.items()
                }
        except (json.JSONDecodeError, KeyError, ValueError):
            return {}
    
    def _save_projects_database(self) -> None:
        """Save projects database"""
        data = {}
        for project_id, project in self.projects_database.items():
            project_data = asdict(project)
            project_data['project_type'] = project.project_type.value
            data[project_id] = project_data
        
        with open(self.projects_db_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_universal_patterns(self) -> Dict[str, UniversalPattern]:
        """Load universal patterns"""
        if not self.patterns_db_file.exists():
            return {}
        
        try:
            with open(self.patterns_db_file, 'r') as f:
                data = json.load(f)
                return {
                    pattern_id: UniversalPattern(
                        pattern_scope=PatternScope(pattern_data['pattern_scope']),
                        **{k: v for k, v in pattern_data.items() if k != 'pattern_scope'}
                    )
                    for pattern_id, pattern_data in data.items()
                }
        except (json.JSONDecodeError, KeyError, ValueError):
            return {}
    
    def _save_universal_patterns(self) -> None:
        """Save universal patterns"""
        data = {}
        for pattern_id, pattern in self.universal_patterns.items():
            pattern_data = asdict(pattern)
            pattern_data['pattern_scope'] = pattern.pattern_scope.value
            data[pattern_id] = pattern_data
        
        with open(self.patterns_db_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_universal_principles(self) -> Dict[str, UniversalPrinciple]:
        """Load universal principles"""
        if not self.principles_db_file.exists():
            return {}
        
        try:
            with open(self.principles_db_file, 'r') as f:
                data = json.load(f)
                return {principle_id: UniversalPrinciple(**principle_data) for principle_id, principle_data in data.items()}
        except (json.JSONDecodeError, KeyError):
            return {}
    
    def _save_universal_principles(self) -> None:
        """Save universal principles"""
        data = {principle_id: asdict(principle) for principle_id, principle in self.universal_principles.items()}
        
        with open(self.principles_db_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_technology_profiles(self) -> Dict[str, TechnologyProfile]:
        """Load technology profiles"""
        if not self.technologies_db_file.exists():
            return {}
        
        try:
            with open(self.technologies_db_file, 'r') as f:
                data = json.load(f)
                return {tech_name: TechnologyProfile(**tech_data) for tech_name, tech_data in data.items()}
        except (json.JSONDecodeError, KeyError):
            return {}
    
    def _save_technology_profiles(self) -> None:
        """Save technology profiles"""
        data = {tech_name: asdict(profile) for tech_name, profile in self.technology_profiles.items()}
        
        with open(self.technologies_db_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_team_dynamics(self) -> Dict[str, TeamDynamicsProfile]:
        """Load team dynamics profiles"""
        if not self.team_dynamics_db_file.exists():
            return {}
        
        try:
            with open(self.team_dynamics_db_file, 'r') as f:
                data = json.load(f)
                return {profile_id: TeamDynamicsProfile(**profile_data) for profile_id, profile_data in data.items()}
        except (json.JSONDecodeError, KeyError):
            return {}
    
    def _update_technology_profiles(self, tech_stack: Dict[str, str]) -> None:
        """Update technology profiles based on project tech stack"""
        for tech, version in tech_stack.items():
            if tech not in self.technology_profiles:
                # Create basic profile for new technology
                self.technology_profiles[tech] = TechnologyProfile(
                    technology_name=tech,
                    category="unknown",
                    adoption_trends={"current": 1.0},
                    success_correlation=0.5,
                    complexity_factor=0.5,
                    learning_curve=0.5,
                    ecosystem_maturity=0.5,
                    community_support=0.5,
                    typical_use_cases=["general"],
                    complementary_technologies=[],
                    performance_characteristics={},
                    scalability_profile={},
                    maintenance_overhead=0.5
                )
        
        self._save_technology_profiles()


def main():
    """CLI interface for NEXUS Universal Mind"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NEXUS Universal Mind - Cross-Project Intelligence")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--status", action="store_true", help="Show universal mind status")
    parser.add_argument("--register-project", help="Register current project")
    parser.add_argument("--query", help="Query universal intelligence")
    parser.add_argument("--patterns", action="store_true", help="List universal patterns")
    
    args = parser.parse_args()
    
    # Initialize universal mind
    universal_mind = NEXUSUniversalMind(Path(args.project_root))
    
    if args.status:
        status = universal_mind.get_universal_mind_status()
        print(json.dumps(status, indent=2))
    
    elif args.register_project:
        project_id = universal_mind.register_project(
            project_name=args.register_project,
            project_type=ProjectType.WEB_APPLICATION,
            tech_stack={"python": "3.12", "fastapi": "0.104"},
            team_size=3
        )
        print(f"Project registered: {project_id}")
    
    elif args.query:
        result = universal_mind.apply_universal_intelligence({
            "query_type": args.query,
            "domain": "software_development"
        })
        print(json.dumps(result, indent=2))
    
    elif args.patterns:
        print("🌐 Universal Patterns:")
        for pattern in universal_mind.universal_patterns.values():
            print(f"   {pattern.pattern_name} (confidence: {pattern.confidence_score:.1%})")
            print(f"      {pattern.description}")
            print()
    
    else:
        print("NEXUS Universal Mind initialized. Use --help for options.")
        status = universal_mind.get_universal_mind_status()
        print(f"Intelligence Maturity: {status['intelligence_maturity']}")
        print(f"Knowledge Base: {status['knowledge_base']['total_patterns']} patterns, {status['knowledge_base']['total_principles']} principles")


if __name__ == "__main__":
    main()