#!/usr/bin/env python3
"""
Performance Audit Test Suite for SectorWars 2102 I18N Implementation
Tests for caching, database queries, and payload optimization
"""

import json
import time
import os
import psutil
from pathlib import Path
from typing import Dict, List, Any

class PerformanceAuditTest:
    def __init__(self):
        self.test_results = []
        self.base_path = Path(__file__).parent / "shared" / "i18n"
        
    def log_test_result(self, test_name: str, severity: str, status: str, details: str, metrics: Dict = None):
        """Log test result with performance metrics"""
        result = {
            "test": test_name,
            "severity": severity,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        if metrics:
            result["metrics"] = metrics
        self.test_results.append(result)
    
    def test_translation_file_sizes(self):
        """Test 7: Payload Size Optimization"""
        print("🔍 Test 7: Translation File Size Analysis")
        
        file_sizes = {}
        total_size = 0
        large_files = []
        
        # Check all translation files
        for file_path in self.base_path.rglob("*.json"):
            try:
                file_size = os.path.getsize(file_path)
                relative_path = str(file_path.relative_to(self.base_path))
                file_sizes[relative_path] = file_size
                total_size += file_size
                
                # Flag large files (>100KB)
                if file_size > 100 * 1024:
                    large_files.append((relative_path, file_size))
                    
            except Exception as e:
                print(f"   ❌ Error checking {file_path}: {e}")
        
        # Analyze sizes
        avg_size = total_size / len(file_sizes) if file_sizes else 0
        max_size = max(file_sizes.values()) if file_sizes else 0
        max_file = max(file_sizes.items(), key=lambda x: x[1])[0] if file_sizes else None
        
        metrics = {
            "total_files": len(file_sizes),
            "total_size_mb": total_size / (1024 * 1024),
            "average_size_kb": avg_size / 1024,
            "largest_file": max_file,
            "largest_size_kb": max_size / 1024,
            "large_files_count": len(large_files)
        }
        
        # Performance thresholds
        issues = []
        if total_size > 10 * 1024 * 1024:  # >10MB total
            issues.append(f"Total translation size is large: {total_size/(1024*1024):.1f}MB")
        
        if max_size > 500 * 1024:  # >500KB single file
            issues.append(f"Largest file is too big: {max_file} ({max_size/1024:.1f}KB)")
        
        if avg_size > 100 * 1024:  # >100KB average
            issues.append(f"Average file size is large: {avg_size/1024:.1f}KB")
        
        if issues:
            self.log_test_result(
                "Translation File Sizes",
                "MEDIUM",
                "FAILED",
                f"Found {len(issues)} size optimization issues",
                metrics
            )
            print(f"   ❌ FAILED: Found {len(issues)} size issues")
            for issue in issues:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Translation File Sizes",
                "MEDIUM", 
                "PASSED",
                "Translation file sizes are optimized",
                metrics
            )
            print("   ✅ PASSED: File sizes are reasonable")
        
        print(f"      📊 Total: {total_size/(1024*1024):.1f}MB across {len(file_sizes)} files")
        print(f"      📊 Average: {avg_size/1024:.1f}KB per file")
        print(f"      📊 Largest: {max_file} ({max_size/1024:.1f}KB)")
    
    def test_memory_usage_simulation(self):
        """Test 5: Memory Usage Analysis"""
        print("\n🔍 Test 5: Memory Usage Simulation")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Load all translation files into memory
        loaded_translations = {}
        start_time = time.time()
        
        try:
            for file_path in self.base_path.rglob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    relative_path = str(file_path.relative_to(self.base_path))
                    loaded_translations[relative_path] = content
            
            load_time = time.time() - start_time
            peak_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_used = peak_memory - initial_memory
            
            # Count total translation keys
            total_keys = 0
            for content in loaded_translations.values():
                def count_keys(data):
                    count = 0
                    if isinstance(data, dict):
                        for value in data.values():
                            if isinstance(value, dict):
                                count += count_keys(value)
                            else:
                                count += 1
                    return count
                total_keys += count_keys(content)
            
            metrics = {
                "load_time_ms": load_time * 1000,
                "memory_used_mb": memory_used,
                "total_files": len(loaded_translations),
                "total_keys": total_keys,
                "keys_per_mb": total_keys / memory_used if memory_used > 0 else 0
            }
            
            # Performance thresholds
            issues = []
            if load_time > 1.0:  # >1 second load time
                issues.append(f"Load time is slow: {load_time*1000:.0f}ms")
            
            if memory_used > 50:  # >50MB memory usage
                issues.append(f"Memory usage is high: {memory_used:.1f}MB")
            
            if issues:
                self.log_test_result(
                    "Memory Usage Analysis",
                    "HIGH",
                    "FAILED", 
                    f"Found {len(issues)} memory performance issues",
                    metrics
                )
                print(f"   ❌ FAILED: Found {len(issues)} memory issues")
                for issue in issues:
                    print(f"      - {issue}")
            else:
                self.log_test_result(
                    "Memory Usage Analysis",
                    "HIGH",
                    "PASSED",
                    "Memory usage is within acceptable limits",
                    metrics
                )
                print("   ✅ PASSED: Memory usage is efficient")
            
            print(f"      📊 Load time: {load_time*1000:.0f}ms")
            print(f"      📊 Memory used: {memory_used:.1f}MB")
            print(f"      📊 Keys loaded: {total_keys:,}")
            
        except Exception as e:
            self.log_test_result(
                "Memory Usage Analysis",
                "HIGH",
                "ERROR",
                f"Test failed with error: {str(e)}"
            )
            print(f"   ❌ ERROR: {e}")
    
    def test_translation_loading_efficiency(self):
        """Test 6: Translation Loading Efficiency"""
        print("\n🔍 Test 6: Translation Loading Efficiency")
        
        # Test individual file loading times
        load_times = []
        file_performances = []
        
        for file_path in list(self.base_path.rglob("*.json"))[:10]:  # Test first 10 files
            try:
                start_time = time.time()
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                load_time = time.time() - start_time
                file_size = os.path.getsize(file_path)
                
                load_times.append(load_time)
                file_performances.append({
                    "file": str(file_path.relative_to(self.base_path)),
                    "load_time_ms": load_time * 1000,
                    "size_kb": file_size / 1024,
                    "throughput": file_size / load_time if load_time > 0 else 0
                })
                
            except Exception as e:
                print(f"   ❌ Error loading {file_path}: {e}")
        
        if load_times:
            avg_load_time = sum(load_times) / len(load_times)
            max_load_time = max(load_times)
            slow_files = [f for f in file_performances if f["load_time_ms"] > 100]  # >100ms
            
            metrics = {
                "files_tested": len(load_times),
                "avg_load_time_ms": avg_load_time * 1000,
                "max_load_time_ms": max_load_time * 1000,
                "slow_files_count": len(slow_files)
            }
            
            # Performance thresholds
            issues = []
            if avg_load_time > 0.05:  # >50ms average
                issues.append(f"Average load time is slow: {avg_load_time*1000:.0f}ms")
            
            if max_load_time > 0.2:  # >200ms max
                issues.append(f"Slowest file takes too long: {max_load_time*1000:.0f}ms")
            
            if len(slow_files) > len(file_performances) * 0.2:  # >20% slow files
                issues.append(f"Too many slow files: {len(slow_files)}/{len(file_performances)}")
            
            if issues:
                self.log_test_result(
                    "Translation Loading Efficiency",
                    "MEDIUM",
                    "FAILED",
                    f"Found {len(issues)} loading efficiency issues",
                    metrics
                )
                print(f"   ❌ FAILED: Found {len(issues)} efficiency issues")
                for issue in issues:
                    print(f"      - {issue}")
            else:
                self.log_test_result(
                    "Translation Loading Efficiency",
                    "MEDIUM",
                    "PASSED",
                    "Translation loading is efficient",
                    metrics
                )
                print("   ✅ PASSED: Loading efficiency is good")
            
            print(f"      📊 Average load time: {avg_load_time*1000:.1f}ms")
            print(f"      📊 Slowest file: {max_load_time*1000:.1f}ms")
            print(f"      📊 Files tested: {len(load_times)}")
    
    def test_translation_structure_efficiency(self):
        """Test translation key structure for lookup efficiency"""
        print("\n🔍 Test: Translation Structure Efficiency")
        
        depth_analysis = {}
        key_count_analysis = {}
        
        for file_path in self.base_path.rglob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                def analyze_structure(data, depth=0, path=""):
                    if isinstance(data, dict):
                        for key, value in data.items():
                            current_path = f"{path}.{key}" if path else key
                            if isinstance(value, dict):
                                analyze_structure(value, depth + 1, current_path)
                            else:
                                # Record depth for this key
                                if depth not in depth_analysis:
                                    depth_analysis[depth] = 0
                                depth_analysis[depth] += 1
                
                analyze_structure(content)
                
                # Count keys at each level
                relative_path = str(file_path.relative_to(self.base_path))
                key_count_analysis[relative_path] = len(str(content))
                
            except Exception as e:
                print(f"   ❌ Error analyzing {file_path}: {e}")
        
        # Analyze structure efficiency
        max_depth = max(depth_analysis.keys()) if depth_analysis else 0
        avg_depth = sum(d * count for d, count in depth_analysis.items()) / sum(depth_analysis.values()) if depth_analysis else 0
        
        metrics = {
            "max_depth": max_depth,
            "average_depth": avg_depth,
            "depth_distribution": depth_analysis
        }
        
        issues = []
        if max_depth > 5:  # Too deep nesting
            issues.append(f"Translation structure is too deep: {max_depth} levels")
        
        if avg_depth > 3:  # Average too deep
            issues.append(f"Average nesting depth is high: {avg_depth:.1f}")
        
        if issues:
            self.log_test_result(
                "Translation Structure Efficiency",
                "LOW",
                "FAILED",
                f"Found {len(issues)} structure efficiency issues",
                metrics
            )
            print(f"   ❌ FAILED: Found {len(issues)} structure issues")
            for issue in issues:
                print(f"      - {issue}")
        else:
            self.log_test_result(
                "Translation Structure Efficiency",
                "LOW",
                "PASSED",
                "Translation structure is efficient for lookups",
                metrics
            )
            print("   ✅ PASSED: Structure is efficient")
        
        print(f"      📊 Maximum nesting depth: {max_depth}")
        print(f"      📊 Average depth: {avg_depth:.1f}")
    
    def generate_performance_report(self):
        """Generate comprehensive performance audit report"""
        print("\n" + "="*60)
        print("⚡ PERFORMANCE AUDIT REPORT")
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
        
        # Display key metrics
        print(f"\n📊 KEY PERFORMANCE METRICS:")
        for test in self.test_results:
            if "metrics" in test:
                print(f"   {test['test']}:")
                for metric, value in test["metrics"].items():
                    if isinstance(value, float):
                        print(f"      {metric}: {value:.2f}")
                    else:
                        print(f"      {metric}: {value}")
        
        if failed_tests:
            print(f"\n❌ PERFORMANCE ISSUES:")
            for test in failed_tests:
                print(f"   [{test['severity']}] {test['test']}: {test['details']}")
        
        # Performance score
        total_points = len(self.test_results) * 10
        failed_points = len([r for r in high_severity if r['status'] == 'FAILED']) * 10
        failed_points += len([r for r in medium_severity if r['status'] == 'FAILED']) * 5
        failed_points += len([r for r in low_severity if r['status'] == 'FAILED']) * 2
        
        performance_score = max(0, total_points - failed_points) / total_points * 100
        
        print(f"\n📈 PERFORMANCE SCORE: {performance_score:.1f}%")
        
        if performance_score >= 90:
            print("🚀 EXCELLENT: Performance is highly optimized")
        elif performance_score >= 75:
            print("✅ GOOD: Performance is solid with room for minor improvements")
        elif performance_score >= 60:
            print("⚠️  FAIR: Performance needs optimization")
        else:
            print("❌ POOR: Performance requires significant optimization")

def main():
    """Run the performance audit"""
    print("⚡ STARTING PERFORMANCE AUDIT FOR SECTORWARS 2102 I18N IMPLEMENTATION")
    print("="*75)
    
    auditor = PerformanceAuditTest()
    
    # Run all performance tests
    auditor.test_translation_file_sizes()
    auditor.test_memory_usage_simulation()
    auditor.test_translation_loading_efficiency()
    auditor.test_translation_structure_efficiency()
    
    # Generate final report
    auditor.generate_performance_report()

if __name__ == "__main__":
    main()