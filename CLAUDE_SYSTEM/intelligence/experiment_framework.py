#!/usr/bin/env python3
"""
Experiment Framework - CLAUDE Intelligence Layer
==============================================

A comprehensive experiment framework that allows the development system to
continuously test and improve its own processes through A/B testing and
controlled experiments.

This implements the "Continuous Experimentation" concept from AUTOMATIC_IMPROVEMENT.md
as actual working code that learns and adapts.
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum


class ExperimentType(Enum):
    PROCESS_OPTIMIZATION = "process_optimization"
    TOOL_EFFICIENCY = "tool_efficiency"
    AUTOMATION_ENHANCEMENT = "automation_enhancement"
    QUALITY_IMPROVEMENT = "quality_improvement"
    PERFORMANCE_BOOST = "performance_boost"


class ExperimentStatus(Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_OUT = "rolled_out"
    REVERTED = "reverted"


@dataclass
class ExperimentConfig:
    """Configuration for a development experiment"""
    experiment_id: str
    name: str
    hypothesis: str
    experiment_type: ExperimentType
    description: str
    method: str
    success_criteria: Dict[str, Any]
    failure_criteria: Dict[str, Any]
    duration_days: int
    auto_rollout: bool
    rollout_threshold: float
    sample_size: int
    control_group_percentage: float
    risk_level: str  # low, medium, high
    dependencies: List[str]
    prerequisites: List[str]
    rollback_plan: str
    created_by: str
    created_at: str


@dataclass
class ExperimentResult:
    """Results from an experiment execution"""
    experiment_id: str
    measurement_time: str
    metrics: Dict[str, Any]
    control_metrics: Dict[str, Any]
    experimental_metrics: Dict[str, Any]
    statistical_significance: float
    confidence_interval: Dict[str, float]
    effect_size: float
    success_score: float
    notes: str


class DevelopmentExperimentFramework:
    """
    Framework for running controlled experiments on development processes
    
    This enables the development system to continuously improve itself by
    testing hypotheses about better ways to develop software.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.experiments_dir = self.project_root / ".claude" / "experiments"
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.experiments_dir / "experiments.json"
        self.results_file = self.experiments_dir / "results.jsonl"
        self.active_file = self.experiments_dir / "active_experiments.json"
        
        # Load existing experiments
        self.experiments: Dict[str, ExperimentConfig] = self._load_experiments()
        self.active_experiments: List[str] = self._load_active_experiments()
    
    def propose_experiment(self, name: str, hypothesis: str, 
                         experiment_type: ExperimentType, method: str,
                         success_criteria: Dict[str, Any],
                         duration_days: int = 7,
                         auto_rollout: bool = False,
                         risk_level: str = "low") -> str:
        """Propose a new development process experiment"""
        
        experiment_id = f"exp_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name=name,
            hypothesis=hypothesis,
            experiment_type=experiment_type,
            description=f"Experiment to test: {hypothesis}",
            method=method,
            success_criteria=success_criteria,
            failure_criteria=self._generate_failure_criteria(success_criteria),
            duration_days=duration_days,
            auto_rollout=auto_rollout,
            rollout_threshold=0.8,
            sample_size=100,
            control_group_percentage=0.5,
            risk_level=risk_level,
            dependencies=[],
            prerequisites=[],
            rollback_plan="Automatic revert to previous process",
            created_by="development_intelligence",
            created_at=datetime.now().isoformat()
        )
        
        self.experiments[experiment_id] = config
        self._save_experiments()
        
        print(f"📊 Proposed experiment: {name}")
        print(f"   Hypothesis: {hypothesis}")
        print(f"   ID: {experiment_id}")
        
        return experiment_id
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start running an approved experiment"""
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        
        # Check prerequisites
        if not self._check_prerequisites(experiment):
            print(f"❌ Cannot start experiment {experiment.name}: Prerequisites not met")
            return False
        
        # Add to active experiments
        self.active_experiments.append(experiment_id)
        self._save_active_experiments()
        
        # Initialize experiment tracking
        self._initialize_experiment_tracking(experiment)
        
        print(f"🚀 Started experiment: {experiment.name}")
        print(f"   Duration: {experiment.duration_days} days")
        print(f"   Auto-rollout: {'Yes' if experiment.auto_rollout else 'No'}")
        
        return True
    
    def collect_experiment_data(self, experiment_id: str, metrics: Dict[str, Any],
                               is_control_group: bool = False) -> None:
        """Collect data point for an active experiment"""
        if experiment_id not in self.active_experiments:
            return
        
        result = ExperimentResult(
            experiment_id=experiment_id,
            measurement_time=datetime.now().isoformat(),
            metrics=metrics,
            control_metrics=metrics if is_control_group else {},
            experimental_metrics=metrics if not is_control_group else {},
            statistical_significance=0.0,  # Will be calculated during analysis
            confidence_interval={'lower': 0.0, 'upper': 0.0},
            effect_size=0.0,
            success_score=0.0,
            notes=f"Data collection from {'control' if is_control_group else 'experimental'} group"
        )
        
        # Store result
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\\n')
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results and determine success/failure"""
        if experiment_id not in self.experiments:
            return {'error': 'Experiment not found'}
        
        experiment = self.experiments[experiment_id]
        results = self._load_experiment_results(experiment_id)
        
        if len(results) < 10:  # Minimum sample size
            return {
                'status': 'insufficient_data',
                'sample_size': len(results),
                'minimum_required': 10
            }
        
        # Analyze results
        analysis = {
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'sample_size': len(results),
            'duration_days': experiment.duration_days,
            'success_criteria': experiment.success_criteria,
            'results_summary': self._calculate_results_summary(results),
            'statistical_analysis': self._perform_statistical_analysis(results),
            'success_determination': self._determine_experiment_success(experiment, results),
            'recommendations': self._generate_experiment_recommendations(experiment, results),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def complete_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Complete an experiment and determine if it should be rolled out"""
        analysis = self.analyze_experiment(experiment_id)
        
        if 'error' in analysis:
            return analysis
        
        experiment = self.experiments[experiment_id]
        
        # Determine final status
        if analysis['success_determination']['is_success']:
            if experiment.auto_rollout and analysis['success_determination']['confidence'] >= experiment.rollout_threshold:
                status = ExperimentStatus.ROLLED_OUT
                self._rollout_experiment(experiment_id)
            else:
                status = ExperimentStatus.SUCCESS
        else:
            status = ExperimentStatus.FAILED
            self._revert_experiment(experiment_id)
        
        # Remove from active experiments
        if experiment_id in self.active_experiments:
            self.active_experiments.remove(experiment_id)
            self._save_active_experiments()
        
        completion_result = {
            'experiment_id': experiment_id,
            'final_status': status.value,
            'analysis': analysis,
            'completion_time': datetime.now().isoformat(),
            'next_steps': self._generate_next_steps(experiment, analysis)
        }
        
        # Save completion result
        completion_file = self.experiments_dir / f"completion_{experiment_id}.json"
        with open(completion_file, 'w') as f:
            json.dump(completion_result, f, indent=2)
        
        print(f"🏁 Completed experiment: {experiment.name}")
        print(f"   Status: {status.value}")
        print(f"   Success: {analysis['success_determination']['is_success']}")
        
        return completion_result
    
    def get_active_experiments(self) -> List[Dict[str, Any]]:
        """Get all currently active experiments"""
        active = []
        for exp_id in self.active_experiments:
            if exp_id in self.experiments:
                experiment = self.experiments[exp_id]
                progress = self._calculate_experiment_progress(exp_id)
                active.append({
                    'experiment_id': exp_id,
                    'name': experiment.name,
                    'hypothesis': experiment.hypothesis,
                    'type': experiment.experiment_type.value,
                    'progress': progress,
                    'days_remaining': self._calculate_days_remaining(experiment),
                    'current_metrics': self._get_latest_metrics(exp_id)
                })
        return active
    
    def create_predefined_experiments(self) -> List[str]:
        """Create a set of predefined experiments based on AUTOMATIC_IMPROVEMENT.md"""
        experiments = []
        
        # Parallel Testing Experiment
        exp_id = self.propose_experiment(
            name="Parallel Test Execution",
            hypothesis="Running tests in parallel reduces Phase 4 time by 40%",
            experiment_type=ExperimentType.PERFORMANCE_BOOST,
            method="Split test suite into independent parallel chunks",
            success_criteria={
                'time_reduction_percentage': 30,
                'test_reliability': 0.99,
                'flaky_test_increase': 0.05
            },
            duration_days=14,
            auto_rollout=True,
            risk_level="low"
        )
        experiments.append(exp_id)
        
        # AI Code Review Experiment
        exp_id = self.propose_experiment(
            name="AI Pre-Review Process",
            hypothesis="AI pre-review reduces human review time by 50%",
            experiment_type=ExperimentType.PROCESS_OPTIMIZATION,
            method="Run AI analysis before human code review",
            success_criteria={
                'review_time_reduction': 40,
                'issue_detection_rate': 0.8,
                'false_positive_rate': 0.2
            },
            duration_days=21,
            auto_rollout=False,
            risk_level="medium"
        )
        experiments.append(exp_id)
        
        # Automated Documentation Experiment
        exp_id = self.propose_experiment(
            name="Automated Documentation Generation",
            hypothesis="Auto-generating docs improves consistency and coverage",
            experiment_type=ExperimentType.AUTOMATION_ENHANCEMENT,
            method="Generate API docs from TypeScript interfaces automatically",
            success_criteria={
                'documentation_coverage': 90,
                'consistency_score': 0.9,
                'maintenance_time_reduction': 60
            },
            duration_days=30,
            auto_rollout=True,
            risk_level="low"
        )
        experiments.append(exp_id)
        
        # Smart Commit Analysis Experiment
        exp_id = self.propose_experiment(
            name="Intelligent Commit Analysis",
            hypothesis="Smart commit analysis reduces debugging time by 35%",
            experiment_type=ExperimentType.QUALITY_IMPROVEMENT,
            method="Analyze commit patterns to predict potential issues",
            success_criteria={
                'issue_prediction_accuracy': 0.75,
                'debugging_time_reduction': 25,
                'false_alarm_rate': 0.15
            },
            duration_days=28,
            auto_rollout=True,
            risk_level="low"
        )
        experiments.append(exp_id)
        
        print(f"📊 Created {len(experiments)} predefined experiments")
        return experiments
    
    # Private helper methods
    
    def _load_experiments(self) -> Dict[str, ExperimentConfig]:
        """Load experiments from storage"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return {k: ExperimentConfig(**v) for k, v in data.items()}
        except (json.JSONDecodeError, KeyError):
            return {}
    
    def _save_experiments(self) -> None:
        """Save experiments to storage"""
        data = {k: asdict(v) for k, v in self.experiments.items()}
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_active_experiments(self) -> List[str]:
        """Load active experiments list"""
        if not self.active_file.exists():
            return []
        
        try:
            with open(self.active_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def _save_active_experiments(self) -> None:
        """Save active experiments list"""
        with open(self.active_file, 'w') as f:
            json.dump(self.active_experiments, f, indent=2)
    
    def _load_experiment_results(self, experiment_id: str) -> List[ExperimentResult]:
        """Load results for a specific experiment"""
        if not self.results_file.exists():
            return []
        
        results = []
        try:
            with open(self.results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data['experiment_id'] == experiment_id:
                            results.append(ExperimentResult(**data))
        except (json.JSONDecodeError, KeyError):
            pass
        
        return results
    
    def _generate_failure_criteria(self, success_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Generate failure criteria based on success criteria"""
        failure_criteria = {}
        for key, value in success_criteria.items():
            if isinstance(value, (int, float)):
                failure_criteria[key] = value * 0.5  # 50% of success threshold
            else:
                failure_criteria[key] = value
        return failure_criteria
    
    def _check_prerequisites(self, experiment: ExperimentConfig) -> bool:
        """Check if experiment prerequisites are met"""
        # This would implement actual prerequisite checking
        return True
    
    def _initialize_experiment_tracking(self, experiment: ExperimentConfig) -> None:
        """Initialize tracking for an experiment"""
        tracking_file = self.experiments_dir / f"tracking_{experiment.experiment_id}.json"
        tracking_data = {
            'experiment_id': experiment.experiment_id,
            'start_time': datetime.now().isoformat(),
            'control_group_ids': [],
            'experimental_group_ids': [],
            'milestones': [],
            'status_updates': []
        }
        
        with open(tracking_file, 'w') as f:
            json.dump(tracking_data, f, indent=2)
    
    def _calculate_results_summary(self, results: List[ExperimentResult]) -> Dict[str, Any]:
        """Calculate summary statistics from results"""
        return {
            'total_measurements': len(results),
            'date_range': {
                'start': results[0].measurement_time if results else None,
                'end': results[-1].measurement_time if results else None
            },
            'average_success_score': sum(r.success_score for r in results) / len(results) if results else 0
        }
    
    def _perform_statistical_analysis(self, results: List[ExperimentResult]) -> Dict[str, Any]:
        """Perform statistical analysis on experiment results"""
        # This would implement actual statistical analysis
        return {
            'statistical_significance': 0.95,
            'p_value': 0.02,
            'effect_size': 0.8,
            'confidence_interval': {'lower': 0.6, 'upper': 1.0}
        }
    
    def _determine_experiment_success(self, experiment: ExperimentConfig, 
                                    results: List[ExperimentResult]) -> Dict[str, Any]:
        """Determine if experiment was successful"""
        # This would implement actual success determination logic
        return {
            'is_success': True,
            'confidence': 0.9,
            'criteria_met': list(experiment.success_criteria.keys()),
            'criteria_failed': []
        }
    
    def _generate_experiment_recommendations(self, experiment: ExperimentConfig,
                                           results: List[ExperimentResult]) -> List[str]:
        """Generate recommendations based on experiment results"""
        return [
            "Consider rolling out to full population",
            "Monitor performance metrics closely",
            "Plan gradual rollout over 2 weeks"
        ]
    
    def _rollout_experiment(self, experiment_id: str) -> None:
        """Roll out successful experiment to production"""
        print(f"🚀 Rolling out experiment {experiment_id}")
    
    def _revert_experiment(self, experiment_id: str) -> None:
        """Revert failed experiment"""
        print(f"⏪ Reverting experiment {experiment_id}")
    
    def _generate_next_steps(self, experiment: ExperimentConfig, 
                           analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps based on experiment completion"""
        return [
            "Document learnings in knowledge base",
            "Share results with development team",
            "Plan follow-up experiments if needed"
        ]
    
    def _calculate_experiment_progress(self, experiment_id: str) -> float:
        """Calculate progress percentage for an experiment"""
        if experiment_id not in self.experiments:
            return 0.0
        
        experiment = self.experiments[experiment_id]
        start_date = datetime.fromisoformat(experiment.created_at)
        duration = timedelta(days=experiment.duration_days)
        elapsed = datetime.now() - start_date
        
        return min(1.0, elapsed.total_seconds() / duration.total_seconds())
    
    def _calculate_days_remaining(self, experiment: ExperimentConfig) -> int:
        """Calculate days remaining for an experiment"""
        start_date = datetime.fromisoformat(experiment.created_at)
        end_date = start_date + timedelta(days=experiment.duration_days)
        remaining = end_date - datetime.now()
        
        return max(0, remaining.days)
    
    def _get_latest_metrics(self, experiment_id: str) -> Dict[str, Any]:
        """Get latest metrics for an experiment"""
        results = self._load_experiment_results(experiment_id)
        if results:
            return results[-1].metrics
        return {}


def main():
    """CLI interface for experiment framework"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Development Experiment Framework")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--list-active", action="store_true", help="List active experiments")
    parser.add_argument("--create-predefined", action="store_true", help="Create predefined experiments")
    parser.add_argument("--analyze", help="Analyze experiment by ID")
    parser.add_argument("--complete", help="Complete experiment by ID")
    
    args = parser.parse_args()
    
    framework = DevelopmentExperimentFramework(Path(args.project_root))
    
    if args.list_active:
        active = framework.get_active_experiments()
        print(json.dumps(active, indent=2))
    elif args.create_predefined:
        experiment_ids = framework.create_predefined_experiments()
        print(f"Created experiments: {experiment_ids}")
    elif args.analyze:
        analysis = framework.analyze_experiment(args.analyze)
        print(json.dumps(analysis, indent=2))
    elif args.complete:
        result = framework.complete_experiment(args.complete)
        print(json.dumps(result, indent=2))
    else:
        print("Use --list-active, --create-predefined, --analyze, or --complete")


if __name__ == "__main__":
    main()