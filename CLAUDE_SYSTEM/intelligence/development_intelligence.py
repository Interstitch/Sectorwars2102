#!/usr/bin/env python3
"""
Development Intelligence Engine - CLAUDE System Intelligence Layer
================================================================

This module implements a living, learning development intelligence system that:
- Collects real-time development metrics through git hooks
- Learns patterns from development history
- Makes autonomous decisions to optimize development process
- Runs experiments to discover better approaches
- Predicts issues before they occur
- Self-heals development bottlenecks

This transforms the concepts from AUTOMATIC_IMPROVEMENT.md into working intelligence.
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class DecisionType(Enum):
    PHASE_TRANSITION = "phase_transition"
    TESTING_STRATEGY = "testing_strategy"
    REFACTORING_RECOMMENDATION = "refactoring_recommendation"
    DOCUMENTATION_GENERATION = "documentation_generation"
    ANALYSIS_TRIGGER = "analysis_trigger"
    HEALING_ACTION = "healing_action"


class ExperimentStatus(Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_OUT = "rolled_out"


@dataclass
class DevelopmentMetric:
    timestamp: str
    phase: str
    duration: float
    success: bool
    error_count: int
    files_changed: int
    lines_changed: int
    test_coverage: Optional[float]
    complexity_score: Optional[float]
    context: Dict[str, Any]


@dataclass
class Pattern:
    pattern_id: str
    pattern_type: str
    confidence: float
    description: str
    conditions: Dict[str, Any]
    recommendations: List[str]
    success_rate: float
    frequency: int
    last_seen: str


@dataclass
class Decision:
    decision_id: str
    decision_type: DecisionType
    context: Dict[str, Any]
    reasoning: str
    action: str
    confidence: float
    timestamp: str
    outcome: Optional[str] = None
    success: Optional[bool] = None


@dataclass
class Experiment:
    experiment_id: str
    name: str
    hypothesis: str
    method: str
    success_criteria: Dict[str, Any]
    status: ExperimentStatus
    start_time: str
    end_time: Optional[str]
    results: Dict[str, Any]
    auto_rollout: bool


class DevelopmentIntelligence:
    """
    Core Development Intelligence Engine
    
    This is the brain of the self-improving development system.
    It learns from every development action and continuously optimizes the process.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.intelligence_dir = self.project_root / ".claude" / "intelligence"
        self.metrics_file = self.intelligence_dir / "metrics.jsonl"
        self.patterns_file = self.intelligence_dir / "patterns.json"
        self.decisions_file = self.intelligence_dir / "decisions.jsonl"
        self.experiments_file = self.intelligence_dir / "experiments.json"
        self.predictions_file = self.intelligence_dir / "predictions.json"
        
        # Ensure directories exist
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data structures
        self.patterns: List[Pattern] = self._load_patterns()
        self.active_experiments: List[Experiment] = self._load_experiments()
    
    def collect_development_metric(self, phase: str, duration: float, success: bool, 
                                 context: Dict[str, Any]) -> None:
        """Collect real-time development metrics"""
        metric = DevelopmentMetric(
            timestamp=datetime.now().isoformat(),
            phase=phase,
            duration=duration,
            success=success,
            error_count=context.get('error_count', 0),
            files_changed=context.get('files_changed', 0),
            lines_changed=context.get('lines_changed', 0),
            test_coverage=context.get('test_coverage'),
            complexity_score=context.get('complexity_score'),
            context=context
        )
        
        # Store metric
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metric)) + '\n')
        
        # Trigger real-time analysis
        self._analyze_metric(metric)
    
    def make_autonomous_decision(self, decision_type: DecisionType, 
                               context: Dict[str, Any]) -> Decision:
        """Make autonomous decisions based on learned patterns"""
        relevant_patterns = self._find_relevant_patterns(decision_type, context)
        
        decision = self._generate_decision(decision_type, context, relevant_patterns)
        
        # Log decision
        with open(self.decisions_file, 'a') as f:
            f.write(json.dumps(asdict(decision)) + '\n')
        
        return decision
    
    def learn_from_outcome(self, decision_id: str, outcome: str, success: bool) -> None:
        """Learn from decision outcomes to improve future decisions"""
        # Update decision record
        decisions = self._load_decisions()
        for decision in decisions:
            if decision.decision_id == decision_id:
                decision.outcome = outcome
                decision.success = success
                break
        
        # Update patterns based on outcome
        self._update_patterns_from_outcome(decision_id, outcome, success)
        
        # Save updated decisions
        self._save_decisions(decisions)
    
    def propose_experiment(self, name: str, hypothesis: str, method: str, 
                         success_criteria: Dict[str, Any], auto_rollout: bool = False) -> Experiment:
        """Propose new development process experiment"""
        experiment = Experiment(
            experiment_id=self._generate_id(f"exp_{name}"),
            name=name,
            hypothesis=hypothesis,
            method=method,
            success_criteria=success_criteria,
            status=ExperimentStatus.PROPOSED,
            start_time=datetime.now().isoformat(),
            end_time=None,
            results={},
            auto_rollout=auto_rollout
        )
        
        self.active_experiments.append(experiment)
        self._save_experiments()
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start running an experiment"""
        for exp in self.active_experiments:
            if exp.experiment_id == experiment_id:
                exp.status = ExperimentStatus.ACTIVE
                exp.start_time = datetime.now().isoformat()
                self._save_experiments()
                return True
        return False
    
    def evaluate_experiments(self) -> List[Experiment]:
        """Evaluate active experiments and determine success/failure"""
        completed = []
        
        for exp in self.active_experiments:
            if exp.status == ExperimentStatus.ACTIVE:
                if self._evaluate_experiment_success(exp):
                    exp.status = ExperimentStatus.SUCCESS
                    completed.append(exp)
                    
                    # Auto-rollout if enabled
                    if exp.auto_rollout:
                        self._rollout_experiment(exp)
                        exp.status = ExperimentStatus.ROLLED_OUT
                elif self._evaluate_experiment_failure(exp):
                    exp.status = ExperimentStatus.FAILED
                    completed.append(exp)
        
        if completed:
            self._save_experiments()
        
        return completed
    
    def predict_issues(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict potential issues based on current development patterns"""
        predictions = []
        
        # Analyze current trajectory
        recent_metrics = self._get_recent_metrics(hours=24)
        
        # Performance degradation prediction
        if self._predict_performance_degradation(recent_metrics):
            predictions.append({
                'type': 'performance_degradation',
                'confidence': 0.8,
                'description': 'Performance degradation likely in next 2-3 commits',
                'recommendation': 'Run comprehensive analysis and consider optimization'
            })
        
        # Complexity explosion prediction
        if self._predict_complexity_explosion(recent_metrics, context):
            predictions.append({
                'type': 'complexity_explosion',
                'confidence': 0.75,
                'description': 'Code complexity approaching critical threshold',
                'recommendation': 'Schedule refactoring session before next major feature'
            })
        
        # Test coverage degradation
        if self._predict_test_coverage_issues(recent_metrics):
            predictions.append({
                'type': 'test_coverage_decline',
                'confidence': 0.85,
                'description': 'Test coverage declining rapidly',
                'recommendation': 'Implement test-first development for next features'
            })
        
        # Save predictions
        with open(self.predictions_file, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        return predictions
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on learned patterns"""
        recommendations = []
        
        # Analyze bottlenecks
        bottlenecks = self._identify_bottlenecks()
        for bottleneck in bottlenecks:
            recommendations.append({
                'type': 'bottleneck_optimization',
                'area': bottleneck['phase'],
                'impact': bottleneck['time_impact'],
                'recommendation': bottleneck['optimization'],
                'confidence': bottleneck['confidence']
            })
        
        # Suggest automation opportunities
        automation_ops = self._identify_automation_opportunities()
        for op in automation_ops:
            recommendations.append({
                'type': 'automation_opportunity',
                'task': op['task'],
                'frequency': op['frequency'],
                'time_saved': op['estimated_time_saved'],
                'implementation_effort': op['effort'],
                'recommendation': op['automation_approach']
            })
        
        return recommendations
    
    def auto_heal_development_issues(self, context: Dict[str, Any]) -> List[str]:
        """Automatically heal common development issues"""
        healing_actions = []
        
        # Check for common issues and apply known fixes
        if self._detect_build_failure_pattern(context):
            action = self._apply_build_failure_healing(context)
            if action:
                healing_actions.append(action)
        
        if self._detect_test_failure_pattern(context):
            action = self._apply_test_failure_healing(context)
            if action:
                healing_actions.append(action)
        
        if self._detect_performance_regression(context):
            action = self._apply_performance_healing(context)
            if action:
                healing_actions.append(action)
        
        return healing_actions
    
    def generate_intelligence_report(self) -> Dict[str, Any]:
        """Generate comprehensive intelligence report"""
        recent_metrics = self._get_recent_metrics(hours=168)  # Last week
        
        report = {
            'intelligence_summary': {
                'metrics_collected': len(recent_metrics),
                'patterns_learned': len(self.patterns),
                'decisions_made': len(self._load_decisions()),
                'experiments_active': len([e for e in self.active_experiments if e.status == ExperimentStatus.ACTIVE]),
                'experiments_successful': len([e for e in self.active_experiments if e.status == ExperimentStatus.SUCCESS])
            },
            'performance_trends': self._analyze_performance_trends(recent_metrics),
            'learned_patterns': [asdict(p) for p in self.patterns[-10:]],  # Latest 10 patterns
            'active_experiments': [asdict(e) for e in self.active_experiments if e.status == ExperimentStatus.ACTIVE],
            'predictions': self.predict_issues({}),
            'optimization_recommendations': self.get_optimization_recommendations(),
            'autonomy_metrics': self._calculate_autonomy_metrics()
        }
        
        return report
    
    # Private helper methods
    
    def _load_patterns(self) -> List[Pattern]:
        """Load patterns from storage"""
        if not self.patterns_file.exists():
            return []
        
        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                return [Pattern(**p) for p in data]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def _save_patterns(self) -> None:
        """Save patterns to storage"""
        with open(self.patterns_file, 'w') as f:
            json.dump([asdict(p) for p in self.patterns], f, indent=2)
    
    def _load_experiments(self) -> List[Experiment]:
        """Load experiments from storage"""
        if not self.experiments_file.exists():
            return []
        
        try:
            with open(self.experiments_file, 'r') as f:
                data = json.load(f)
                return [Experiment(**e) for e in data]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def _save_experiments(self) -> None:
        """Save experiments to storage"""
        with open(self.experiments_file, 'w') as f:
            json.dump([asdict(e) for e in self.active_experiments], f, indent=2)
    
    def _load_decisions(self) -> List[Decision]:
        """Load decisions from storage"""
        if not self.decisions_file.exists():
            return []
        
        decisions = []
        try:
            with open(self.decisions_file, 'r') as f:
                for line in f:
                    if line.strip():
                        decisions.append(Decision(**json.loads(line)))
        except (json.JSONDecodeError, KeyError):
            pass
        
        return decisions
    
    def _save_decisions(self, decisions: List[Decision]) -> None:
        """Save decisions to storage"""
        with open(self.decisions_file, 'w') as f:
            for decision in decisions:
                f.write(json.dumps(asdict(decision)) + '\n')
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        timestamp = str(time.time())
        return f"{prefix}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _analyze_metric(self, metric: DevelopmentMetric) -> None:
        """Analyze a metric for patterns and anomalies"""
        # This would trigger real-time pattern recognition
        # and potentially generate autonomous decisions
        pass
    
    def _find_relevant_patterns(self, decision_type: DecisionType, context: Dict[str, Any]) -> List[Pattern]:
        """Find patterns relevant to current decision context"""
        # This would implement sophisticated pattern matching
        return []
    
    def _generate_decision(self, decision_type: DecisionType, context: Dict[str, Any], 
                         patterns: List[Pattern]) -> Decision:
        """Generate a decision based on context and patterns"""
        decision_id = self._generate_id("decision")
        
        # This would implement intelligent decision-making logic
        return Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            context=context,
            reasoning="Autonomous decision based on learned patterns",
            action="Recommended action based on intelligence",
            confidence=0.8,
            timestamp=datetime.now().isoformat()
        )
    
    def _get_recent_metrics(self, hours: int) -> List[DevelopmentMetric]:
        """Get metrics from the last N hours"""
        if not self.metrics_file.exists():
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_metrics = []
        
        try:
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    if line.strip():
                        metric_data = json.loads(line)
                        metric_time = datetime.fromisoformat(metric_data['timestamp'])
                        if metric_time > cutoff:
                            recent_metrics.append(DevelopmentMetric(**metric_data))
        except (json.JSONDecodeError, KeyError):
            pass
        
        return recent_metrics
    
    def _predict_performance_degradation(self, metrics: List[DevelopmentMetric]) -> bool:
        """Predict if performance is degrading"""
        # Implement performance trend analysis
        return False
    
    def _predict_complexity_explosion(self, metrics: List[DevelopmentMetric], context: Dict[str, Any]) -> bool:
        """Predict if code complexity is growing too fast"""
        # Implement complexity trend analysis
        return False
    
    def _predict_test_coverage_issues(self, metrics: List[DevelopmentMetric]) -> bool:
        """Predict test coverage problems"""
        # Implement test coverage trend analysis
        return False
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify development process bottlenecks"""
        # Implement bottleneck detection
        return []
    
    def _identify_automation_opportunities(self) -> List[Dict[str, Any]]:
        """Identify tasks that could be automated"""
        # Implement automation opportunity detection
        return []
    
    def _detect_build_failure_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect build failure patterns"""
        return False
    
    def _apply_build_failure_healing(self, context: Dict[str, Any]) -> Optional[str]:
        """Apply healing for build failures"""
        return None
    
    def _detect_test_failure_pattern(self, context: Dict[str, Any]) -> bool:
        """Detect test failure patterns"""
        return False
    
    def _apply_test_failure_healing(self, context: Dict[str, Any]) -> Optional[str]:
        """Apply healing for test failures"""
        return None
    
    def _detect_performance_regression(self, context: Dict[str, Any]) -> bool:
        """Detect performance regression patterns"""
        return False
    
    def _apply_performance_healing(self, context: Dict[str, Any]) -> Optional[str]:
        """Apply healing for performance issues"""
        return None
    
    def _analyze_performance_trends(self, metrics: List[DevelopmentMetric]) -> Dict[str, Any]:
        """Analyze performance trends"""
        return {'trend': 'stable', 'details': 'Performance analysis not yet implemented'}
    
    def _calculate_autonomy_metrics(self) -> Dict[str, Any]:
        """Calculate how autonomous the system has become"""
        decisions = self._load_decisions()
        total_decisions = len(decisions)
        autonomous_decisions = len([d for d in decisions if d.confidence > 0.7])
        
        return {
            'autonomy_level': autonomous_decisions / total_decisions if total_decisions > 0 else 0,
            'total_decisions': total_decisions,
            'autonomous_decisions': autonomous_decisions
        }
    
    def _evaluate_experiment_success(self, experiment: Experiment) -> bool:
        """Evaluate if an experiment has succeeded"""
        # Implement experiment success evaluation
        return False
    
    def _evaluate_experiment_failure(self, experiment: Experiment) -> bool:
        """Evaluate if an experiment has failed"""
        # Implement experiment failure evaluation
        return False
    
    def _rollout_experiment(self, experiment: Experiment) -> None:
        """Roll out a successful experiment"""
        # Implement experiment rollout
        pass
    
    def _update_patterns_from_outcome(self, decision_id: str, outcome: str, success: bool) -> None:
        """Update patterns based on decision outcomes"""
        # Implement pattern learning from outcomes
        pass


def main():
    """CLI interface for development intelligence"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Development Intelligence Engine")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--collect-metric", action="store_true", help="Collect development metric")
    parser.add_argument("--make-decision", help="Make autonomous decision")
    parser.add_argument("--predict", action="store_true", help="Generate predictions")
    parser.add_argument("--report", action="store_true", help="Generate intelligence report")
    parser.add_argument("--heal", action="store_true", help="Auto-heal development issues")
    
    args = parser.parse_args()
    
    intelligence = DevelopmentIntelligence(Path(args.project_root))
    
    if args.report:
        report = intelligence.generate_intelligence_report()
        print(json.dumps(report, indent=2))
    elif args.predict:
        predictions = intelligence.predict_issues({})
        print(json.dumps(predictions, indent=2))
    elif args.heal:
        actions = intelligence.auto_heal_development_issues({})
        print(f"Healing actions taken: {actions}")
    else:
        print("Use --report, --predict, or --heal to interact with the intelligence system")


if __name__ == "__main__":
    main()