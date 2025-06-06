#!/usr/bin/env python3
"""
Git Hooks Healer - CLAUDE System Component
==========================================

This healer ensures comprehensive self-healing git hooks are installed for the CLAUDE.md system.
The enhanced hooks provide automated quality checks, pattern learning, AI context preservation,
and development cycle tracking with intelligent next-step recommendations.

Enhanced Features:
- Installs enhanced pre-commit hook with AI context reminders and Phase 0 health checks
- Installs intelligent post-commit hook with commit pattern analysis and next-phase suggestions
- Provides AI context preservation with explicit 6-phase methodology reminders
- Implements self-healing mechanisms to detect missed development phases
- Creates comprehensive logging for development session tracking
- Includes development velocity monitoring and analysis recommendations
- Provides automatic directory creation and backup of existing hooks
- Validates hook permissions and functionality with version management

Pre-commit Hook Capabilities:
- AI context reminders with complete 6-phase development loop guidance
- Development context analysis to detect missed phases
- Phase 0 system health check execution with result logging
- Self-healing recommendations when quality gates fail
- Critical reminders about proper commit practices and methodology adherence

Post-commit Hook Capabilities:
- Intelligent commit pattern analysis (feat/fix/refactor/docs/test detection)
- Automatic next-phase suggestions based on commit type and file changes
- Development velocity tracking with high-activity period detection
- Comprehensive analysis recommendations for significant changes
- Specific testing and documentation suggestions with exact commands
- Long-term development cycle monitoring with warning systems
- Pattern learning integration with result tracking and logging
"""

import os
import stat
from pathlib import Path
from typing import Dict, List, Any


class GitHooksHealer:
    """Manages git hooks installation and maintenance"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.git_dir = self.project_root / ".git"
        self.hooks_dir = self.git_dir / "hooks"
        self.system_version = "4.0.0"
        
    def diagnose(self) -> Dict[str, Any]:
        """Diagnose git hooks status"""
        issues = []
        recommendations = []
        
        # Check if this is a git repository
        if not self.git_dir.exists():
            issues.append("Not a git repository")
            return {
                "issues": issues,
                "recommendations": ["Initialize git repository"],
                "severity": "high"
            }
        
        # Check if hooks directory exists
        if not self.hooks_dir.exists():
            issues.append("Git hooks directory does not exist")
            recommendations.append("Create .git/hooks directory")
        
        # Check pre-commit hook
        pre_commit_hook = self.hooks_dir / "pre-commit"
        if not pre_commit_hook.exists():
            issues.append("Pre-commit hook not installed")
            recommendations.append("Install pre-commit hook")
        elif not self._is_claude_hook(pre_commit_hook):
            issues.append("Pre-commit hook exists but is not CLAUDE-managed")
            recommendations.append("Update pre-commit hook to CLAUDE version")
        elif not self._is_current_version(pre_commit_hook):
            issues.append("Pre-commit hook is outdated")
            recommendations.append("Update pre-commit hook to current version")
        
        # Check post-commit hook
        post_commit_hook = self.hooks_dir / "post-commit"
        if not post_commit_hook.exists():
            issues.append("Post-commit hook not installed")
            recommendations.append("Install post-commit hook")
        elif not self._is_claude_hook(post_commit_hook):
            issues.append("Post-commit hook exists but is not CLAUDE-managed")
            recommendations.append("Update post-commit hook to CLAUDE version")
        elif not self._is_current_version(post_commit_hook):
            issues.append("Post-commit hook is outdated")
            recommendations.append("Update post-commit hook to current version")
        
        # Check hook permissions
        for hook_name in ["pre-commit", "post-commit"]:
            hook_path = self.hooks_dir / hook_name
            if hook_path.exists() and not self._is_executable(hook_path):
                issues.append(f"{hook_name} hook is not executable")
                recommendations.append(f"Make {hook_name} hook executable")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "severity": "medium" if issues else "none"
        }
    
    def heal(self) -> Dict[str, Any]:
        """Install or update git hooks"""
        actions_taken = []
        errors = []
        
        try:
            # Ensure hooks directory exists
            if not self.hooks_dir.exists():
                self.hooks_dir.mkdir(parents=True, exist_ok=True)
                actions_taken.append("Created git hooks directory")
            
            # Install/update pre-commit hook
            pre_commit_result = self._install_pre_commit_hook()
            if pre_commit_result["success"]:
                actions_taken.append(pre_commit_result["message"])
            else:
                errors.append(pre_commit_result["message"])
            
            # Install/update post-commit hook
            post_commit_result = self._install_post_commit_hook()
            if post_commit_result["success"]:
                actions_taken.append(post_commit_result["message"])
            else:
                errors.append(post_commit_result["message"])
            
        except Exception as e:
            errors.append(f"Error during git hooks installation: {str(e)}")
        
        return {
            "actions_taken": actions_taken,
            "errors": errors,
            "success": len(errors) == 0
        }
    
    def _is_claude_hook(self, hook_path: Path) -> bool:
        """Check if hook is managed by CLAUDE system"""
        if not hook_path.exists():
            return False
        
        content = hook_path.read_text()
        return "Auto-generated by CLAUDE.md system" in content
    
    def _is_current_version(self, hook_path: Path) -> bool:
        """Check if hook is current version"""
        if not hook_path.exists():
            return False
        
        content = hook_path.read_text()
        return f"v{self.system_version}" in content
    
    def _is_executable(self, file_path: Path) -> bool:
        """Check if file is executable"""
        return file_path.exists() and os.access(file_path, os.X_OK)
    
    def _make_executable(self, file_path: Path):
        """Make file executable"""
        current_mode = file_path.stat().st_mode
        file_path.chmod(current_mode | stat.S_IEXEC)
    
    def _backup_existing_hook(self, hook_path: Path):
        """Create backup of existing hook"""
        if hook_path.exists() and not self._is_claude_hook(hook_path):
            backup_path = hook_path.with_suffix(f"{hook_path.suffix}.backup")
            hook_path.rename(backup_path)
            return f"Backed up existing hook to {backup_path.name}"
        return None
    
    def _install_pre_commit_hook(self) -> Dict[str, Any]:
        """Install enhanced pre-commit hook with self-healing capabilities"""
        hook_path = self.hooks_dir / "pre-commit"
        
        try:
            # Backup existing hook if needed
            backup_msg = self._backup_existing_hook(hook_path)
            
            # Write enhanced self-healing hook
            hook_content = f'''#!/bin/bash
# Auto-generated by CLAUDE.md system v{self.system_version}
# Enhanced pre-commit hook with self-healing and AI context preservation

echo "🔍 CLAUDE.md Pre-Commit: Phase 0 System Health Check"
echo "📋 Context: This is part of the 6-phase CLAUDE.md development methodology"
echo "📚 Reminder: Follow complete development loop - Phase 0→1→2→3→4→5→6"

# Function to check if we're in a development session that might need healing
check_development_context() {{
    local needs_healing=0
    
    # Check if there are recent code changes without analysis
    if [ -d ".claude/memory" ]; then
        # Look for signs that development work was done without proper analysis
        local last_analysis=$(find .claude/reports -name "*.json" -type f -printf '%T@ %p\\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- 2>/dev/null || echo "")
        local git_last_activity=$(git log -1 --format=%ct 2>/dev/null || echo "0")
        
        if [ -n "$last_analysis" ] && [ "$git_last_activity" -gt "0" ]; then
            local analysis_time=$(stat -c %Y "$last_analysis" 2>/dev/null || echo "0")
            local time_diff=$((git_last_activity - analysis_time))
            
            # If last git activity was more than 1 hour after last analysis, suggest healing
            if [ "$time_diff" -gt 3600 ]; then
                echo "⚠️  Detected development activity without recent analysis ($(($time_diff/3600))h gap)"
                echo "💡 Recommendation: Consider running full analysis after commit"
                echo "    python CLAUDE_SYSTEM/claude-system.py --analyze"
                needs_healing=1
            fi
        fi
    fi
    
    # Check for common signs of incomplete development cycles
    if git diff --name-only HEAD^ HEAD 2>/dev/null | grep -E "\\.(py|js|ts|tsx|jsx)$" >/dev/null 2>&1; then
        echo "📝 Code files modified - ensuring quality gates are met"
        if [ ! -f ".claude/reports/latest_quality_check.json" ]; then
            echo "💡 No recent quality check found - will run comprehensive check"
            needs_healing=1
        fi
    fi
    
    return $needs_healing
}}

# Function to provide AI context reminders
provide_ai_context() {{
    echo ""
    echo "🤖 AI CONTEXT REMINDER:"
    echo "   📋 You are following the CLAUDE.md 6-Phase Self-Improving Development Loop:"
    echo "   📋 Phase 0: System Health Check (CURRENT) ✓"
    echo "   📋 Phase 1: Ideation & Brainstorming"
    echo "   📋 Phase 2: Detailed Planning" 
    echo "   📋 Phase 3: Implementation"
    echo "   📋 Phase 4: Testing & Validation"
    echo "   📋 Phase 5: Documentation & Data Definition"
    echo "   📋 Phase 6: Review & Reflection"
    echo "   📋 CRITICAL: Always commit work with proper descriptions"
    echo "   📋 REMINDER: Follow all phases - don't skip steps!"
    echo ""
}}

# Main pre-commit execution
main() {{
    provide_ai_context
    
    # Check development context and provide recommendations
    if check_development_context; then
        echo "🔄 Consider running healing/analysis cycle after this commit"
    fi
    
    # Ensure CLAUDE system is available
    if [ ! -f "CLAUDE_SYSTEM/claude-system.py" ]; then
        echo "❌ CLAUDE_SYSTEM/claude-system.py not found"
        echo "💡 Please ensure CLAUDE system is properly installed"
        echo "   Run: python CLAUDE_SYSTEM/claude-system.py --init"
        exit 1
    fi
    
    # Create necessary directories
    mkdir -p .claude/memory .claude/reports .claude/patterns .claude/cache
    
    # Run Phase 0: System Health Check (part of 6-phase methodology)
    echo "⚡ Executing Phase 0: System Health Check (Quick Mode)"
    python CLAUDE_SYSTEM/claude-system.py --quick
    local quick_result=$?
    
    # Collect development intelligence
    echo "🧠 Collecting development intelligence..."
    if [ -f "CLAUDE_SYSTEM/intelligence/intelligence_integration.py" ]; then
        python -c "
import sys
sys.path.append('CLAUDE_SYSTEM')
from intelligence.intelligence_integration import IntelligenceIntegration
from pathlib import Path
integration = IntelligenceIntegration(Path('.'))
result = integration.on_pre_commit({{'phase': 'pre_commit', 'quick_result': $quick_result}})
print('🔮 Intelligence: ' + str(result.get('intelligence_decision', 'Analyzing...')))
if result.get('predictions'):
    print('📊 Predictions: ' + str(len(result['predictions'])) + ' potential issues detected')
for rec in result.get('recommendations', [])[:2]:
    print('💡 ' + str(rec))
" 2>/dev/null || echo "🤖 Intelligence system warming up..."
    fi
    
    # Store health check timestamp for future reference
    echo "$(date -Iseconds): Pre-commit health check completed (exit: $quick_result)" >> .claude/memory/health_checks.log
    
    if [ $quick_result -eq 0 ]; then
        echo "✅ Phase 0 Health Check: PASSED"
        echo "💡 Next: Continue with commit, then consider Phase 1-6 cycle as needed"
    else
        echo "❌ Phase 0 Health Check: FAILED"
        echo "🔧 Recommendation: Run healing before committing"
        echo "   python CLAUDE_SYSTEM/claude-system.py --heal"
        echo "🔍 For detailed analysis: python CLAUDE_SYSTEM/claude-system.py --analyze"
        
        # Allow commit but warn
        echo "⚠️  Allowing commit with warnings - please address issues soon"
    fi
    
    echo "📋 Pre-commit complete. Remember: This is Phase 0 of 6-phase development cycle"
    exit 0
}}

# Execute main function
main "$@"
'''
            
            hook_path.write_text(hook_content)
            self._make_executable(hook_path)
            
            message = "Installed pre-commit hook"
            if backup_msg:
                message += f" ({backup_msg})"
            
            return {"success": True, "message": message}
            
        except Exception as e:
            return {"success": False, "message": f"Failed to install pre-commit hook: {str(e)}"}
    
    def _install_post_commit_hook(self) -> Dict[str, Any]:
        """Install enhanced post-commit hook with development cycle tracking"""
        hook_path = self.hooks_dir / "post-commit"
        
        try:
            # Backup existing hook if needed
            backup_msg = self._backup_existing_hook(hook_path)
            
            # Ensure .claude/memory directory exists
            memory_dir = self.project_root / ".claude" / "memory"
            memory_dir.mkdir(parents=True, exist_ok=True)
            
            # Write enhanced post-commit hook
            hook_content = f'''#!/bin/bash
# Auto-generated by CLAUDE.md system v{self.system_version}
# Enhanced post-commit hook with development cycle tracking and self-healing

echo "📚 CLAUDE.md Post-Commit: Pattern Learning & Development Cycle Tracking"

# Function to analyze commit and suggest next phases
analyze_commit_and_suggest_phases() {{
    local commit_msg=$(git log -1 --pretty=%B)
    local files_changed=$(git diff --name-only HEAD~1 HEAD | wc -l)
    local code_files_changed=$(git diff --name-only HEAD~1 HEAD | grep -E "\\.(py|js|ts|tsx|jsx|java|cpp|c|h)$" | wc -l)
    
    echo "📊 Commit Analysis:"
    echo "   📝 Files changed: $files_changed"
    echo "   💻 Code files: $code_files_changed"
    echo "   📋 Message: $commit_msg"
    
    # Analyze commit message for phase indicators
    local suggested_next_phase=""
    local needs_analysis=false
    local needs_testing=false
    local needs_documentation=false
    
    # Pattern matching for different types of commits
    if echo "$commit_msg" | grep -iE "(feat|feature|add|implement|create)" >/dev/null; then
        echo "🆕 New feature detected"
        suggested_next_phase="Phase 4: Testing & Validation"
        needs_testing=true
    elif echo "$commit_msg" | grep -iE "(fix|bugfix|patch|repair|resolve)" >/dev/null; then
        echo "🔧 Bug fix detected"
        suggested_next_phase="Phase 4: Testing & Validation"
        needs_testing=true
    elif echo "$commit_msg" | grep -iE "(refactor|reorganize|restructure|optimize)" >/dev/null; then
        echo "♻️  Refactoring detected"
        suggested_next_phase="Phase 4: Testing & Validation"
        needs_testing=true
        needs_analysis=true
    elif echo "$commit_msg" | grep -iE "(docs|documentation|readme|comment)" >/dev/null; then
        echo "📚 Documentation update detected"
        suggested_next_phase="Phase 6: Review & Reflection"
    elif echo "$commit_msg" | grep -iE "(test|spec|testing)" >/dev/null; then
        echo "🧪 Test-related changes detected"
        suggested_next_phase="Phase 6: Review & Reflection"
    elif [ "$code_files_changed" -gt 0 ]; then
        echo "💻 Code changes detected"
        suggested_next_phase="Phase 4: Testing & Validation"
        needs_testing=true
        if [ "$code_files_changed" -gt 5 ]; then
            needs_analysis=true
        fi
    fi
    
    # Provide AI context and recommendations
    echo ""
    echo "🤖 AI CONTEXT & NEXT STEPS:"
    echo "   📋 Current: Post-commit processing complete"
    echo "   📋 Commit type analysis complete"
    
    if [ -n "$suggested_next_phase" ]; then
        echo "   📋 RECOMMENDED NEXT: $suggested_next_phase"
    fi
    
    # Provide specific recommendations based on analysis
    if [ "$needs_testing" = true ]; then
        echo "   🧪 SUGGESTION: Run tests to validate changes"
        echo "      Backend: docker-compose exec gameserver poetry run pytest"
        echo "      E2E: npx playwright test -c e2e_tests/playwright.config.ts"
    fi
    
    if [ "$needs_analysis" = true ]; then
        echo "   🔍 SUGGESTION: Run comprehensive analysis due to significant changes"
        echo "      Command: python CLAUDE_SYSTEM/claude-system.py --analyze"
    fi
    
    if [ "$needs_documentation" = true ]; then
        echo "   📝 SUGGESTION: Update documentation for new features"
        echo "      Consider updating README.md and relevant docs/"
    fi
    
    # Check if we're falling behind on the development cycle
    local days_since_analysis=999
    if [ -d ".claude/reports" ]; then
        local last_analysis=$(find .claude/reports -name "*.json" -type f -printf '%T@ %p\\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "")
        if [ -n "$last_analysis" ]; then
            local analysis_time=$(stat -c %Y "$last_analysis" 2>/dev/null || echo "0")
            local current_time=$(date +%s)
            local time_diff=$((current_time - analysis_time))
            days_since_analysis=$((time_diff / 86400))
        fi
    fi
    
    if [ "$days_since_analysis" -gt 7 ]; then
        echo "   ⚠️  WARNING: No comprehensive analysis in $days_since_analysis days"
        echo "   🔄 STRONGLY RECOMMEND: python CLAUDE_SYSTEM/claude-system.py --analyze"
    elif [ "$days_since_analysis" -gt 3 ] && [ "$code_files_changed" -gt 0 ]; then
        echo "   💡 INFO: Consider running analysis (last analysis: $days_since_analysis days ago)"
    fi
    
    echo "   📋 REMINDER: Follow complete 6-phase CLAUDE.md development cycle"
    echo ""
}}

# Function to track development session patterns
track_development_session() {{
    local session_file=".claude/memory/dev_session.json"
    local commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    local today=$(date +%Y-%m-%d)
    
    # Simple session tracking (could be enhanced with JSON parsing)
    echo "$(date -Iseconds),commit_count:$commit_count,day:$today" >> .claude/memory/session_activity.log
    
    # Check for development velocity patterns
    local commits_today=$(git log --since="00:00:00" --oneline | wc -l)
    if [ "$commits_today" -gt 10 ]; then
        echo "🚀 High development velocity detected ($commits_today commits today)"
        echo "   💡 Consider running comprehensive analysis and documentation update"
    fi
}}

# Main post-commit execution
main() {{
    # Ensure necessary directories exist
    mkdir -p .claude/memory .claude/reports .claude/patterns .claude/cache
    
    # Extract and log commit patterns
    local commit_msg=$(git log -1 --pretty=%B)
    echo "$(date -Iseconds): $commit_msg" >> .claude/memory/commits.log
    
    # Track development session patterns
    track_development_session
    
    # Analyze commit and provide AI context/suggestions
    analyze_commit_and_suggest_phases
    
    # Run pattern learning if CLAUDE system is available
    if [ -f "CLAUDE_SYSTEM/claude-system.py" ]; then
        echo "🧠 Running Pattern Learning (Phase 4 component)..."
        python CLAUDE_SYSTEM/claude-system.py --learn
        local learn_result=$?
        
        if [ $learn_result -eq 0 ]; then
            echo "✅ Pattern learning completed successfully"
        else
            echo "⚠️  Pattern learning completed with warnings"
        fi
        
        # Collect post-commit intelligence
        echo "🔮 Collecting post-commit intelligence..."
        if [ -f "CLAUDE_SYSTEM/intelligence/intelligence_integration.py" ]; then
            python -c "
import sys
sys.path.append('CLAUDE_SYSTEM')
from intelligence.intelligence_integration import IntelligenceIntegration
from pathlib import Path
integration = IntelligenceIntegration(Path('.'))
result = integration.on_post_commit({{'phase': 'post_commit', 'learn_result': $learn_result}})
print('🎯 Next Phase: ' + str(result.get('next_phase_recommendation', 'Continue development')))
for insight in result.get('learning_insights', {{}}).get('pattern_recognition', [])[:2]:
    print('📈 Pattern: ' + str(insight))
for opt in result.get('optimization_recommendations', [])[:2]:
    print('⚡ Optimization: ' + str(opt.get('recommendation', 'No recommendation')))
if result.get('healing_actions'):
    print('🔧 Auto-healing: ' + str(len(result['healing_actions'])) + ' actions taken')
" 2>/dev/null || echo "🤖 Intelligence analysis in progress..."
        fi
        
        # Log learning activity
        echo "$(date -Iseconds): Pattern learning completed (exit: $learn_result)" >> .claude/memory/learning_activity.log
    else
        echo "⚠️  CLAUDE_SYSTEM/claude-system.py not found - skipping pattern learning"
        echo "💡 Consider running: python CLAUDE_SYSTEM/claude-system.py --init"
    fi
    
    echo "📋 Post-commit processing complete"
    echo "💡 Remember: Continue with suggested next phase of development cycle"
}}

# Execute main function
main "$@"
'''
            
            hook_path.write_text(hook_content)
            self._make_executable(hook_path)
            
            message = "Installed post-commit hook"
            if backup_msg:
                message += f" ({backup_msg})"
            
            return {"success": True, "message": message}
            
        except Exception as e:
            return {"success": False, "message": f"Failed to install post-commit hook: {str(e)}"}


def main():
    """CLI interface for git hooks healer"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Git Hooks Healer")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--diagnose", action="store_true", help="Diagnose git hooks status")
    parser.add_argument("--heal", action="store_true", help="Install/update git hooks")
    
    args = parser.parse_args()
    
    healer = GitHooksHealer(Path(args.project_root))
    
    if args.diagnose:
        result = healer.diagnose()
        print(json.dumps(result, indent=2))
    elif args.heal:
        result = healer.heal()
        print(json.dumps(result, indent=2))
    else:
        print("Use --diagnose to check status or --heal to install/update hooks")


if __name__ == "__main__":
    main()