#!/usr/bin/env python3
"""
SectorWars Regional Management CLI Tool
Provides command-line interface for managing regional containers and deployments
"""

import argparse
import asyncio
import json
import sys
import logging
from typing import Dict, List, Optional
import httpx
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegionCLI:
    """Command-line interface for regional management"""
    
    def __init__(self, region_manager_url: str = "http://localhost:8081"):
        self.region_manager_url = region_manager_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def list_regions(self) -> List[Dict]:
        """List all active regions"""
        try:
            response = await self.client.get(f"{self.region_manager_url}/regions")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list regions: {e}")
            return []
    
    async def get_region_status(self, region_name: str) -> Optional[Dict]:
        """Get status of a specific region"""
        try:
            response = await self.client.get(f"{self.region_manager_url}/regions/{region_name}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Region '{region_name}' not found")
            else:
                logger.error(f"Failed to get region status: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get region status: {e}")
            return None
    
    async def provision_region(self, config: Dict) -> bool:
        """Provision a new region"""
        try:
            response = await self.client.post(
                f"{self.region_manager_url}/regions/provision",
                json=config
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Region provisioning started: {result['message']}")
            return True
        except Exception as e:
            logger.error(f"Failed to provision region: {e}")
            return False
    
    async def terminate_region(self, region_name: str) -> bool:
        """Terminate a region"""
        try:
            response = await self.client.delete(f"{self.region_manager_url}/regions/{region_name}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"Region termination started: {result['message']}")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate region: {e}")
            return False
    
    async def scale_region(self, region_name: str, cpu_cores: float, memory_gb: int, disk_gb: int) -> bool:
        """Scale region resources"""
        try:
            config = {
                "cpu_cores": cpu_cores,
                "memory_gb": memory_gb,
                "disk_gb": disk_gb
            }
            response = await self.client.post(
                f"{self.region_manager_url}/regions/{region_name}/scale",
                json=config
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Region scaling started: {result['message']}")
            return True
        except Exception as e:
            logger.error(f"Failed to scale region: {e}")
            return False
    
    async def get_metrics(self) -> Optional[Dict]:
        """Get platform-wide metrics"""
        try:
            response = await self.client.get(f"{self.region_manager_url}/metrics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return None
    
    def print_regions_table(self, regions: List[Dict]):
        """Print regions in a formatted table"""
        if not regions:
            print("No regions found.")
            return
        
        # Header
        print(f"{'Name':<20} {'Status':<12} {'Owner':<36} {'Players':<8} {'CPU%':<6} {'Mem%':<6} {'Created':<20}")
        print("-" * 120)
        
        # Rows
        for region in regions:
            name = region.get('name', 'Unknown')[:19]
            status = region.get('status', 'Unknown')[:11]
            owner = region.get('owner_id', 'Unknown')[:35]
            players = str(region.get('player_count', 0))
            
            resource_usage = region.get('resource_usage', {})
            cpu = f"{resource_usage.get('cpu_percent', 0):.1f}"
            memory = f"{resource_usage.get('memory_percent', 0):.1f}"
            
            created = region.get('created_at', 'Unknown')
            if created and created != 'Unknown':
                try:
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created = created_dt.strftime('%Y-%m-%d %H:%M')
                except:
                    created = created[:19]
            
            print(f"{name:<20} {status:<12} {owner:<36} {players:<8} {cpu:<6} {memory:<6} {created:<20}")
    
    def print_region_details(self, region: Dict):
        """Print detailed region information"""
        print(f"\n=== Region Details: {region.get('name', 'Unknown')} ===")
        print(f"Status:         {region.get('status', 'Unknown')}")
        print(f"Owner ID:       {region.get('owner_id', 'Unknown')}")
        print(f"Container ID:   {region.get('container_id', 'None')}")
        print(f"Player Count:   {region.get('player_count', 0)}")
        print(f"Created At:     {region.get('created_at', 'Unknown')}")
        
        resource_usage = region.get('resource_usage', {})
        if resource_usage:
            print(f"\n--- Resource Usage ---")
            print(f"CPU Usage:      {resource_usage.get('cpu_percent', 0):.1f}%")
            print(f"Memory Usage:   {resource_usage.get('memory_percent', 0):.1f}%")
            print(f"Memory MB:      {resource_usage.get('memory_mb', 0):.1f}")
            print(f"Network I/O:    {resource_usage.get('network_io_mb', 0):.1f} MB")
            print(f"Disk I/O:       {resource_usage.get('disk_io_mb', 0):.1f} MB")
            print(f"Uptime:         {resource_usage.get('uptime_seconds', 0)} seconds")
    
    def print_metrics(self, metrics: Dict):
        """Print platform metrics"""
        print("\n=== Platform Metrics ===")
        print(f"Total Regions:     {metrics.get('total_regions', 0)}")
        print(f"Active Regions:    {metrics.get('active_regions', 0)}")
        print(f"Total Players:     {metrics.get('total_players', 0)}")
        print(f"Avg CPU Usage:     {metrics.get('average_cpu_usage', 0):.1f}%")
        print(f"Total Memory:      {metrics.get('total_memory_usage_mb', 0):.1f} MB")
        
        regions = metrics.get('regions', [])
        if regions:
            print(f"\n--- Regional Breakdown ---")
            self.print_regions_table(regions)


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="SectorWars Regional Management CLI")
    parser.add_argument('--url', default='http://localhost:8081', 
                       help='Region Manager URL (default: http://localhost:8081)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List regions
    list_parser = subparsers.add_parser('list', help='List all regions')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table',
                           help='Output format')
    
    # Show region details
    show_parser = subparsers.add_parser('show', help='Show region details')
    show_parser.add_argument('region_name', help='Name of the region')
    show_parser.add_argument('--format', choices=['table', 'json'], default='table',
                           help='Output format')
    
    # Provision region
    provision_parser = subparsers.add_parser('provision', help='Provision a new region')
    provision_parser.add_argument('config_file', help='YAML configuration file')
    
    # Terminate region
    terminate_parser = subparsers.add_parser('terminate', help='Terminate a region')
    terminate_parser.add_argument('region_name', help='Name of the region')
    terminate_parser.add_argument('--confirm', action='store_true',
                                 help='Skip confirmation prompt')
    
    # Scale region
    scale_parser = subparsers.add_parser('scale', help='Scale region resources')
    scale_parser.add_argument('region_name', help='Name of the region')
    scale_parser.add_argument('--cpu', type=float, required=True, help='CPU cores')
    scale_parser.add_argument('--memory', type=int, required=True, help='Memory in GB')
    scale_parser.add_argument('--disk', type=int, required=True, help='Disk in GB')
    
    # Show metrics
    metrics_parser = subparsers.add_parser('metrics', help='Show platform metrics')
    metrics_parser.add_argument('--format', choices=['table', 'json'], default='table',
                               help='Output format')
    
    # Generate sample config
    config_parser = subparsers.add_parser('config', help='Generate sample region config')
    config_parser.add_argument('output_file', help='Output YAML file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle config generation (no API call needed)
    if args.command == 'config':
        sample_config = {
            'name': 'my-awesome-region',
            'owner_id': '00000000-0000-0000-0000-000000000000',
            'cpu_cores': 2.0,
            'memory_gb': 4,
            'disk_gb': 20,
            'max_players': 100,
            'governance_type': 'democracy',
            'economic_specialization': 'commerce',
            'starting_credits': 1500,
            'starting_ship': 'scout',
            'language_pack': {
                'greeting': 'Welcome to my region!',
                'currency': 'credits',
                'government': 'Democratic Council'
            },
            'aesthetic_theme': {
                'primary_color': '#1a365d',
                'secondary_color': '#2d3748',
                'style': 'modern'
            },
            'custom_rules': {
                'pvp_enabled': True,
                'trading_tax': 0.05,
                'max_ships_per_player': 10
            }
        }
        
        with open(args.output_file, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)
        
        print(f"Sample configuration written to {args.output_file}")
        return
    
    # Initialize CLI client
    cli = RegionCLI(args.url)
    
    try:
        if args.command == 'list':
            regions = await cli.list_regions()
            if args.format == 'json':
                print(json.dumps(regions, indent=2))
            else:
                cli.print_regions_table(regions)
        
        elif args.command == 'show':
            region = await cli.get_region_status(args.region_name)
            if region:
                if args.format == 'json':
                    print(json.dumps(region, indent=2))
                else:
                    cli.print_region_details(region)
        
        elif args.command == 'provision':
            with open(args.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            success = await cli.provision_region(config)
            if success:
                print(f"Region provisioning started successfully")
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.command == 'terminate':
            if not args.confirm:
                confirm = input(f"Are you sure you want to terminate region '{args.region_name}'? (y/N): ")
                if confirm.lower() != 'y':
                    print("Termination cancelled")
                    return
            
            success = await cli.terminate_region(args.region_name)
            if success:
                print(f"Region termination started successfully")
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.command == 'scale':
            success = await cli.scale_region(args.region_name, args.cpu, args.memory, args.disk)
            if success:
                print(f"Region scaling started successfully")
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.command == 'metrics':
            metrics = await cli.get_metrics()
            if metrics:
                if args.format == 'json':
                    print(json.dumps(metrics, indent=2))
                else:
                    cli.print_metrics(metrics)
    
    finally:
        await cli.close()


if __name__ == '__main__':
    asyncio.run(main())