#!/usr/bin/env python3
"""
Central Nexus Management CLI Tool
Provides command-line interface for generating and managing the Central Nexus galaxy
"""

import argparse
import asyncio
import json
import sys
import logging
from typing import Dict, List, Optional
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NexusCLI:
    """Command-line interface for Central Nexus management"""
    
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def get_nexus_status(self) -> Optional[Dict]:
        """Get Central Nexus status"""
        try:
            response = await self.client.get(f"{self.api_url}/api/v1/nexus/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get nexus status: {e}")
            return None
    
    async def generate_nexus(
        self, 
        force_regenerate: bool = False, 
        preserve_player_data: bool = True,
        districts: Optional[List[str]] = None
    ) -> bool:
        """Generate Central Nexus"""
        try:
            payload = {
                "force_regenerate": force_regenerate,
                "preserve_player_data": preserve_player_data
            }
            if districts:
                payload["districts_to_regenerate"] = districts
            
            response = await self.client.post(
                f"{self.api_url}/api/v1/nexus/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Generation started: {result['message']}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate nexus: {e}")
            return False
    
    async def get_nexus_stats(self) -> Optional[Dict]:
        """Get Central Nexus statistics"""
        try:
            response = await self.client.get(f"{self.api_url}/api/v1/nexus/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get nexus stats: {e}")
            return None
    
    async def get_districts(self) -> Optional[List[Dict]]:
        """Get list of all districts"""
        try:
            response = await self.client.get(f"{self.api_url}/api/v1/nexus/districts")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get districts: {e}")
            return None
    
    async def get_district_details(self, district_type: str) -> Optional[Dict]:
        """Get detailed information about a district"""
        try:
            response = await self.client.get(f"{self.api_url}/api/v1/nexus/districts/{district_type}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get district details: {e}")
            return None
    
    async def regenerate_district(
        self, 
        district_type: str, 
        preserve_player_data: bool = True
    ) -> bool:
        """Regenerate a specific district"""
        try:
            response = await self.client.post(
                f"{self.api_url}/api/v1/nexus/districts/{district_type}/regenerate",
                params={"preserve_player_data": preserve_player_data}
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"District regeneration started: {result['message']}")
            return True
        except Exception as e:
            logger.error(f"Failed to regenerate district: {e}")
            return False
    
    def print_status(self, status: Dict):
        """Print nexus status in a formatted way"""
        print(f"\n=== Central Nexus Status ===")
        print(f"Exists:          {'Yes' if status.get('exists') else 'No'}")
        print(f"Status:          {status.get('status', 'Unknown')}")
        
        if status.get('exists'):
            print(f"Nexus ID:        {status.get('nexus_id', 'Unknown')}")
            print(f"Created:         {status.get('created_at', 'Unknown')}")
            print(f"Total Sectors:   {status.get('total_sectors', 0):,}")
            print(f"Total Ports:     {status.get('total_ports', 0):,}")
            print(f"Total Planets:   {status.get('total_planets', 0):,}")
            print(f"Governance:      {status.get('governance_type', 'Unknown')}")
            print(f"Specialization:  {status.get('economic_specialization', 'Unknown')}")
    
    def print_stats(self, stats: Dict):
        """Print comprehensive statistics"""
        print(f"\n=== Central Nexus Statistics ===")
        print(f"Total Sectors:   {stats.get('total_sectors', 0):,}")
        print(f"Total Ports:     {stats.get('total_ports', 0):,}")
        print(f"Total Planets:   {stats.get('total_planets', 0):,}")
        print(f"Total Warp Gates: {stats.get('total_warp_gates', 0):,}")
        print(f"Active Players:  {stats.get('active_players', 0):,}")
        print(f"Daily Traffic:   {stats.get('daily_traffic', 0):,}")
        
        districts = stats.get('districts', [])
        if districts:
            print(f"\n--- District Breakdown ---")
            print(f"{'District':<20} {'Sectors':<8} {'Security':<8} {'Development':<12}")
            print("-" * 60)
            
            for district in districts:
                district_name = district.get('district_type', '').replace('_', ' ').title()
                sectors = district.get('sectors', 0)
                security = district.get('avg_security', 0)
                development = district.get('avg_development', 0)
                
                print(f"{district_name:<20} {sectors:<8} {security:<8.1f} {development:<12.1f}")
    
    def print_districts(self, districts: List[Dict]):
        """Print districts table"""
        print(f"\n=== Central Nexus Districts ===")
        print(f"{'District':<20} {'Sectors':<8} {'Ports':<8} {'Planets':<8} {'Security':<8} {'Traffic':<8}")
        print("-" * 80)
        
        for district in districts:
            name = district.get('name', '')[:19]
            sectors = district.get('sectors_count', 0)
            ports = district.get('ports_count', 0)
            planets = district.get('planets_count', 0)
            security = district.get('security_level', 0)
            traffic = district.get('current_traffic', 0)
            
            print(f"{name:<20} {sectors:<8} {ports:<8} {planets:<8} {security:<8} {traffic:<8}")
    
    def print_district_details(self, details: Dict):
        """Print detailed district information"""
        district_type = details.get('district_type', 'Unknown')
        print(f"\n=== District Details: {district_type.replace('_', ' ').title()} ===")
        print(f"District Type:    {district_type}")
        print(f"Total Sectors:    {details.get('total_sectors', 0):,}")
        print(f"Sector Range:     {details.get('sector_range', (0, 0))[0]:,} - {details.get('sector_range', (0, 0))[1]:,}")
        
        # Sample sectors
        sample_sectors = details.get('sample_sectors', [])
        if sample_sectors:
            print(f"\n--- Sample Sectors ---")
            print(f"{'Sector':<8} {'Security':<8} {'Development':<12} {'Traffic':<8}")
            print("-" * 40)
            
            for sector in sample_sectors[:5]:  # Show first 5
                sector_num = sector.get('sector_number', 0)
                security = sector.get('security_level', 0)
                development = sector.get('development_level', 0)
                traffic = sector.get('traffic_level', 0)
                
                print(f"{sector_num:<8} {security:<8} {development:<12} {traffic:<8}")
        
        # Sample ports
        sample_ports = details.get('sample_ports', [])
        if sample_ports:
            print(f"\n--- Sample Ports ---")
            print(f"{'Sector':<8} {'Class':<6} {'Type':<20} {'Fee':<8}")
            print("-" * 50)
            
            for port in sample_ports[:5]:  # Show first 5
                sector_id = port.get('sector_id', 0)
                port_class = port.get('port_class', 'Unknown')
                port_type = port.get('port_type', 'Unknown')[:19]
                docking_fee = port.get('docking_fee', 0)
                
                print(f"{sector_id:<8} {port_class:<6} {port_type:<20} {docking_fee:<8}")
        
        # Sample planets
        sample_planets = details.get('sample_planets', [])
        if sample_planets:
            print(f"\n--- Sample Planets ---")
            print(f"{'Sector':<8} {'Type':<15} {'Population':<12} {'Development':<12}")
            print("-" * 55)
            
            for planet in sample_planets[:5]:  # Show first 5
                sector_id = planet.get('sector_id', 0)
                planet_type = planet.get('planet_type', 'Unknown')[:14]
                population = planet.get('population', 0)
                development = planet.get('development_level', 0)
                
                print(f"{sector_id:<8} {planet_type:<15} {population:<12:,} {development:<12}")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Central Nexus Management CLI")
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='API base URL (default: http://localhost:8080)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show Central Nexus status')
    status_parser.add_argument('--format', choices=['table', 'json'], default='table',
                              help='Output format')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate Central Nexus')
    generate_parser.add_argument('--force', action='store_true',
                                help='Force regeneration if nexus exists')
    generate_parser.add_argument('--no-preserve-data', action='store_true',
                                help='Do not preserve player data during regeneration')
    generate_parser.add_argument('--districts', nargs='+',
                                help='Specific districts to regenerate')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show comprehensive statistics')
    stats_parser.add_argument('--format', choices=['table', 'json'], default='table',
                             help='Output format')
    
    # Districts command
    districts_parser = subparsers.add_parser('districts', help='List all districts')
    districts_parser.add_argument('--format', choices=['table', 'json'], default='table',
                                 help='Output format')
    
    # District details command
    district_parser = subparsers.add_parser('district', help='Show district details')
    district_parser.add_argument('district_type', help='District type to show')
    district_parser.add_argument('--format', choices=['table', 'json'], default='table',
                                help='Output format')
    
    # Regenerate district command
    regen_parser = subparsers.add_parser('regenerate', help='Regenerate a district')
    regen_parser.add_argument('district_type', help='District type to regenerate')
    regen_parser.add_argument('--no-preserve-data', action='store_true',
                             help='Do not preserve player data during regeneration')
    regen_parser.add_argument('--confirm', action='store_true',
                             help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI client
    cli = NexusCLI(args.url)
    
    try:
        if args.command == 'status':
            status = await cli.get_nexus_status()
            if status:
                if args.format == 'json':
                    print(json.dumps(status, indent=2))
                else:
                    cli.print_status(status)
        
        elif args.command == 'generate':
            preserve_data = not args.no_preserve_data
            success = await cli.generate_nexus(
                force_regenerate=args.force,
                preserve_player_data=preserve_data,
                districts=args.districts
            )
            if success:
                print("Central Nexus generation started successfully")
                print("This process takes 15-20 minutes. Use 'status' command to check progress.")
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.command == 'stats':
            stats = await cli.get_nexus_stats()
            if stats:
                if args.format == 'json':
                    print(json.dumps(stats, indent=2))
                else:
                    cli.print_stats(stats)
        
        elif args.command == 'districts':
            districts = await cli.get_districts()
            if districts:
                if args.format == 'json':
                    print(json.dumps(districts, indent=2))
                else:
                    cli.print_districts(districts)
        
        elif args.command == 'district':
            details = await cli.get_district_details(args.district_type)
            if details:
                if args.format == 'json':
                    print(json.dumps(details, indent=2))
                else:
                    cli.print_district_details(details)
        
        elif args.command == 'regenerate':
            if not args.confirm:
                confirm = input(f"Are you sure you want to regenerate district '{args.district_type}'? (y/N): ")
                if confirm.lower() != 'y':
                    print("Regeneration cancelled")
                    return
            
            preserve_data = not args.no_preserve_data
            success = await cli.regenerate_district(args.district_type, preserve_data)
            if success:
                print(f"District {args.district_type} regeneration started successfully")
                sys.exit(0)
            else:
                sys.exit(1)
    
    finally:
        await cli.close()


if __name__ == '__main__':
    asyncio.run(main())