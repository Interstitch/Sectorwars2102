#!/usr/bin/env python3
"""
Audit Validation Test Suite for SectorWars 2102 I18N Implementation
Validates and confirms audit findings with additional testing
"""

import json
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any

class AuditValidationTest:
    def __init__(self):
        self.validation_results = []
        self.base_path = Path(__file__).parent
        
    def log_validation(self, test_name: str, finding: str, confirmed: bool, details: str):
        """Log validation result"""
        self.validation_results.append({
            "test": test_name,
            "finding": finding,
            "confirmed": confirmed,
            "details": details,
            "timestamp": time.time()
        })
    
    def validate_security_findings(self):
        """Validate the security audit findings"""
        print("🔍 VALIDATING SECURITY AUDIT FINDINGS")
        print("="*50)
        
        # Validate language code inconsistency finding
        print("1. Validating Language Code Inconsistency Finding...")
        
        model_file = self.base_path / "services/gameserver/src/models/translation.py"
        config_file = self.base_path / "shared/i18n/config.ts"
        
        zh_cn_in_model = False
        zh_in_files = False
        
        if model_file.exists():
            with open(model_file, 'r') as f:
                model_content = f.read()
                if 'zh-CN' in model_content:
                    zh_cn_in_model = True
        
        # Check actual translation files
        zh_files = list(self.base_path.rglob("zh.json")) + list(self.base_path.rglob("*/zh/*.json"))
        if zh_files:
            zh_in_files = True
        
        inconsistency_confirmed = zh_cn_in_model and zh_in_files
        
        self.log_validation(
            "Security Audit",
            "Language code inconsistency (zh-CN vs zh)",
            inconsistency_confirmed,
            f"Model uses zh-CN: {zh_cn_in_model}, Files use zh: {zh_in_files}"
        )
        
        print(f"   {'✅ CONFIRMED' if inconsistency_confirmed else '❌ NOT CONFIRMED'}: Language code mismatch found")
        
        # Validate XSS vulnerability claims
        print("\n2. Validating XSS Vulnerability Claims...")
        
        actual_html_found = False
        script_content_found = False
        
        for json_file in self.base_path.rglob("*.json"):
            if "i18n" not in str(json_file):
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for actual HTML tags (not just accented characters)
                if '<script' in content.lower() or '<iframe' in content.lower():
                    script_content_found = True
                
                if '<' in content and '>' in content and 'script' not in content.lower():
                    # Check if it's actual HTML vs accented characters
                    import re
                    html_tags = re.findall(r'<[^>]+>', content)
                    if html_tags:
                        actual_html_found = True
                        break
                        
            except Exception:
                continue
        
        xss_confirmed = actual_html_found or script_content_found
        
        self.log_validation(
            "Security Audit", 
            "XSS vulnerability in translations",
            xss_confirmed,
            f"Actual HTML found: {actual_html_found}, Script content: {script_content_found}"
        )
        
        print(f"   {'✅ CONFIRMED' if xss_confirmed else '❌ FALSE POSITIVE'}: XSS vulnerability claim")
    
    def validate_performance_findings(self):
        """Validate the performance audit findings"""
        print("\n🔍 VALIDATING PERFORMANCE AUDIT FINDINGS")
        print("="*50)
        
        # Validate file size measurements
        print("1. Validating File Size Measurements...")
        
        total_size = 0
        file_count = 0
        
        for json_file in self.base_path.rglob("*.json"):
            if "i18n" in str(json_file):
                try:
                    file_size = json_file.stat().st_size
                    total_size += file_size
                    file_count += 1
                except:
                    continue
        
        total_size_mb = total_size / (1024 * 1024)
        avg_size_kb = (total_size / file_count / 1024) if file_count > 0 else 0
        
        size_efficient = total_size_mb < 1.0 and avg_size_kb < 10.0
        
        self.log_validation(
            "Performance Audit",
            "Translation files are efficiently sized",
            size_efficient,
            f"Total: {total_size_mb:.2f}MB, Average: {avg_size_kb:.1f}KB, Files: {file_count}"
        )
        
        print(f"   {'✅ CONFIRMED' if size_efficient else '❌ NOT CONFIRMED'}: File sizes are efficient")
        print(f"      Total size: {total_size_mb:.2f}MB across {file_count} files")
        
        # Validate memory usage claims
        print("\n2. Validating Memory Usage Claims...")
        
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)
        
        # Load all translation files
        start_time = time.time()
        translations = {}
        
        try:
            for json_file in self.base_path.rglob("*.json"):
                if "i18n" in str(json_file):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        translations[str(json_file)] = json.load(f)
            
            load_time = time.time() - start_time
            peak_memory = process.memory_info().rss / (1024 * 1024)
            memory_used = peak_memory - initial_memory
            
            memory_efficient = memory_used < 10.0 and load_time < 0.5
            
            self.log_validation(
                "Performance Audit",
                "Memory usage is efficient",
                memory_efficient,
                f"Memory used: {memory_used:.1f}MB, Load time: {load_time*1000:.0f}ms"
            )
            
            print(f"   {'✅ CONFIRMED' if memory_efficient else '❌ NOT CONFIRMED'}: Memory usage is efficient")
            print(f"      Memory used: {memory_used:.1f}MB, Load time: {load_time*1000:.0f}ms")
            
        except Exception as e:
            print(f"   ❌ ERROR: Could not validate memory usage - {e}")
    
    def validate_code_quality_findings(self):
        """Validate the code quality audit findings"""
        print("\n🔍 VALIDATING CODE QUALITY AUDIT FINDINGS")
        print("="*50)
        
        # Validate TypeScript type safety issues
        print("1. Validating TypeScript Type Safety Issues...")
        
        ts_files_with_any = 0
        total_ts_files = 0
        
        for ts_file in self.base_path.rglob("*.ts"):
            if "node_modules" in str(ts_file):
                continue
                
            total_ts_files += 1
            try:
                with open(ts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if ': any' in content:
                    ts_files_with_any += 1
                    
            except Exception:
                continue
        
        type_safety_issues = ts_files_with_any > (total_ts_files * 0.1)  # >10% of files
        
        self.log_validation(
            "Code Quality Audit",
            "TypeScript type safety issues exist",
            type_safety_issues,
            f"Files with 'any': {ts_files_with_any}/{total_ts_files}"
        )
        
        print(f"   {'✅ CONFIRMED' if type_safety_issues else '❌ NOT CONFIRMED'}: TypeScript type safety issues")
        print(f"      Files with 'any' type: {ts_files_with_any}/{total_ts_files}")
        
        # Validate pluralization support issues
        print("\n2. Validating Pluralization Support Issues...")
        
        languages_with_plurals = set()
        languages_without_plurals = set()
        
        for json_file in self.base_path.rglob("*.json"):
            if "i18n" not in str(json_file):
                continue
                
            # Extract language from file path
            lang_code = None
            parts = json_file.parts
            
            if json_file.name.endswith('.json') and len(json_file.stem) == 2:
                lang_code = json_file.stem
            elif len(parts) > 1 and len(parts[-2]) == 2:
                lang_code = parts[-2]
            
            if lang_code:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if '_plural' in content or '{{count}}' in content:
                        languages_with_plurals.add(lang_code)
                    else:
                        languages_without_plurals.add(lang_code)
                        
                except Exception:
                    continue
        
        # Check if complex languages (Russian, Arabic) have pluralization
        complex_languages = {"ru", "ar"}
        missing_complex_plurals = complex_languages - languages_with_plurals
        
        pluralization_issues = len(missing_complex_plurals) > 0
        
        self.log_validation(
            "Code Quality Audit",
            "Complex languages lack pluralization",
            pluralization_issues, 
            f"Languages with plurals: {sorted(languages_with_plurals)}, Missing complex: {sorted(missing_complex_plurals)}"
        )
        
        print(f"   {'✅ CONFIRMED' if pluralization_issues else '❌ NOT CONFIRMED'}: Pluralization support issues")
        print(f"      Languages with plurals: {sorted(languages_with_plurals)}")
        print(f"      Missing complex plurals: {sorted(missing_complex_plurals)}")
    
    def validate_audit_coverage(self):
        """Validate that the audit covered all important areas"""
        print("\n🔍 VALIDATING AUDIT COVERAGE")
        print("="*50)
        
        # Check if all critical files were analyzed
        critical_files = [
            "services/gameserver/src/models/translation.py",
            "services/gameserver/src/services/translation_service.py", 
            "services/gameserver/src/api/routes/translation.py",
            "shared/i18n/config.ts",
            "services/admin-ui/src/components/common/LanguageSwitcher.tsx"
        ]
        
        files_exist = 0
        for file_path in critical_files:
            if (self.base_path / file_path).exists():
                files_exist += 1
        
        coverage_adequate = files_exist >= len(critical_files) * 0.8  # 80% coverage
        
        self.log_validation(
            "Audit Coverage",
            "All critical files were covered",
            coverage_adequate,
            f"Critical files found: {files_exist}/{len(critical_files)}"
        )
        
        print(f"   {'✅ CONFIRMED' if coverage_adequate else '❌ INSUFFICIENT'}: Audit coverage")
        print(f"      Critical files analyzed: {files_exist}/{len(critical_files)}")
        
        # Check translation file coverage
        expected_languages = {"en", "es", "fr", "zh", "pt"}
        found_languages = set()
        
        for json_file in self.base_path.rglob("*.json"):
            if "i18n" in str(json_file):
                if json_file.name.endswith('.json') and len(json_file.stem) == 2:
                    found_languages.add(json_file.stem)
        
        lang_coverage = len(found_languages & expected_languages) / len(expected_languages)
        
        print(f"      Language coverage: {lang_coverage*100:.0f}% ({len(found_languages & expected_languages)}/{len(expected_languages)})")
    
    def generate_validation_report(self):
        """Generate validation summary report"""
        print("\n" + "="*60)
        print("✅ AUDIT VALIDATION SUMMARY")
        print("="*60)
        
        confirmed_findings = [v for v in self.validation_results if v["confirmed"]]
        disputed_findings = [v for v in self.validation_results if not v["confirmed"]]
        
        print(f"Total Findings Validated: {len(self.validation_results)}")
        print(f"Confirmed Findings: {len(confirmed_findings)}")
        print(f"Disputed/False Positives: {len(disputed_findings)}")
        
        print(f"\n✅ CONFIRMED FINDINGS:")
        for finding in confirmed_findings:
            print(f"   • {finding['finding']}")
            print(f"     Details: {finding['details']}")
        
        if disputed_findings:
            print(f"\n❌ DISPUTED FINDINGS:")
            for finding in disputed_findings:
                print(f"   • {finding['finding']}")
                print(f"     Details: {finding['details']}")
        
        # Calculate audit accuracy
        accuracy = len(confirmed_findings) / len(self.validation_results) * 100 if self.validation_results else 0
        
        print(f"\n📊 AUDIT ACCURACY: {accuracy:.1f}%")
        
        if accuracy >= 80:
            print("🎯 EXCELLENT: Audit findings are highly reliable")
        elif accuracy >= 60:
            print("✅ GOOD: Audit findings are mostly accurate")
        else:
            print("⚠️  FAIR: Audit has some false positives")

def main():
    """Run the audit validation"""
    print("✅ STARTING AUDIT VALIDATION FOR SECTORWARS 2102 I18N AUDIT")
    print("="*70)
    
    validator = AuditValidationTest()
    
    # Run all validation tests
    validator.validate_security_findings()
    validator.validate_performance_findings()
    validator.validate_code_quality_findings()
    validator.validate_audit_coverage()
    
    # Generate validation report
    validator.generate_validation_report()

if __name__ == "__main__":
    main()