"""Monitoring service for regional containers and performance"""

import asyncio
import docker
import logging
from typing import Dict, Optional, Any
import httpx
import psutil
from datetime import datetime

from config import get_settings

logger = logging.getLogger(__name__)


class RegionMonitor:
    """Monitor regional container performance and health"""
    
    def __init__(self):
        self.settings = get_settings()
        self.docker_client = docker.from_env()
        self.http_client = httpx.AsyncClient(timeout=10.0)
    
    async def initialize(self):
        """Initialize monitoring service"""
        logger.info("Initializing Region Monitor...")
    
    async def cleanup(self):
        """Cleanup monitoring resources"""
        await self.http_client.aclose()
    
    async def get_container_stats(self, container_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get resource usage statistics for a container"""
        if not container_id:
            return None
        
        try:
            container = self.docker_client.containers.get(container_id)
            
            # Get container stats
            stats = container.stats(stream=False)
            
            # Calculate CPU usage
            cpu_stats = stats['cpu_stats']
            precpu_stats = stats['precpu_stats']
            
            cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
            system_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']
            cpu_percent = 0.0
            
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * len(cpu_stats['cpu_usage']['percpu_usage']) * 100.0
            
            # Calculate memory usage
            memory_stats = stats['memory_stats']
            memory_usage = memory_stats.get('usage', 0)
            memory_limit = memory_stats.get('limit', 1)
            memory_percent = (memory_usage / memory_limit) * 100.0
            memory_mb = memory_usage / (1024 * 1024)
            
            # Calculate network I/O
            network_io = 0.0
            if 'networks' in stats:
                for interface, data in stats['networks'].items():
                    network_io += data.get('rx_bytes', 0) + data.get('tx_bytes', 0)
            network_io_mb = network_io / (1024 * 1024)
            
            # Calculate disk I/O
            disk_io = 0.0
            if 'blkio_stats' in stats and 'io_service_bytes_recursive' in stats['blkio_stats']:
                for item in stats['blkio_stats']['io_service_bytes_recursive']:
                    disk_io += item.get('value', 0)
            disk_io_mb = disk_io / (1024 * 1024)
            
            # Container uptime
            created_at = datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
            uptime_seconds = (datetime.now(created_at.tzinfo) - created_at).total_seconds()
            
            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "network_io_mb": round(network_io_mb, 2),
                "disk_io_mb": round(disk_io_mb, 2),
                "uptime_seconds": int(uptime_seconds),
                "cpu_cores": len(cpu_stats['cpu_usage']['percpu_usage']),
                "memory_limit_gb": round(memory_limit / (1024 ** 3), 2)
            }
        
        except Exception as e:
            logger.error(f"Failed to get container stats for {container_id}: {e}")
            return None
    
    async def get_region_player_count(self, region_name: str) -> int:
        """Get current player count for a region"""
        try:
            # Try to get player count from regional API
            response = await self.http_client.get(
                f"http://region-{region_name}-server:8080/api/v1/status/players"
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('active_players', 0)
        
        except Exception as e:
            logger.warning(f"Failed to get player count for region {region_name}: {e}")
        
        return 0
    
    async def get_region_health(self, region_name: str) -> Dict[str, Any]:
        """Get comprehensive health status for a region"""
        try:
            response = await self.http_client.get(
                f"http://region-{region_name}-server:8080/api/v1/status/health"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Failed to get health for region {region_name}: {e}")
            return {"status": "unreachable", "error": str(e)}
    
    async def get_region_metrics(self, region_name: str) -> Dict[str, Any]:
        """Get detailed metrics for a region"""
        try:
            # Get basic metrics
            response = await self.http_client.get(
                f"http://region-{region_name}-server:8080/api/v1/status/metrics"
            )
            
            if response.status_code == 200:
                metrics = response.json()
                
                # Add container resource metrics
                containers = self.docker_client.containers.list(
                    filters={"label": f"region={region_name}"}
                )
                
                if containers:
                    container_stats = await self.get_container_stats(containers[0].id)
                    if container_stats:
                        metrics['resource_usage'] = container_stats
                
                return metrics
            else:
                return {"error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Failed to get metrics for region {region_name}: {e}")
            return {"error": str(e)}
    
    async def check_region_connectivity(self, region_name: str) -> bool:
        """Check if a region is reachable"""
        try:
            response = await self.http_client.get(
                f"http://region-{region_name}-server:8080/api/v1/status/ping",
                timeout=5.0
            )
            return response.status_code == 200
        
        except Exception:
            return False
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get host system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024 ** 3)
            memory_total_gb = memory.total / (1024 ** 3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)
            
            # Network stats
            network = psutil.net_io_counters()
            
            # Docker stats
            docker_containers = len(self.docker_client.containers.list())
            docker_images = len(self.docker_client.images.list())
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "cores": cpu_count
                },
                "memory": {
                    "percent": memory_percent,
                    "used_gb": round(memory_used_gb, 2),
                    "total_gb": round(memory_total_gb, 2)
                },
                "disk": {
                    "percent": round(disk_percent, 2),
                    "used_gb": round(disk_used_gb, 2),
                    "total_gb": round(disk_total_gb, 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "docker": {
                    "containers": docker_containers,
                    "images": docker_images
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}
    
    async def analyze_scaling_needs(self, region_name: str, stats: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze if a region needs scaling based on current metrics"""
        try:
            cpu_usage = stats.get("cpu_percent", 0)
            memory_usage = stats.get("memory_percent", 0)
            
            recommendations = {
                "scale_needed": False,
                "direction": None,
                "current_cpu": cpu_usage,
                "current_memory": memory_usage,
                "recommendations": []
            }
            
            # Scale up recommendations
            if cpu_usage > self.settings.SCALE_UP_CPU_THRESHOLD:
                recommendations["scale_needed"] = True
                recommendations["direction"] = "up"
                recommendations["recommendations"].append(
                    f"CPU usage at {cpu_usage:.1f}% - consider increasing CPU allocation"
                )
            
            if memory_usage > self.settings.SCALE_UP_MEMORY_THRESHOLD:
                recommendations["scale_needed"] = True
                recommendations["direction"] = "up"
                recommendations["recommendations"].append(
                    f"Memory usage at {memory_usage:.1f}% - consider increasing memory allocation"
                )
            
            # Scale down recommendations (only if not scaling up)
            if not recommendations["scale_needed"]:
                if (cpu_usage < self.settings.SCALE_DOWN_CPU_THRESHOLD and 
                    memory_usage < self.settings.SCALE_DOWN_MEMORY_THRESHOLD):
                    recommendations["scale_needed"] = True
                    recommendations["direction"] = "down"
                    recommendations["recommendations"].append(
                        f"Low resource usage (CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%) - consider reducing allocation"
                    )
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Failed to analyze scaling needs for {region_name}: {e}")
            return None