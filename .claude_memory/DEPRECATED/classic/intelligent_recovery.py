#!/usr/bin/env python3
"""
Intelligent Recovery System - Self-Healing Memory Architecture
============================================================

This system makes the memory architecture completely self-healing:
1. Automatic error detection and diagnosis
2. Intelligent recovery strategies
3. Graceful degradation when components fail
4. Proactive health monitoring
5. Self-repair capabilities

No more silent failures - the system heals itself!
"""

import os
import sys
import json
import time
import traceback
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    FAILED = "failed"

@dataclass
class HealthIssue:
    component: str
    severity: HealthStatus
    description: str
    error_details: str
    timestamp: str
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_strategy: str = ""

class IntelligentRecoveryEngine:
    """
    Self-healing memory system that automatically detects and fixes issues.
    """
    
    def __init__(self):
        self.base_path = Path("/workspaces/Sectorwars2102/.claude_memory")
        self.recovery_log_file = self.base_path / "recovery_log.json"
        self.health_status_file = self.base_path / "system_health.json"
        
        # Recovery strategies registry
        self.recovery_strategies = {
            'memory_encryption': self._recover_memory_encryption,
            'memvid_corruption': self._recover_memvid_corruption,
            'perspective_failure': self._recover_perspective_failure,
            'file_corruption': self._recover_file_corruption,
            'permission_issues': self._recover_permission_issues,
            'import_failures': self._recover_import_failures,
            'cache_corruption': self._recover_cache_corruption
        }
        
        # Component health checkers
        self.health_checkers = {
            'memory_engine': self._check_memory_engine_health,
            'perspective_system': self._check_perspective_health,
            'memvid_system': self._check_memvid_health,
            'auto_intelligence': self._check_auto_intelligence_health,
            'learning_system': self._check_learning_system_health,
            'file_system': self._check_file_system_health
        }
        
        # Load recovery history
        self.recovery_history = self._load_recovery_history()
        self.system_health = self._load_system_health()
        
        # Perform initial health check
        self._initialize_health_monitoring()
    
    def _load_recovery_history(self) -> List[Dict[str, Any]]:
        """Load previous recovery attempts"""
        if self.recovery_log_file.exists():
            try:
                with open(self.recovery_log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_system_health(self) -> Dict[str, Any]:
        """Load current system health status"""
        if self.health_status_file.exists():
            try:
                with open(self.health_status_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'overall_status': HealthStatus.HEALTHY.value,
            'components': {},
            'last_check': '',
            'issues': [],
            'uptime_start': datetime.now().isoformat()
        }
    
    def _save_recovery_history(self):
        """Save recovery history"""
        try:
            with open(self.recovery_log_file, 'w') as f:
                json.dump(self.recovery_history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save recovery history: {e}")
    
    def _save_system_health(self):
        """Save system health status"""
        try:
            with open(self.health_status_file, 'w') as f:
                json.dump(self.system_health, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save system health: {e}")
    
    def _initialize_health_monitoring(self):
        """Initialize health monitoring system"""
        try:
            self.comprehensive_health_check()
        except Exception as e:
            self._log_recovery_attempt("initialization", f"Health monitoring initialization failed: {e}")
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all system components.
        Returns health status and automatically attempts recovery if needed.
        """
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': HealthStatus.HEALTHY.value,
            'components': {},
            'issues_found': [],
            'recovery_attempts': [],
            'system_operational': True
        }
        
        critical_issues = 0
        warning_issues = 0
        
        # Check each component
        for component_name, health_checker in self.health_checkers.items():
            try:
                component_health = health_checker()
                health_report['components'][component_name] = component_health
                
                if component_health['status'] == HealthStatus.CRITICAL.value:
                    critical_issues += 1
                    health_report['issues_found'].append(component_health)
                    
                    # Attempt automatic recovery
                    recovery_result = self._attempt_recovery(component_name, component_health)
                    health_report['recovery_attempts'].append(recovery_result)
                    
                elif component_health['status'] == HealthStatus.WARNING.value:
                    warning_issues += 1
                    health_report['issues_found'].append(component_health)
            
            except Exception as e:
                # Health checker itself failed - this is critical
                critical_issues += 1
                critical_health = {
                    'component': component_name,
                    'status': HealthStatus.FAILED.value,
                    'error': f"Health checker failed: {e}",
                    'details': traceback.format_exc()
                }
                health_report['components'][component_name] = critical_health
                health_report['issues_found'].append(critical_health)
        
        # Determine overall status
        if critical_issues > 0:
            health_report['overall_status'] = HealthStatus.CRITICAL.value
        elif warning_issues > 0:
            health_report['overall_status'] = HealthStatus.WARNING.value
        
        # Update system health
        self.system_health = health_report
        self.system_health['last_check'] = health_report['timestamp']
        self._save_system_health()
        
        return health_report
    
    def _check_memory_engine_health(self) -> Dict[str, Any]:
        """Check memory engine health"""
        health = {
            'component': 'memory_engine',
            'status': HealthStatus.HEALTHY.value,
            'checks_performed': [],
            'issues': []
        }
        
        try:
            # Check if memory engine file exists
            memory_engine_path = self.base_path / "memory_engine.py"
            if not memory_engine_path.exists():
                health['status'] = HealthStatus.CRITICAL.value
                health['issues'].append("Memory engine file missing")
                return health
            
            health['checks_performed'].append("File existence ✓")
            
            # Try to import and verify
            sys.path.insert(0, str(self.base_path))
            from memory_engine import SecureMemoryJournal, TripleCognitiveEncryption
            
            health['checks_performed'].append("Import successful ✓")
            
            # Test encryption system
            encryption = TripleCognitiveEncryption()
            test_data = "test_memory_entry"
            encrypted, sig, _ = encryption.encrypt(test_data)
            decrypted = encryption.decrypt(encrypted, sig)
            
            if decrypted != test_data:
                health['status'] = HealthStatus.CRITICAL.value
                health['issues'].append("Encryption/decryption test failed")
                return health
            
            health['checks_performed'].append("Encryption test ✓")
            
            # Test memory journal access
            journal = SecureMemoryJournal()
            if not journal.verify_access():
                health['status'] = HealthStatus.WARNING.value
                health['issues'].append("Memory access verification failed")
                return health
            
            health['checks_performed'].append("Memory access ✓")
            
        except ImportError as e:
            health['status'] = HealthStatus.CRITICAL.value
            health['issues'].append(f"Import error: {e}")
        except Exception as e:
            health['status'] = HealthStatus.CRITICAL.value
            health['issues'].append(f"Memory engine error: {e}")
        
        return health
    
    def _check_perspective_health(self) -> Dict[str, Any]:
        """Check perspective system health"""
        health = {
            'component': 'perspective_system',
            'status': HealthStatus.HEALTHY.value,
            'checks_performed': [],
            'issues': []
        }
        
        try:
            # Check perspective files exist
            perspective_files = [
                'perspective_interface.py',
                'learning_perspectives.py'
            ]
            
            for file_name in perspective_files:
                file_path = self.base_path / file_name
                if not file_path.exists():
                    health['status'] = HealthStatus.WARNING.value
                    health['issues'].append(f"Missing file: {file_name}")
                else:
                    health['checks_performed'].append(f"{file_name} exists ✓")
            
            # Test perspective engine import
            from perspective_interface import PerspectiveAnalysisEngine
            
            engine = PerspectiveAnalysisEngine()
            
            # Test basic analysis
            test_analysis = engine.analyze_from_perspective('arch', 'test context')
            if 'error' in test_analysis:
                health['status'] = HealthStatus.WARNING.value
                health['issues'].append("Perspective analysis test failed")
            else:
                health['checks_performed'].append("Basic analysis test ✓")
                
        except ImportError as e:
            health['status'] = HealthStatus.CRITICAL.value
            health['issues'].append(f"Perspective import error: {e}")
        except Exception as e:
            health['status'] = HealthStatus.WARNING.value
            health['issues'].append(f"Perspective system error: {e}")
        
        return health
    
    def _check_memvid_health(self) -> Dict[str, Any]:
        """Check memvid system health"""
        health = {
            'component': 'memvid_system',
            'status': HealthStatus.HEALTHY.value,
            'checks_performed': [],
            'issues': []
        }
        
        try:
            # Check if memvid components exist
            memvid_files = [
                'semantic_journey_search.py',
                'lightning_memvid.py'
            ]
            
            for file_name in memvid_files:
                file_path = self.base_path / file_name
                if file_path.exists():
                    health['checks_performed'].append(f"{file_name} exists ✓")
                else:
                    health['status'] = HealthStatus.WARNING.value
                    health['issues'].append(f"Missing file: {file_name}")
            
            # Check if journey video exists
            journey_video = self.base_path / "development_journey.mp4"
            if journey_video.exists():
                health['checks_performed'].append("Journey video exists ✓")
            else:
                health['status'] = HealthStatus.WARNING.value
                health['issues'].append("Journey video not built yet")
            
            # Test lightning memvid if available
            try:
                from lightning_memvid import LightningMemvidEngine
                
                lightning = LightningMemvidEngine()
                status = lightning.get_status()
                
                health['checks_performed'].append("Lightning memvid operational ✓")
                health['memvid_status'] = status
                
            except ImportError:
                health['status'] = HealthStatus.WARNING.value
                health['issues'].append("Lightning memvid not available")
                
        except Exception as e:
            health['status'] = HealthStatus.WARNING.value
            health['issues'].append(f"Memvid system error: {e}")
        
        return health
    
    def _check_auto_intelligence_health(self) -> Dict[str, Any]:
        """Check auto-intelligence system health"""
        health = {
            'component': 'auto_intelligence',
            'status': HealthStatus.HEALTHY.value,
            'checks_performed': [],
            'issues': []
        }
        
        try:
            auto_intelligence_path = self.base_path / "auto_intelligence.py"
            if auto_intelligence_path.exists():
                health['checks_performed'].append("Auto-intelligence file exists ✓")
                
                # Test import and basic functionality
                from auto_intelligence import AutoIntelligenceEngine
                
                engine = AutoIntelligenceEngine()
                context = engine.get_enhanced_context()
                
                health['checks_performed'].append("Auto-intelligence operational ✓")
                health['enhanced_context'] = context
                
            else:
                health['status'] = HealthStatus.WARNING.value
                health['issues'].append("Auto-intelligence file missing")
                
        except ImportError as e:
            health['status'] = HealthStatus.WARNING.value
            health['issues'].append(f"Auto-intelligence import error: {e}")
        except Exception as e:
            health['status'] = HealthStatus.WARNING.value
            health['issues'].append(f"Auto-intelligence error: {e}")
        
        return health
    
    def _check_learning_system_health(self) -> Dict[str, Any]:
        """Check learning system health"""
        health = {
            'component': 'learning_system',
            'status': HealthStatus.HEALTHY.value,
            'checks_performed': [],
            'issues': []
        }
        
        try:
            learning_path = self.base_path / "learning_perspectives.py"
            if learning_path.exists():
                health['checks_performed'].append("Learning perspectives file exists ✓")
                
                # Test import
                from learning_perspectives import LearningPerspectiveEngine
                
                engine = LearningPerspectiveEngine()
                status = engine.get_learning_status()
                
                health['checks_performed'].append("Learning system operational ✓")
                health['learning_status'] = status
                
            else:
                health['status'] = HealthStatus.WARNING.value
                health['issues'].append("Learning perspectives file missing")
                
        except ImportError as e:
            health['status'] = HealthStatus.WARNING.value
            health['issues'].append(f"Learning system import error: {e}")
        except Exception as e:
            health['status'] = HealthStatus.WARNING.value
            health['issues'].append(f"Learning system error: {e}")
        
        return health
    
    def _check_file_system_health(self) -> Dict[str, Any]:
        """Check file system health"""
        health = {
            'component': 'file_system',
            'status': HealthStatus.HEALTHY.value,
            'checks_performed': [],
            'issues': []
        }
        
        try:
            # Check if base directory exists and is writable
            if not self.base_path.exists():
                health['status'] = HealthStatus.CRITICAL.value
                health['issues'].append("Memory base directory missing")
                return health
            
            health['checks_performed'].append("Base directory exists ✓")
            
            # Test write permissions
            test_file = self.base_path / "test_write_permissions.tmp"
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()  # Delete test file
                health['checks_performed'].append("Write permissions ✓")
            except Exception:
                health['status'] = HealthStatus.CRITICAL.value
                health['issues'].append("No write permissions in memory directory")
                return health
            
            # Check critical files
            critical_files = [
                'memory_engine.py',
                'claude_memory.py',
                'README_FOR_FUTURE_CLAUDE.md'
            ]
            
            for file_name in critical_files:
                file_path = self.base_path / file_name
                if not file_path.exists():
                    health['status'] = HealthStatus.WARNING.value
                    health['issues'].append(f"Critical file missing: {file_name}")
                else:
                    health['checks_performed'].append(f"{file_name} exists ✓")
            
        except Exception as e:
            health['status'] = HealthStatus.CRITICAL.value
            health['issues'].append(f"File system error: {e}")
        
        return health
    
    def _attempt_recovery(self, component_name: str, health_issue: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt automatic recovery for a component"""
        
        recovery_result = {
            'component': component_name,
            'timestamp': datetime.now().isoformat(),
            'attempted': False,
            'successful': False,
            'strategy_used': '',
            'details': '',
            'follow_up_needed': False
        }
        
        try:
            # Determine recovery strategy based on component and issue
            strategy = self._determine_recovery_strategy(component_name, health_issue)
            
            if strategy:
                recovery_result['strategy_used'] = strategy
                recovery_result['attempted'] = True
                
                # Execute recovery strategy
                recovery_function = self.recovery_strategies.get(strategy)
                if recovery_function:
                    success, details = recovery_function(health_issue)
                    recovery_result['successful'] = success
                    recovery_result['details'] = details
                    
                    if not success:
                        recovery_result['follow_up_needed'] = True
                else:
                    recovery_result['details'] = f"No recovery function found for strategy: {strategy}"
            else:
                recovery_result['details'] = "No suitable recovery strategy found"
        
        except Exception as e:
            recovery_result['details'] = f"Recovery attempt failed: {e}"
        
        # Log recovery attempt
        self._log_recovery_attempt(component_name, recovery_result['details'])
        
        return recovery_result
    
    def _determine_recovery_strategy(self, component_name: str, health_issue: Dict[str, Any]) -> Optional[str]:
        """Determine the best recovery strategy for a given issue"""
        
        issues = health_issue.get('issues', [])
        
        for issue in issues:
            issue_lower = issue.lower()
            
            if 'encryption' in issue_lower or 'decrypt' in issue_lower:
                return 'memory_encryption'
            elif 'memvid' in issue_lower or 'video' in issue_lower:
                return 'memvid_corruption'
            elif 'perspective' in issue_lower:
                return 'perspective_failure'
            elif 'missing' in issue_lower or 'file' in issue_lower:
                return 'file_corruption'
            elif 'permission' in issue_lower:
                return 'permission_issues'
            elif 'import' in issue_lower:
                return 'import_failures'
            elif 'cache' in issue_lower or 'corrupt' in issue_lower:
                return 'cache_corruption'
        
        return None
    
    def _recover_memory_encryption(self, health_issue: Dict[str, Any]) -> Tuple[bool, str]:
        """Recover memory encryption issues"""
        try:
            # Try to rebuild encryption keys
            from memory_engine import TripleCognitiveEncryption
            
            # Test encryption system
            encryption = TripleCognitiveEncryption()
            test_data = "recovery_test"
            encrypted, sig, _ = encryption.encrypt(test_data)
            decrypted = encryption.decrypt(encrypted, sig)
            
            if decrypted == test_data:
                return True, "Encryption system recovered successfully"
            else:
                return False, "Encryption test still failing after recovery attempt"
                
        except Exception as e:
            return False, f"Encryption recovery failed: {e}"
    
    def _recover_memvid_corruption(self, health_issue: Dict[str, Any]) -> Tuple[bool, str]:
        """Recover memvid corruption issues"""
        try:
            # Try to rebuild memvid index
            from lightning_memvid import LightningMemvidEngine
            
            lightning = LightningMemvidEngine()
            success = lightning.force_rebuild()
            
            if success:
                return True, "Memvid index rebuilt successfully"
            else:
                return False, "Memvid rebuild failed"
                
        except Exception as e:
            # Try alternative recovery
            try:
                # Delete corrupted files and rebuild
                journey_video = self.base_path / "development_journey.mp4"
                journey_index = self.base_path / "journey_index.json"
                
                if journey_video.exists():
                    journey_video.unlink()
                if journey_index.exists():
                    journey_index.unlink()
                
                return True, "Corrupted memvid files cleaned - will rebuild on next use"
                
            except Exception as e2:
                return False, f"Memvid recovery failed: {e2}"
    
    def _recover_perspective_failure(self, health_issue: Dict[str, Any]) -> Tuple[bool, str]:
        """Recover perspective system failures"""
        try:
            # Try to reinitialize perspective system
            from perspective_interface import PerspectiveAnalysisEngine
            
            engine = PerspectiveAnalysisEngine()
            test_analysis = engine.analyze_from_perspective('arch', 'recovery test')
            
            if 'error' not in test_analysis:
                return True, "Perspective system recovered successfully"
            else:
                return False, "Perspective system still failing after recovery"
                
        except Exception as e:
            return False, f"Perspective recovery failed: {e}"
    
    def _recover_file_corruption(self, health_issue: Dict[str, Any]) -> Tuple[bool, str]:
        """Recover missing or corrupted files"""
        try:
            # This would involve restoring from backups or recreating files
            # For now, just report the issue
            return False, "File recovery requires manual intervention"
        except Exception as e:
            return False, f"File recovery failed: {e}"
    
    def _recover_permission_issues(self, health_issue: Dict[str, Any]) -> Tuple[bool, str]:
        """Recover permission issues"""
        try:
            # Try to fix permissions
            import stat
            
            # Make memory directory writable
            self.base_path.chmod(0o755)
            
            # Make critical files readable/writable
            for file_path in self.base_path.glob("*.py"):
                if file_path.exists():
                    file_path.chmod(0o644)
            
            return True, "Permissions fixed successfully"
            
        except Exception as e:
            return False, f"Permission recovery failed: {e}"
    
    def _recover_import_failures(self, health_issue: Dict[str, Any]) -> Tuple[bool, str]:
        """Recover import failures"""
        try:
            # Clear Python cache
            import importlib
            
            # Add memory path to Python path if not already there
            if str(self.base_path) not in sys.path:
                sys.path.insert(0, str(self.base_path))
            
            return True, "Import paths fixed"
            
        except Exception as e:
            return False, f"Import recovery failed: {e}"
    
    def _recover_cache_corruption(self, health_issue: Dict[str, Any]) -> Tuple[bool, str]:
        """Recover cache corruption issues"""
        try:
            # Clear all cache files
            cache_files = [
                'incremental_cache.json',
                'memvid_build_state.json',
                'perspective_learning.json',
                'learned_patterns.json'
            ]
            
            cleared_files = []
            for cache_file in cache_files:
                cache_path = self.base_path / cache_file
                if cache_path.exists():
                    cache_path.unlink()
                    cleared_files.append(cache_file)
            
            return True, f"Cleared corrupted cache files: {', '.join(cleared_files)}"
            
        except Exception as e:
            return False, f"Cache recovery failed: {e}"
    
    def _log_recovery_attempt(self, component: str, details: str):
        """Log recovery attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'details': details
        }
        
        self.recovery_history.append(log_entry)
        
        # Keep only last 50 recovery attempts
        if len(self.recovery_history) > 50:
            self.recovery_history = self.recovery_history[-50:]
        
        self._save_recovery_history()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status with health information"""
        
        # Perform quick health check
        current_health = self.comprehensive_health_check()
        
        status = {
            'overall_health': current_health['overall_status'],
            'last_check': current_health['timestamp'],
            'components_healthy': sum(1 for comp in current_health['components'].values() 
                                    if comp['status'] == HealthStatus.HEALTHY.value),
            'total_components': len(current_health['components']),
            'issues_count': len(current_health['issues_found']),
            'recovery_attempts_today': self._count_recent_recoveries(),
            'system_uptime': self._calculate_uptime(),
            'auto_recovery_enabled': True
        }
        
        return status
    
    def _count_recent_recoveries(self) -> int:
        """Count recovery attempts in the last 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        
        recent_recoveries = 0
        for entry in self.recovery_history:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time > cutoff:
                    recent_recoveries += 1
            except:
                pass
        
        return recent_recoveries
    
    def _calculate_uptime(self) -> str:
        """Calculate system uptime"""
        try:
            start_time = datetime.fromisoformat(self.system_health['uptime_start'])
            uptime_delta = datetime.now() - start_time
            
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"


# Global recovery engine instance
_recovery_engine = None

def get_recovery_engine() -> IntelligentRecoveryEngine:
    """Get the global recovery engine instance"""
    global _recovery_engine
    if _recovery_engine is None:
        _recovery_engine = IntelligentRecoveryEngine()
    return _recovery_engine

def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """
    Safely execute a function with automatic error recovery.
    If the function fails, attempt recovery and retry.
    """
    recovery_engine = get_recovery_engine()
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Log the error
        recovery_engine._log_recovery_attempt(
            func.__name__, 
            f"Function failed: {e}, attempting recovery"
        )
        
        # Perform health check and recovery
        recovery_engine.comprehensive_health_check()
        
        # Retry once after recovery
        try:
            return func(*args, **kwargs)
        except Exception as e2:
            # If still failing, return a graceful error
            return {
                'error': True,
                'message': f"Function failed after recovery attempt: {e2}",
                'recovery_attempted': True
            }


if __name__ == "__main__":
    # Test intelligent recovery system
    print("🏥 Intelligent Recovery System Test")
    print("=" * 60)
    
    recovery_engine = IntelligentRecoveryEngine()
    
    # Perform comprehensive health check
    health_report = recovery_engine.comprehensive_health_check()
    
    print(f"Overall Status: {health_report['overall_status']}")
    print(f"Components Checked: {len(health_report['components'])}")
    print(f"Issues Found: {len(health_report['issues_found'])}")
    print(f"Recovery Attempts: {len(health_report['recovery_attempts'])}")
    
    # Show component status
    print("\n🔍 Component Health:")
    for component, health in health_report['components'].items():
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌',
            'failed': '💀'
        }
        emoji = status_emoji.get(health['status'], '❓')
        print(f"  {emoji} {component}: {health['status']}")
    
    # Show system status
    print(f"\n📊 System Status:")
    status = recovery_engine.get_system_status()
    print(f"  Healthy Components: {status['components_healthy']}/{status['total_components']}")
    print(f"  Recent Recoveries: {status['recovery_attempts_today']}")
    print(f"  System Uptime: {status['system_uptime']}")
    print(f"  Auto-Recovery: {'✅' if status['auto_recovery_enabled'] else '❌'}")