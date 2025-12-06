#!/usr/bin/env python3
"""
System Health Check for SectorWars 2102
Automatically detects environment (development vs production) and adjusts expectations.
Uses built-in modules to test basic connectivity.
"""

import os
import sys
import socket
import subprocess
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def detect_environment():
    """Detect deployment environment and architecture mode"""
    env = os.environ.get("ENVIRONMENT", "development").lower()
    dev_env = os.environ.get("DEV_ENVIRONMENT", "").lower()
    compose_profiles = os.environ.get("COMPOSE_PROFILES", "").lower()

    is_multi_regional = "multi-regional" in compose_profiles
    is_development = env in ["development", "dev"] or "codespace" in dev_env

    return {
        "environment": env,
        "is_development": is_development,
        "is_multi_regional": is_multi_regional,
        "compose_profiles": compose_profiles
    }


def test_port_connectivity(env_config):
    """Test that all required ports are accessible"""
    print("🔌 Testing Port Connectivity...")

    # Core services required in all environments
    required_ports = [
        (5433, "PostgreSQL Database", True),
        (6379, "Redis Cache", True),
        (8080, "Game Server", True),
        (3000, "Player Client", True),
        (3001, "Admin UI", True),
        (80, "Nginx Gateway", True)
    ]

    # Optional services based on environment
    optional_ports = [
        (8081, "Region Manager", env_config["is_multi_regional"])
    ]

    results = {}
    optional_results = {}

    # Test required ports
    for port, service, _ in required_ports:
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

    # Test optional ports
    for port, service, should_test in optional_ports:
        if should_test:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('localhost', port))
                sock.close()

                if result == 0:
                    optional_results[service] = "✅ OPEN"
                    print(f"  ✅ {service} (:{port}): ACCESSIBLE")
                else:
                    optional_results[service] = "⚠️ OPTIONAL - Not Running"
                    print(f"  ⚠️ {service} (:{port}): OPTIONAL - Not running")

            except Exception as e:
                optional_results[service] = f"⚠️ OPTIONAL - {e}"
                print(f"  ⚠️ {service} (:{port}): OPTIONAL - {e}")
        else:
            print(f"  ⏸️ {service} (:{port}): SKIPPED - Not required in {env_config['environment']} mode")

    return {"required": results, "optional": optional_results}


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


def test_http_endpoints(env_config):
    """Test HTTP endpoint accessibility"""
    print("\n🌐 Testing HTTP Endpoint Accessibility...")

    # Required API endpoints (need proper HTTP 200 responses)
    required_api_endpoints = [
        ("http://localhost:8080/api/v1/status/health", "Game Server Health")
    ]

    # Frontend services (in development, just verify they're serving content)
    required_frontend_endpoints = [
        (3000, "Player Client"),
        (3001, "Admin UI"),
        (80, "Nginx Gateway")
    ]

    # Optional endpoints based on environment
    optional_endpoints = [
        ("http://localhost:8081/health", "Region Manager Health", env_config["is_multi_regional"])
    ]

    results = {}
    optional_results = {}

    # Test API endpoints (expect proper HTTP 200 responses)
    for url, service in required_api_endpoints:
        start_time = time.time()
        try:
            request = Request(url, headers={'User-Agent': 'SectorWars-HealthCheck/1.0'})
            response = urlopen(request, timeout=10)
            response_time = (time.time() - start_time) * 1000

            if response.status == 200:
                results[service] = f"✅ OK ({response_time:.0f}ms)"
                print(f"  ✅ {service}: OK ({response_time:.0f}ms)")
            else:
                results[service] = f"❌ HTTP {response.status}"
                print(f"  ❌ {service}: HTTP {response.status}")

        except HTTPError as e:
            response_time = (time.time() - start_time) * 1000
            results[service] = f"❌ HTTP {e.code}"
            print(f"  ❌ {service}: HTTP {e.code}")

        except URLError as e:
            response_time = (time.time() - start_time) * 1000
            results[service] = f"❌ Connection Failed"
            print(f"  ❌ {service}: Connection failed")

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            results[service] = f"❌ Error"
            print(f"  ❌ {service}: Error - {type(e).__name__}")

    # Test frontend services (just verify HTTP connection works)
    # Vite dev servers behave differently with different clients, so we just check connectivity
    for port, service in required_frontend_endpoints:
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            response_time = (time.time() - start_time) * 1000

            if result == 0:
                # Port is open, now try a simple HTTP request
                try:
                    request = Request(f'http://localhost:{port}',
                                    headers={'User-Agent': 'Mozilla/5.0'})
                    response = urlopen(request, timeout=5)
                    results[service] = f"✅ OK ({response_time:.0f}ms)"
                    print(f"  ✅ {service}: OK ({response_time:.0f}ms)")
                except (HTTPError, URLError):
                    # Even if we get an HTTP error, if we can connect, the service is up
                    results[service] = f"✅ OK (Serving)"
                    print(f"  ✅ {service}: OK (Serving)")
            else:
                results[service] = "❌ Port Closed"
                print(f"  ❌ {service}: Port not accessible")

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            results[service] = "❌ Connection Failed"
            print(f"  ❌ {service}: Connection failed")

    # Test optional endpoints
    for url, service, should_test in optional_endpoints:
        if should_test:
            try:
                start_time = time.time()
                request = Request(url, headers={'User-Agent': 'SectorWars-HealthCheck/1.0'})
                response = urlopen(request, timeout=10)
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    optional_results[service] = f"✅ OK ({response_time:.0f}ms)"
                    print(f"  ✅ {service}: OK ({response_time:.0f}ms)")
                else:
                    optional_results[service] = f"⚠️ HTTP {response.status}"
                    print(f"  ⚠️ {service}: HTTP {response.status}")

            except Exception as e:
                optional_results[service] = f"⚠️ OPTIONAL - Not Available"
                print(f"  ⚠️ {service}: OPTIONAL - Not available")
        else:
            print(f"  ⏸️ {service}: SKIPPED - Not required in {env_config['environment']} mode")

    return {"required": results, "optional": optional_results}


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


def generate_system_report(test_results, env_config):
    """Generate system health report"""
    print("\n" + "="*60)
    print("📊 SYSTEM HEALTH REPORT")
    print("="*60)

    # Display environment information
    print(f"\n🌍 ENVIRONMENT: {env_config['environment'].upper()}")
    if env_config['is_multi_regional']:
        print(f"   🌐 Mode: Multi-Regional Architecture")
    else:
        print(f"   💻 Mode: Single-Region Development")

    # Count successful tests for REQUIRED services only
    total_required = 0
    healthy_required = 0
    total_optional = 0
    healthy_optional = 0

    for category, results in test_results.items():
        if isinstance(results, dict):
            # Handle required services
            if "required" in results:
                for service, status in results["required"].items():
                    total_required += 1
                    if "✅" in str(status) or "working" in str(status):
                        healthy_required += 1

            # Handle optional services
            if "optional" in results:
                for service, status in results["optional"].items():
                    total_optional += 1
                    if "✅" in str(status):
                        healthy_optional += 1

            # Handle simple status dict (redis, database)
            if "status" in results and category in ["redis", "database"]:
                total_required += 1
                if results["status"] == "working":
                    healthy_required += 1

            # Handle docker results
            if "total" in results and "healthy" in results and category == "docker":
                # Don't count individual containers in overall score
                pass

    # Calculate health percentage based on REQUIRED services only
    health_percentage = (healthy_required / total_required * 100) if total_required > 0 else 0

    print(f"\n🎯 REQUIRED SERVICES HEALTH: {health_percentage:.1f}%")
    print(f"   Required Services: {healthy_required}/{total_required} healthy")
    if total_optional > 0:
        optional_percentage = (healthy_optional / total_optional * 100) if total_optional > 0 else 0
        print(f"   Optional Services: {healthy_optional}/{total_optional} healthy ({optional_percentage:.1f}%)")

    # Determine system status
    if health_percentage >= 95:
        status_icon = "🟢"
        status_text = "EXCELLENT - System Fully Operational"
    elif health_percentage >= 85:
        status_icon = "🟡"
        status_text = "GOOD - Minor Issues Detected"
    elif health_percentage >= 70:
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

    # Deployment readiness (environment-aware)
    print("\n🚀 DEPLOYMENT READINESS:")
    if env_config['is_development']:
        # Development environment thresholds
        if health_percentage >= 90:
            print("   ✅ READY FOR DEVELOPMENT")
            print("   ✅ All critical services operational")
        elif health_percentage >= 75:
            print("   🟡 DEVELOPMENT MODE - Minor issues detected")
            print("   🟡 Fix issues for optimal development experience")
        else:
            print("   ❌ DEVELOPMENT ENVIRONMENT ISSUES")
            print("   ❌ Critical services need attention")
    else:
        # Production environment thresholds (stricter)
        if health_percentage >= 95 and total_optional > 0 and healthy_optional == total_optional:
            print("   ✅ READY FOR PRODUCTION")
            print("   ✅ Multi-regional system operational")
            print("   ✅ All critical and optional services healthy")
        elif health_percentage >= 90:
            print("   🟡 READY FOR STAGING")
            print("   🟡 Address minor issues before production")
        else:
            print("   ❌ NOT READY FOR DEPLOYMENT")
            print("   ❌ Critical issues must be resolved")

    print("="*60)

    # Success threshold: 85% for dev, 90% for production
    threshold = 85 if env_config['is_development'] else 90
    return health_percentage >= threshold


def main():
    """Main system health check function"""
    print("🚀 SectorWars 2102 System Health Check")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Detect environment configuration
    env_config = detect_environment()
    print(f"\n🔍 Detected Environment: {env_config['environment']}")
    if env_config['is_multi_regional']:
        print(f"   Multi-regional mode enabled")
    if env_config['is_development']:
        print(f"   Development mode - using relaxed health thresholds")

    # Run all health checks
    test_results = {}

    test_results["ports"] = test_port_connectivity(env_config)
    test_results["docker"] = test_docker_containers()
    test_results["http"] = test_http_endpoints(env_config)
    test_results["redis"] = test_redis_connection()
    test_results["database"] = test_database_connection()

    # Generate final report
    system_healthy = generate_system_report(test_results, env_config)

    # Exit with appropriate code
    exit_code = 0 if system_healthy else 1
    print(f"\n🏁 Health check completed with exit code: {exit_code}")

    if not system_healthy:
        print(f"\n💡 TIP: Review failed services above and check logs:")
        print(f"   docker-compose logs <service-name>")

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