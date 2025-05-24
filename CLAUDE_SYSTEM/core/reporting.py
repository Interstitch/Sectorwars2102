"""
Report Generation Module
========================

Generates comprehensive analysis reports.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ReportGenerator:
    """Generates analysis reports"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / ".claude" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, metrics: Dict, opportunities: List, 
                       patterns: Dict, healing_actions: List) -> Dict[str, Any]:
        """Generate comprehensive report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.1",
            "metrics": metrics,
            "opportunities": len(opportunities),
            "patterns": len(patterns),
            "healing_actions": len(healing_actions),
            "summary": {
                "total_opportunities": len(opportunities),
                "quality_score": self._calculate_quality_score(opportunities),
                "patterns_learned": len(patterns),
                "healing_success_rate": self._calculate_healing_success_rate(healing_actions)
            }
        }
        
        # Save report
        report_file = self.reports_dir / f"analysis-{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also save as latest
        latest_file = self.reports_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        self._display_summary(report)
        
        return report
    
    def _calculate_quality_score(self, opportunities: List) -> float:
        """Calculate quality score based on opportunities"""
        if not opportunities:
            return 100.0
        
        # Simple scoring: subtract points for each opportunity
        score = 100.0 - (len(opportunities) * 5)
        return max(0.0, min(100.0, score))
    
    def _calculate_healing_success_rate(self, healing_actions: List) -> float:
        """Calculate healing success rate"""
        if not healing_actions:
            return 100.0
        
        successful = len([a for a in healing_actions if a.get('success', False)])
        return (successful / len(healing_actions)) * 100
    
    def _display_summary(self, report: Dict[str, Any]) -> None:
        """Display report summary"""
        summary = report["summary"]
        
        print(f"📊 Quality Score: {summary['quality_score']:.1f}/100")
        print(f"🎯 Opportunities: {summary['total_opportunities']}")
        print(f"🧠 Patterns: {summary['patterns_learned']}")
        print(f"🏥 Healing Success: {summary['healing_success_rate']:.1f}%")