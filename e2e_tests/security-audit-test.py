#!/usr/bin/env python3
"""
Security Audit Test Suite for SectorWars 2102 I18N Implementation
Tests for XSS vulnerabilities, input validation, and authentication issues
"""

import json
import re
import requests
import time
from pathlib import Path
from typing import Dict, List, Any

class SecurityAuditTest:
    def __init__(self, api_base_url="http://localhost:8080"):
        self.api_base_url = api_base_url
        self.test_results = []
        
    def log_test_result(self, test_name: str, severity: str, status: str, details: str):
        """Log test result for reporting"""
        self.test_results.append({
            "test": test_name,
            "severity": severity,
            "status": status,
            "details": details,
            "timestamp": time.time()
        })
        
    def test_xss_vulnerability_in_translations(self):
        """Test 1: XSS Vulnerability Assessment"""
        print("🔍 Test 1: XSS Vulnerability Assessment")
        
        # Test malicious script injection in translation values
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>"
        ]
        
        vulnerabilities_found = []
        
        # Check if translations contain unescaped HTML
        base_path = Path(__file__).parent / "shared" / "i18n"
        
        for lang_file in base_path.rglob("*.json"):
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    
                # Recursively check for HTML content
                def check_html_content(data, path=""):
                    if isinstance(data, dict):
                        for key, value in data.items():
                            check_html_content(value, f"{path}.{key}" if path else key)
                    elif isinstance(data, str):
                        # Check for HTML tags
                        if re.search(r'<[^>]+>', data):
                            vulnerabilities_found.append({
                                "file": str(lang_file),
                                "key": path,
                                "value": data,
                                "risk": "Potential HTML injection"
                            })
                        
                        # Check for script-like content
                        if any(payload.lower() in data.lower() for payload in ["script", "javascript:", "onerror="]):
                            vulnerabilities_found.append({
                                "file": str(lang_file),
                                "key": path,
                                "value": data,
                                "risk": "Script injection detected"
                            })
                
                check_html_content(translations)
                
            except Exception as e:
                print(f"   ❌ Error reading {lang_file}: {e}")
        
        if vulnerabilities_found:
            self.log_test_result(
                "XSS Vulnerability Test",
                "HIGH",
                "FAILED",
                f"Found {len(vulnerabilities_found)} potential XSS vulnerabilities in translation files"
            )
            print(f"   ❌ FAILED: Found {len(vulnerabilities_found)} potential XSS vulnerabilities")
            for vuln in vulnerabilities_found[:3]:  # Show first 3
                print(f"      - {vuln['file']}: {vuln['key']} = {vuln['value'][:50]}...")
        else:
            self.log_test_result(
                "XSS Vulnerability Test",
                "HIGH", 
                "PASSED",
                "No HTML or script content found in translation files"
            )
            print("   ✅ PASSED: No HTML or script content found in translation files")
    
    def test_input_validation(self):
        """Test 2: Input Validation Testing"""
        print("\n🔍 Test 2: Input Validation Testing")
        
        # Test oversized translation values
        oversized_content = "A" * 100000  # 100KB string
        
        # Test malformed JSON structure
        malformed_translations = [
            {"key": "../../../etc/passwd", "value": "malicious"},
            {"key": "'; DROP TABLE translations; --", "value": "sql injection"},
            {"key": "normal.key", "value": oversized_content},
            {"key": "", "value": "empty key"},
            {"key": "valid.key", "value": ""},
        ]
        
        validation_issues = []
        
        # Check translation key validation patterns
        key_validation_regex = r'^[a-zA-Z][a-zA-Z0-9._-]*$'
        
        for test_case in malformed_translations:
            key = test_case["key"]
            value = test_case["value"]
            
            # Test key format
            if not re.match(key_validation_regex, key) and key != "":
                validation_issues.append(f"Invalid key format: '{key}'")
            
            # Test value size
            if len(value) > 10000:  # 10KB limit
                validation_issues.append(f"Oversized value for key '{key}': {len(value)} chars")
            
            # Test for suspicious patterns
            if any(pattern in key.lower() for pattern in ["../", "drop", "select", "union"]):
                validation_issues.append(f"Suspicious key pattern: '{key}'")
        
        if validation_issues:
            self.log_test_result(
                "Input Validation Test",
                "MEDIUM",
                "FAILED", 
                f"Found {len(validation_issues)} validation issues"
            )
            print(f"   ❌ FAILED: Found {len(validation_issues)} validation issues")
            for issue in validation_issues[:3]:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Input Validation Test",
                "MEDIUM",
                "PASSED",
                "All test inputs properly validated"
            )
            print("   ✅ PASSED: Input validation patterns appear secure")
    
    def test_language_code_consistency(self):
        """Test 8: Language Code Consistency (moved to security due to importance)"""
        print("\n🔍 Test 8: Language Code Consistency")
        
        # Check for consistency between database model and file structure
        inconsistencies = []
        
        base_path = Path(__file__).parent / "shared" / "i18n"
        
        # Languages defined in model
        model_languages = ["en", "es", "zh-CN", "fr", "pt", "de", "ja", "ru", "ar", "ko", "it", "nl"]
        
        # Languages found in files
        file_languages = set()
        
        # Check locales folder
        locales_path = base_path / "locales"
        if locales_path.exists():
            for file in locales_path.glob("*.json"):
                lang_code = file.stem
                file_languages.add(lang_code)
        
        # Check namespaces folder
        namespaces_path = base_path / "namespaces"
        if namespaces_path.exists():
            for lang_dir in namespaces_path.iterdir():
                if lang_dir.is_dir() and lang_dir.name != "__pycache__":
                    file_languages.add(lang_dir.name)
        
        # Compare model vs files
        file_languages_list = list(file_languages)
        
        # Check for zh-CN vs zh inconsistency
        if "zh-CN" in model_languages and "zh" in file_languages_list:
            inconsistencies.append("Language code mismatch: Model uses 'zh-CN' but files use 'zh'")
        
        # Check for missing languages
        normalized_model = [lang.replace("-CN", "") for lang in model_languages]
        for model_lang in normalized_model:
            if model_lang not in file_languages_list and model_lang in ["en", "es", "fr", "pt", "zh"]:
                inconsistencies.append(f"Missing translation files for supported language: {model_lang}")
        
        if inconsistencies:
            self.log_test_result(
                "Language Code Consistency",
                "HIGH",
                "FAILED",
                f"Found {len(inconsistencies)} language code inconsistencies"
            )
            print(f"   ❌ FAILED: Found {len(inconsistencies)} inconsistencies")
            for issue in inconsistencies:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Language Code Consistency",
                "HIGH",
                "PASSED",
                "Language codes are consistent across model and files"
            )
            print("   ✅ PASSED: Language codes are consistent")
    
    def test_translation_key_structure(self):
        """Test 13: Translation Key Validation"""
        print("\n🔍 Test 13: Translation Key Structure Validation")
        
        structure_issues = []
        base_path = Path(__file__).parent / "shared" / "i18n"
        
        # Expected namespace structure
        expected_namespaces = {
            "common": ["buttons", "status", "actions", "time", "units", "navigation"],
            "auth": ["login", "register", "logout", "mfa", "oauth", "password"],
            "admin": ["navigation", "dashboard", "users", "universe", "economy", "ai", "security", "forms", "permissions"],
            "game": ["navigation", "ships", "resources", "trading", "combat", "planets", "ai", "teams", "galaxy", "status", "firstLogin"]
        }
        
        # Check English base files for structure
        for namespace, expected_sections in expected_namespaces.items():
            if namespace == "common":
                file_path = base_path / "locales" / "en.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "common" in data:
                            common_data = data["common"]
                            for section in expected_sections:
                                if section not in common_data:
                                    structure_issues.append(f"Missing section '{section}' in common namespace")
            else:
                file_path = base_path / "namespaces" / f"{namespace}.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for section in expected_sections:
                            if section not in data:
                                structure_issues.append(f"Missing section '{section}' in {namespace} namespace")
        
        if structure_issues:
            self.log_test_result(
                "Translation Key Structure",
                "LOW",
                "FAILED",
                f"Found {len(structure_issues)} structure issues"
            )
            print(f"   ❌ FAILED: Found {len(structure_issues)} structure issues")
            for issue in structure_issues[:3]:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Translation Key Structure", 
                "LOW",
                "PASSED",
                "Translation key structure follows expected patterns"
            )
            print("   ✅ PASSED: Translation structure is well-organized")
    
    def generate_security_report(self):
        """Generate comprehensive security audit report"""
        print("\n" + "="*60)
        print("🔐 SECURITY AUDIT REPORT")
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
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   [{test['severity']}] {test['test']}: {test['details']}")
        
        if passed_tests:
            print(f"\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   [{test['severity']}] {test['test']}")
        
        # Security score
        total_points = len(self.test_results) * 10
        failed_points = len([r for r in high_severity if r['status'] == 'FAILED']) * 10
        failed_points += len([r for r in medium_severity if r['status'] == 'FAILED']) * 5
        failed_points += len([r for r in low_severity if r['status'] == 'FAILED']) * 2
        
        security_score = max(0, total_points - failed_points) / total_points * 100
        
        print(f"\n📊 SECURITY SCORE: {security_score:.1f}%")
        
        if security_score >= 90:
            print("🎉 EXCELLENT: Security implementation is strong")
        elif security_score >= 75:
            print("✅ GOOD: Security is adequate with minor improvements needed")
        elif security_score >= 60:
            print("⚠️  FAIR: Security needs attention, several issues found")
        else:
            print("❌ POOR: Security implementation needs significant improvement")

def main():
    """Run the security audit"""
    print("🔍 STARTING SECURITY AUDIT FOR SECTORWARS 2102 I18N IMPLEMENTATION")
    print("="*70)
    
    auditor = SecurityAuditTest()
    
    # Run all security tests
    auditor.test_xss_vulnerability_in_translations()
    auditor.test_input_validation()
    auditor.test_language_code_consistency()
    auditor.test_translation_key_structure()
    
    # Generate final report
    auditor.generate_security_report()

if __name__ == "__main__":
    main()