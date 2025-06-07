#!/usr/bin/env python3
"""
Simple System Health Check for Multi-Regional SectorWars 2102
Uses built-in modules to test basic connectivity
"""

import sys
import socket
import subprocess
import time
from urllib.request import urlopen
from urllib.error import URLError


def test_port_connectivity():
    """Test that all required ports are accessible"""
    print("🔌 Testing Port Connectivity...")
    
    ports_to_test = [
        (5433, "PostgreSQL Database"),
        (6379, "Redis Cache"),
        (8080, "Game Server"),
        (8081, "Region Manager"),
        (3000, "Player Client"),
        (3001, "Admin UI"),
        (80, "Nginx Gateway")
    ]
    
    results = {}
    for port, service in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                results[service] = "✅ OPEN"
                print(f"  ✅ {service} (:{port}): ACCESSIBLE")
            else:
                results[service] = "❌ CLOSED"
                print(f"  ❌ {service} (:{port}): NOT ACCESSIBLE")
        
        except Exception as e:
            results[service] = f"❌ ERROR: {e}"
            print(f"  ❌ {service} (:{port}): ERROR - {e}")
    
    return results


def test_docker_containers():
    """Test Docker container status"""
    print("\n🐳 Testing Docker Container Status...")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            container_count = 0
            healthy_count = 0
            
            for line in lines[1:]:  # Skip header
                if 'sectorwars' in line:
                    container_count += 1
                    if 'Up' in line:
                        healthy_count += 1
                        print(f"  ✅ {line}")
                    else:
                        print(f"  ❌ {line}")
            
            print(f"\n  📊 Summary: {healthy_count}/{container_count} containers healthy")
            return {"total": container_count, "healthy": healthy_count}
        
        else:
            print(f"  ❌ Docker command failed: {result.stderr}")
            return {"error": result.stderr}
    
    except Exception as e:
        print(f"  ❌ Docker test failed: {e}")
        return {"error": str(e)}


def test_http_endpoints():
    """Test HTTP endpoint accessibility"""
    print("\n🌐 Testing HTTP Endpoint Accessibility...")
    
    endpoints_to_test = [
        ("http://localhost:8080/api/v1/status/health", "Game Server Health"),
        ("http://localhost:8081/health", "Region Manager Health"),
        ("http://localhost:3000", "Player Client"),
        ("http://localhost:3001", "Admin UI"),
        ("http://localhost:80", "Nginx Gateway")
    ]
    
    results = {}
    for url, service in endpoints_to_test:
        try:
            start_time = time.time()
            response = urlopen(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status == 200:
                results[service] = f"✅ OK ({response_time:.0f}ms)"
                print(f"  ✅ {service}: OK ({response_time:.0f}ms)")
            else:
                results[service] = f"❌ HTTP {response.status}"
                print(f"  ❌ {service}: HTTP {response.status}")
        
        except URLError as e:
            results[service] = f"❌ URL Error: {e}"
            print(f"  ❌ {service}: URL Error - {e}")
        
        except Exception as e:
            results[service] = f"❌ Error: {e}"
            print(f"  ❌ {service}: Error - {e}")
    
    return results


def test_redis_connection():
    """Test Redis connection using redis-cli"""
    print("\n🔥 Testing Redis Connection...")
    
    try:
        result = subprocess.run(
            ["docker", "exec", "sectorwars-redis-cache", "redis-cli", "-a", "redis_dev_password_123", "ping"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "PONG" in result.stdout:
            print("  ✅ Redis: PONG received")
            return {"status": "working"}
        else:
            print(f"  ❌ Redis: {result.stderr}")
            return {"status": "failed", "error": result.stderr}
    
    except Exception as e:
        print(f"  ❌ Redis test failed: {e}")
        return {"status": "error", "error": str(e)}


def test_database_connection():
    """Test PostgreSQL connection"""
    print("\n🗄️ Testing PostgreSQL Connection...")
    
    try:
        result = subprocess.run(
            ["docker", "exec", "sectorwars-database", "pg_isready", "-U", "postgres", "-d", "sectorwars_dev"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  ✅ PostgreSQL: Connection ready")
            return {"status": "working"}
        else:
            print(f"  ❌ PostgreSQL: {result.stderr}")
            return {"status": "failed", "error": result.stderr}
    
    except Exception as e:
        print(f"  ❌ PostgreSQL test failed: {e}")
        return {"status": "error", "error": str(e)}


def generate_system_report(test_results):
    """Generate system health report"""
    print("\n" + "="*60)
    print("📊 SYSTEM HEALTH REPORT")
    print("="*60)
    
    # Count successful tests
    total_services = 0
    healthy_services = 0
    
    for category, results in test_results.items():
        if isinstance(results, dict):
            for service, status in results.items():
                if service not in ["total", "healthy", "error", "status"]:
                    total_services += 1
                    if "✅" in str(status) or "working" in str(status):
                        healthy_services += 1
    
    # Calculate health percentage
    health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
    
    print(f"\n🎯 OVERALL SYSTEM HEALTH: {health_percentage:.1f}%")
    print(f"   Services Tested: {total_services}")
    print(f"   Healthy Services: {healthy_services}")
    print(f"   Failed Services: {total_services - healthy_services}")
    
    # Determine system status
    if health_percentage >= 90:
        status_icon = "🟢"
        status_text = "EXCELLENT - System Fully Operational"
    elif health_percentage >= 75:
        status_icon = "🟡"
        status_text = "GOOD - Minor Issues Detected"
    elif health_percentage >= 50:
        status_icon = "🟠"
        status_text = "FAIR - Multiple Issues Detected"
    else:
        status_icon = "🔴"
        status_text = "POOR - Critical System Issues"
    
    print(f"\n{status_icon} STATUS: {status_text}")
    
    # Architecture status
    print(f"\n🏗️ ARCHITECTURE STATUS:")
    redis_working = test_results.get("redis", {}).get("status") == "working"
    db_working = test_results.get("database", {}).get("status") == "working"
    
    if redis_working and db_working:
        print("   ✅ Hybrid PostgreSQL + Redis architecture: OPERATIONAL")
    elif db_working:
        print("   🟡 PostgreSQL operational, Redis issues detected")
    elif redis_working:
        print("   🟡 Redis operational, PostgreSQL issues detected")
    else:
        print("   ❌ Critical database infrastructure issues")
    
    # Docker status
    docker_results = test_results.get("docker", {})
    if "total" in docker_results and "healthy" in docker_results:
        total = docker_results["total"]
        healthy = docker_results["healthy"]
        if total > 0:
            docker_health = (healthy / total) * 100
            print(f"   🐳 Docker containers: {healthy}/{total} healthy ({docker_health:.0f}%)")
    
    print("\n🚀 DEPLOYMENT READINESS:")
    if health_percentage >= 90:
        print("   ✅ READY FOR PRODUCTION")
        print("   ✅ Multi-regional system operational")
        print("   ✅ All critical services healthy")
    elif health_percentage >= 75:
        print("   🟡 READY FOR STAGING")
        print("   🟡 Address minor issues before production")
    else:
        print("   ❌ NOT READY FOR DEPLOYMENT")
        print("   ❌ Critical issues must be resolved")
    
    print("="*60)
    
    return health_percentage >= 75


def main():
    """Main system health check function"""
    print("🚀 SectorWars 2102 Multi-Regional System Health Check")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run all health checks
    test_results = {}
    
    test_results["ports"] = test_port_connectivity()
    test_results["docker"] = test_docker_containers()
    test_results["http"] = test_http_endpoints()
    test_results["redis"] = test_redis_connection()
    test_results["database"] = test_database_connection()
    
    # Generate final report
    system_healthy = generate_system_report(test_results)
    
    # Exit with appropriate code
    exit_code = 0 if system_healthy else 1
    print(f"\n🏁 Health check completed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Health check interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Health check failed: {e}")
        sys.exit(1)