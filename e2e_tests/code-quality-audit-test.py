#!/usr/bin/env python3
"""
Code Quality Audit Test Suite for SectorWars 2102 I18N Implementation
Tests for TypeScript quality, error handling, and best practices
"""

import json
import re
import ast
import time
from pathlib import Path
from typing import Dict, List, Any, Set

class CodeQualityAuditTest:
    def __init__(self):
        self.test_results = []
        self.base_path = Path(__file__).parent
        
    def log_test_result(self, test_name: str, severity: str, status: str, details: str, findings: List = None):
        """Log test result with detailed findings"""
        result = {
            "test": test_name,
            "severity": severity, 
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        if findings:
            result["findings"] = findings
        self.test_results.append(result)
    
    def test_error_handling_patterns(self):
        """Test 9: Error Handling Review"""
        print("🔍 Test 9: Error Handling Patterns Analysis")
        
        error_handling_issues = []
        files_analyzed = 0
        
        # Check Python files for error handling
        python_files = [
            "services/gameserver/src/services/translation_service.py",
            "services/gameserver/src/api/routes/translation.py",
            "security-audit-test.py",
            "performance-audit-test.py"
        ]
        
        for file_path in python_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                files_analyzed += 1
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for bare except clauses
                    if re.search(r'except\s*:', content):
                        error_handling_issues.append(f"{file_path}: Contains bare except clause (catches all exceptions)")
                    
                    # Check for missing error handling in async functions
                    async_functions = re.findall(r'async def\s+(\w+)', content)
                    for func_name in async_functions:
                        func_pattern = f'async def {func_name}.*?(?=async def|class|$)'
                        func_match = re.search(func_pattern, content, re.DOTALL)
                        if func_match and 'try:' not in func_match.group(0):
                            error_handling_issues.append(f"{file_path}: Function '{func_name}' lacks error handling")
                    
                    # Check for print statements instead of logging
                    print_statements = re.findall(r'print\s*\(', content)
                    if len(print_statements) > 5:  # Allow some prints for scripts
                        error_handling_issues.append(f"{file_path}: Uses print statements instead of proper logging ({len(print_statements)} found)")
                    
                except Exception as e:
                    error_handling_issues.append(f"{file_path}: Could not analyze file - {e}")
        
        # Check TypeScript files for error handling
        ts_files = [
            "shared/i18n/config.ts",
            "services/admin-ui/src/components/common/LanguageSwitcher.tsx"
        ]
        
        for file_path in ts_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                files_analyzed += 1
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for try-catch blocks
                    try_blocks = len(re.findall(r'try\s*{', content))
                    catch_blocks = len(re.findall(r'catch\s*\(', content))
                    
                    if try_blocks != catch_blocks:
                        error_handling_issues.append(f"{file_path}: Mismatched try/catch blocks ({try_blocks} try, {catch_blocks} catch)")
                    
                    # Check for console.error usage
                    if 'console.error' not in content and 'fetch(' in content:
                        error_handling_issues.append(f"{file_path}: Network requests without proper error logging")
                    
                    # Check for empty catch blocks
                    empty_catch = re.search(r'catch\s*\([^)]*\)\s*{\s*}', content)
                    if empty_catch:
                        error_handling_issues.append(f"{file_path}: Contains empty catch block")
                        
                except Exception as e:
                    error_handling_issues.append(f"{file_path}: Could not analyze file - {e}")
        
        if error_handling_issues:
            self.log_test_result(
                "Error Handling Patterns",
                "MEDIUM",
                "FAILED",
                f"Found {len(error_handling_issues)} error handling issues in {files_analyzed} files",
                error_handling_issues
            )
            print(f"   ❌ FAILED: Found {len(error_handling_issues)} error handling issues")
            for issue in error_handling_issues[:3]:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Error Handling Patterns",
                "MEDIUM",
                "PASSED",
                f"Error handling patterns are consistent across {files_analyzed} files"
            )
            print("   ✅ PASSED: Error handling patterns are good")
    
    def test_typescript_type_safety(self):
        """Test 10: TypeScript Type Safety"""
        print("\n🔍 Test 10: TypeScript Type Safety Analysis")
        
        type_safety_issues = []
        ts_files_found = 0
        
        # Check TypeScript files for type safety
        for ts_file in self.base_path.rglob("*.ts"):
            if "node_modules" in str(ts_file):
                continue
                
            ts_files_found += 1
            try:
                with open(ts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                relative_path = str(ts_file.relative_to(self.base_path))
                
                # Check for 'any' type usage
                any_usage = len(re.findall(r':\s*any\b', content))
                if any_usage > 2:  # Allow some any usage
                    type_safety_issues.append(f"{relative_path}: Excessive 'any' type usage ({any_usage} instances)")
                
                # Check for non-null assertions (!.)
                non_null_assertions = len(re.findall(r'!\s*\.', content))
                if non_null_assertions > 3:
                    type_safety_issues.append(f"{relative_path}: Excessive non-null assertions ({non_null_assertions} instances)")
                
                # Check for missing return types on functions
                function_pattern = r'function\s+\w+\s*\([^)]*\)\s*{'
                functions_without_return_type = re.findall(function_pattern, content)
                if len(functions_without_return_type) > 0:
                    type_safety_issues.append(f"{relative_path}: Functions missing return types ({len(functions_without_return_type)} functions)")
                
                # Check for interface definitions
                if 'interface' not in content and len(content) > 1000:  # Large files should have interfaces
                    type_safety_issues.append(f"{relative_path}: Large TypeScript file without interface definitions")
                
            except Exception as e:
                type_safety_issues.append(f"{relative_path}: Could not analyze TypeScript file - {e}")
        
        # Check for .tsx files too
        for tsx_file in self.base_path.rglob("*.tsx"):
            if "node_modules" in str(tsx_file):
                continue
                
            ts_files_found += 1
            try:
                with open(tsx_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                relative_path = str(tsx_file.relative_to(self.base_path))
                
                # Check for proper React component typing
                if 'React.FC' not in content and 'const' in content and ': React.' not in content:
                    type_safety_issues.append(f"{relative_path}: React component may lack proper typing")
                
                # Check for prop interface definitions
                if 'interface' not in content and 'Props' not in content and len(content) > 500:
                    type_safety_issues.append(f"{relative_path}: React component without props interface")
                
            except Exception as e:
                type_safety_issues.append(f"{relative_path}: Could not analyze TSX file - {e}")
        
        if type_safety_issues:
            self.log_test_result(
                "TypeScript Type Safety",
                "MEDIUM",
                "FAILED",
                f"Found {len(type_safety_issues)} type safety issues in {ts_files_found} TypeScript files",
                type_safety_issues
            )
            print(f"   ❌ FAILED: Found {len(type_safety_issues)} type safety issues")
            for issue in type_safety_issues[:3]:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "TypeScript Type Safety",
                "MEDIUM",
                "PASSED",
                f"TypeScript type safety is good across {ts_files_found} files"
            )
            print("   ✅ PASSED: TypeScript type safety is solid")
    
    def test_configuration_management(self):
        """Test: Configuration Management Best Practices"""
        print("\n🔍 Test: Configuration Management Analysis")
        
        config_issues = []
        
        # Check for hardcoded values in key files
        files_to_check = [
            "shared/i18n/config.ts",
            "services/gameserver/src/core/config.py",
            "services/gameserver/src/services/translation_service.py"
        ]
        
        hardcoded_patterns = [
            (r'http://localhost:\d+', "Hardcoded localhost URL"),
            (r'https://[a-zA-Z0-9.-]+\.app\.github\.dev', "Hardcoded GitHub Codespace URL"),
            (r'postgresql://[^"\']*', "Hardcoded database URL"),
            (r'"[A-Za-z0-9]{32,}"', "Possible hardcoded secret/key"),
        ]
        
        for file_path in files_to_check:
            full_path = self.base_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern, description in hardcoded_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            config_issues.append(f"{file_path}: {description} ({len(matches)} instances)")
                    
                except Exception as e:
                    config_issues.append(f"{file_path}: Could not analyze configuration - {e}")
        
        # Check for environment variable usage
        env_files = [".env", ".env.example"]
        env_vars_defined = set()
        
        for env_file in env_files:
            env_path = self.base_path / env_file
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            if '=' in line and not line.strip().startswith('#'):
                                var_name = line.split('=')[0].strip()
                                env_vars_defined.add(var_name)
                except Exception as e:
                    config_issues.append(f"{env_file}: Could not read environment file - {e}")
        
        # Check if important config is externalized
        required_env_vars = [
            'DATABASE_URL', 'JWT_SECRET', 'SECRET_KEY', 'API_BASE_URL'
        ]
        
        missing_env_vars = [var for var in required_env_vars if var not in env_vars_defined]
        if missing_env_vars:
            config_issues.append(f"Missing environment variables: {', '.join(missing_env_vars)}")
        
        if config_issues:
            self.log_test_result(
                "Configuration Management",
                "MEDIUM",
                "FAILED",
                f"Found {len(config_issues)} configuration management issues",
                config_issues
            )
            print(f"   ❌ FAILED: Found {len(config_issues)} configuration issues")
            for issue in config_issues[:3]:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Configuration Management",
                "MEDIUM",
                "PASSED",
                "Configuration management follows best practices"
            )
            print("   ✅ PASSED: Configuration is properly externalized")
    
    def test_pluralization_implementation(self):
        """Test 11: Pluralization Support Analysis"""
        print("\n🔍 Test 11: Pluralization Support Analysis")
        
        pluralization_issues = []
        
        # Check for pluralization in translation files
        plural_patterns_found = 0
        files_with_plurals = 0
        
        for json_file in self.base_path.rglob("*.json"):
            if "i18n" not in str(json_file):
                continue
                
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                def check_pluralization(data, file_path):
                    plural_count = 0
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict):
                                plural_count += check_pluralization(value, file_path)
                            elif isinstance(value, str):
                                # Check for plural forms
                                if key.endswith('_plural') or '{{count}}' in value:
                                    plural_count += 1
                    return plural_count
                
                plurals_in_file = check_pluralization(content, str(json_file))
                if plurals_in_file > 0:
                    files_with_plurals += 1
                    plural_patterns_found += plurals_in_file
                
            except Exception as e:
                pluralization_issues.append(f"{json_file}: Could not analyze pluralization - {e}")
        
        # Check specific language requirements
        complex_plural_languages = ["ru", "ar", "zh"]  # Languages with complex pluralization
        
        for lang in complex_plural_languages:
            lang_files = list(self.base_path.rglob(f"*/{lang}/*.json")) + list(self.base_path.rglob(f"{lang}.json"))
            
            if lang_files:
                # Check if these languages have proper pluralization
                has_complex_plurals = False
                for lang_file in lang_files:
                    try:
                        with open(lang_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if '_plural' in content or 'count}}' in content:
                            has_complex_plurals = True
                            break
                    except:
                        pass
                
                if not has_complex_plurals:
                    pluralization_issues.append(f"Language '{lang}' lacks proper pluralization support")
        
        # Check i18n configuration for pluralization setup
        config_file = self.base_path / "shared" / "i18n" / "config.ts"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                if 'pluralSeparator' not in config_content:
                    pluralization_issues.append("i18n configuration missing pluralization setup")
                
            except Exception as e:
                pluralization_issues.append(f"Could not check i18n configuration - {e}")
        
        findings = [
            f"Plural patterns found: {plural_patterns_found}",
            f"Files with plurals: {files_with_plurals}",
            f"Complex languages checked: {len(complex_plural_languages)}"
        ]
        
        if pluralization_issues:
            self.log_test_result(
                "Pluralization Support",
                "MEDIUM",
                "FAILED",
                f"Found {len(pluralization_issues)} pluralization issues",
                pluralization_issues + findings
            )
            print(f"   ❌ FAILED: Found {len(pluralization_issues)} pluralization issues")
            for issue in pluralization_issues[:3]:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Pluralization Support",
                "MEDIUM", 
                "PASSED",
                "Pluralization support is implemented correctly",
                findings
            )
            print("   ✅ PASSED: Pluralization support is adequate")
        
        print(f"      📊 Plural patterns found: {plural_patterns_found}")
        print(f"      📊 Files with plurals: {files_with_plurals}")
    
    def test_rtl_language_support(self):
        """Test 12: RTL Language Support Analysis"""
        print("\n🔍 Test 12: RTL Language Support Analysis")
        
        rtl_issues = []
        
        # Check for Arabic language support
        arabic_files = list(self.base_path.rglob("ar.json")) + list(self.base_path.rglob("*/ar/*.json"))
        
        if not arabic_files:
            rtl_issues.append("No Arabic translation files found")
        else:
            # Check if Arabic files have content
            for ar_file in arabic_files:
                try:
                    with open(ar_file, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    
                    # Check for Arabic text
                    content_str = json.dumps(content, ensure_ascii=False)
                    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', content_str))
                    
                    if arabic_chars == 0:
                        rtl_issues.append(f"{ar_file}: Arabic file contains no Arabic text")
                        
                except Exception as e:
                    rtl_issues.append(f"{ar_file}: Could not analyze Arabic file - {e}")
        
        # Check i18n configuration for RTL support
        config_file = self.base_path / "shared" / "i18n" / "config.ts"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # Check for direction support
                if 'direction' not in config_content:
                    rtl_issues.append("i18n configuration missing text direction support")
                
                if 'rtl' not in config_content.lower():
                    rtl_issues.append("i18n configuration missing RTL language handling")
                
                # Check for document direction handling
                if 'document.documentElement.dir' not in config_content:
                    rtl_issues.append("Missing automatic document direction switching")
                
            except Exception as e:
                rtl_issues.append(f"Could not check RTL configuration - {e}")
        
        # Check CSS files for RTL support
        css_files = list(self.base_path.rglob("*.css"))
        rtl_css_support = False
        
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                if '[dir="rtl"]' in css_content or 'html[dir="rtl"]' in css_content:
                    rtl_css_support = True
                    break
                    
            except Exception as e:
                pass  # Ignore CSS reading errors
        
        if not rtl_css_support:
            rtl_issues.append("No RTL-specific CSS styles found")
        
        if rtl_issues:
            self.log_test_result(
                "RTL Language Support",
                "MEDIUM",
                "FAILED", 
                f"Found {len(rtl_issues)} RTL support issues",
                rtl_issues
            )
            print(f"   ❌ FAILED: Found {len(rtl_issues)} RTL support issues")
            for issue in rtl_issues[:3]:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "RTL Language Support",
                "MEDIUM",
                "PASSED",
                "RTL language support is properly implemented"
            )
            print("   ✅ PASSED: RTL support is implemented")
    
    def generate_code_quality_report(self):
        """Generate comprehensive code quality audit report"""
        print("\n" + "="*60)
        print("🏗️ CODE QUALITY AUDIT REPORT")
        print("="*60)
        
        high_severity = [r for r in self.test_results if r["severity"] == "HIGH"]
        medium_severity = [r for r in self.test_results if r["severity"] == "MEDIUM"]
        low_severity = [r for r in self.test_results if r["severity"] == "LOW"]
        
        failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]
        passed_tests = [r for r in self.test_results if r["status"] == "PASSED"]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print()
        print(f"HIGH Severity Issues: {len([r for r in high_severity if r['status'] == 'FAILED'])}")
        print(f"MEDIUM Severity Issues: {len([r for r in medium_severity if r['status'] == 'FAILED'])}")
        print(f"LOW Severity Issues: {len([r for r in low_severity if r['status'] == 'FAILED'])}")
        
        if failed_tests:
            print(f"\n❌ CODE QUALITY ISSUES:")
            for test in failed_tests:
                print(f"   [{test['severity']}] {test['test']}: {test['details']}")
                if "findings" in test and test["findings"]:
                    for finding in test["findings"][:2]:  # Show first 2 findings
                        print(f"      • {finding}")
        
        if passed_tests:
            print(f"\n✅ QUALITY STANDARDS MET:")
            for test in passed_tests:
                print(f"   [{test['severity']}] {test['test']}")
        
        # Code quality score
        total_points = len(self.test_results) * 10
        failed_points = len([r for r in high_severity if r['status'] == 'FAILED']) * 10
        failed_points += len([r for r in medium_severity if r['status'] == 'FAILED']) * 5
        failed_points += len([r for r in low_severity if r['status'] == 'FAILED']) * 2
        
        quality_score = max(0, total_points - failed_points) / total_points * 100
        
        print(f"\n🏆 CODE QUALITY SCORE: {quality_score:.1f}%")
        
        if quality_score >= 90:
            print("🌟 EXCELLENT: Code quality meets high standards")
        elif quality_score >= 75:
            print("✅ GOOD: Code quality is solid with minor improvements needed")
        elif quality_score >= 60:
            print("⚠️  FAIR: Code quality needs attention")
        else:
            print("❌ POOR: Code quality requires significant improvement")

def main():
    """Run the code quality audit"""
    import time
    
    print("🏗️ STARTING CODE QUALITY AUDIT FOR SECTORWARS 2102 I18N IMPLEMENTATION")
    print("="*75)
    
    auditor = CodeQualityAuditTest()
    
    # Run all code quality tests
    auditor.test_error_handling_patterns()
    auditor.test_typescript_type_safety()
    auditor.test_configuration_management()
    auditor.test_pluralization_implementation()
    auditor.test_rtl_language_support()
    
    # Generate final report
    auditor.generate_code_quality_report()

if __name__ == "__main__":
    main()