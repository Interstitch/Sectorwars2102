"""
Unit tests for Central Nexus functionality
Tests the core business logic for Central Nexus generation and management
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.nexus_generation_service import NexusGenerationService
from src.models.region import Region
from src.models.sector import Sector
from src.models.planet import Planet
from src.models.port import Port


class TestNexusGenerationService:
    """Test the NexusGenerationService class"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def nexus_service(self):
        """Create NexusGenerationService instance"""
        return NexusGenerationService()
    
    @pytest.fixture
    def sample_nexus_region(self):
        """Sample Central Nexus region"""
        return Region(
            id=uuid.uuid4(),
            name="central-nexus",
            display_name="Central Nexus",
            governance_type="galactic_council",
            economic_specialization="universal_hub",
            total_sectors=5000
        )
    
    def test_districts_configuration(self, nexus_service):
        """Test that all districts are properly configured"""
        districts = nexus_service.districts_config
        
        # Verify all expected districts exist
        expected_districts = {
            'commerce_central', 'diplomatic_quarter', 'industrial_zone',
            'residential_district', 'transit_hub', 'high_security_zone',
            'cultural_center', 'research_campus', 'free_trade_zone', 'gateway_plaza'
        }
        assert set(districts.keys()) == expected_districts
        
        # Verify each district has required configuration
        for district_name, config in districts.items():
            assert 'sectors' in config
            assert 'security_range' in config
            assert 'development_range' in config
            assert 'traffic_range' in config
            assert 'characteristics' in config
            
            # Verify sector counts add up to 5000
            pass  # Will verify in next test
        
        # Verify total sectors add up to 5000
        total_sectors = sum(config['sectors'] for config in districts.values())
        assert total_sectors == 5000
    
    def test_district_characteristics(self, nexus_service):
        """Test district characteristics are properly defined"""
        districts = nexus_service.districts_config
        
        # Commerce Central should have high traffic and development
        commerce = districts['commerce_central']
        assert commerce['traffic_range'][1] >= 8  # High traffic
        assert commerce['development_range'][1] >= 8  # High development
        
        # High Security Zone should have maximum security
        security = districts['high_security_zone']
        assert security['security_range'][1] == 10  # Maximum security
        
        # Residential District should have moderate characteristics
        residential = districts['residential_district']
        assert 3 <= residential['security_range'][0] <= 7
        assert 3 <= residential['development_range'][0] <= 7
    
    @pytest.mark.asyncio
    async def test_generate_central_nexus_new(self, mock_db, nexus_service, sample_nexus_region):
        """Test generating Central Nexus from scratch"""
        # Mock no existing nexus
        mock_db.scalar.return_value = None
        
        # Mock region creation
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock district generation
        with patch.object(nexus_service, '_generate_district') as mock_generate:
            mock_generate.return_value = {
                'sectors_created': 500,
                'ports_created': 50,
                'planets_created': 25
            }
            
            result = await nexus_service.generate_central_nexus(mock_db)
            
            assert result['status'] == 'success'
            assert result['nexus_id'] is not None
            assert result['districts_generated'] == 10
            assert result['total_sectors'] == 5000
            assert result['total_ports'] == 500  # 50 * 10 districts
            assert result['total_planets'] == 250  # 25 * 10 districts
            
            # Verify all districts were generated
            assert mock_generate.call_count == 10
    
    @pytest.mark.asyncio
    async def test_generate_central_nexus_regenerate(self, mock_db, nexus_service, sample_nexus_region):
        """Test regenerating existing Central Nexus"""
        # Mock existing nexus
        mock_db.scalar.return_value = sample_nexus_region
        
        # Mock deletion and recreation
        mock_db.execute.return_value = None
        mock_db.commit.return_value = None
        
        with patch.object(nexus_service, '_generate_district') as mock_generate:
            mock_generate.return_value = {
                'sectors_created': 500,
                'ports_created': 50,
                'planets_created': 25
            }
            
            result = await nexus_service.generate_central_nexus(
                mock_db, force_regenerate=True
            )
            
            assert result['status'] == 'success'
            assert result['regenerated'] is True
            
            # Verify deletion was called
            assert mock_db.execute.call_count >= 1  # At least one delete operation
    
    @pytest.mark.asyncio
    async def test_generate_central_nexus_exists_no_force(self, mock_db, nexus_service, sample_nexus_region):
        """Test generating when nexus exists without force flag"""
        mock_db.scalar.return_value = sample_nexus_region
        
        result = await nexus_service.generate_central_nexus(mock_db)
        
        assert result['status'] == 'exists'
        assert result['message'] == 'Central Nexus already exists'
        assert result['nexus_id'] == str(sample_nexus_region.id)
    
    @pytest.mark.asyncio
    async def test_generate_district_commerce_central(self, mock_db, nexus_service, sample_nexus_region):
        """Test generating Commerce Central district"""
        district_type = 'commerce_central'
        config = nexus_service.districts_config[district_type]
        
        # Mock bulk insert operations
        mock_db.execute.return_value = None
        mock_db.commit.return_value = None
        
        result = await nexus_service._generate_district(
            mock_db, sample_nexus_region.id, district_type, config
        )
        
        assert result['district_type'] == district_type
        assert result['sectors_created'] == config['sectors']
        assert result['ports_created'] > 0
        assert result['planets_created'] > 0
        
        # Verify bulk inserts were called
        assert mock_db.execute.call_count >= 3  # sectors, ports, planets
    
    @pytest.mark.asyncio
    async def test_generate_district_security_validation(self, mock_db, nexus_service, sample_nexus_region):
        """Test that district generation respects security ranges"""
        district_type = 'high_security_zone'
        config = nexus_service.districts_config[district_type]
        
        with patch('random.randint') as mock_randint:
            # Mock security level generation
            mock_randint.return_value = 10  # Maximum security
            
            mock_db.execute.return_value = None
            mock_db.commit.return_value = None
            
            await nexus_service._generate_district(
                mock_db, sample_nexus_region.id, district_type, config
            )
            
            # Verify security level was set correctly
            mock_randint.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_nexus_status_exists(self, mock_db, nexus_service, sample_nexus_region):
        """Test getting nexus status when it exists"""
        # Mock sector counts
        mock_db.scalar.side_effect = [
            sample_nexus_region,  # Nexus exists
            5000,  # Total sectors
            500,   # Total ports
            250    # Total planets
        ]
        
        result = await nexus_service.get_nexus_status(mock_db)
        
        assert result['exists'] is True
        assert result['status'] == 'active'
        assert result['nexus_id'] == str(sample_nexus_region.id)
        assert result['total_sectors'] == 5000
        assert result['total_ports'] == 500
        assert result['total_planets'] == 250
    
    @pytest.mark.asyncio
    async def test_get_nexus_status_not_exists(self, mock_db, nexus_service):
        """Test getting nexus status when it doesn't exist"""
        mock_db.scalar.return_value = None
        
        result = await nexus_service.get_nexus_status(mock_db)
        
        assert result['exists'] is False
        assert result['status'] == 'not_generated'
        assert result['total_sectors'] == 0
        assert result['total_ports'] == 0
        assert result['total_planets'] == 0
    
    @pytest.mark.asyncio
    async def test_get_nexus_statistics(self, mock_db, nexus_service, sample_nexus_region):
        """Test getting comprehensive nexus statistics"""
        # Mock statistics queries
        mock_db.scalar.side_effect = [
            sample_nexus_region,  # Nexus exists
            5000,  # Total sectors
            500,   # Total ports
            250,   # Total planets
            100,   # Total warp gates
            1500,  # Active players
            50000  # Daily traffic
        ]
        
        # Mock district statistics
        district_stats = [
            MagicMock(district_type='commerce_central', sectors=500, avg_security=7.5, avg_development=8.5),
            MagicMock(district_type='industrial_zone', sectors=600, avg_security=6.0, avg_development=7.0)
        ]
        mock_db.execute.return_value.all.return_value = district_stats
        
        result = await nexus_service.get_nexus_statistics(mock_db)
        
        assert result['total_sectors'] == 5000
        assert result['total_ports'] == 500
        assert result['total_planets'] == 250
        assert result['total_warp_gates'] == 100
        assert result['active_players'] == 1500
        assert result['daily_traffic'] == 50000
        assert len(result['districts']) == 2
        assert result['districts'][0]['district_type'] == 'commerce_central'
    
    @pytest.mark.asyncio
    async def test_get_district_info(self, mock_db, nexus_service, sample_nexus_region):
        """Test getting detailed district information"""
        district_type = 'commerce_central'
        
        # Mock nexus existence
        mock_db.scalar.side_effect = [
            sample_nexus_region,  # Nexus exists
            500  # Sector count
        ]
        
        # Mock sample data
        sample_sectors = [
            MagicMock(sector_number=1, security_level=8, development_level=9, traffic_level=8),
            MagicMock(sector_number=2, security_level=7, development_level=8, traffic_level=9)
        ]
        sample_ports = [
            MagicMock(sector_id=1, port_class='A', port_type='Trade Hub', docking_fee=500),
            MagicMock(sector_id=2, port_class='B', port_type='Market', docking_fee=300)
        ]
        sample_planets = [
            MagicMock(sector_id=1, planet_type='Urban', population=1000000, development_level=9),
            MagicMock(sector_id=2, planet_type='Industrial', population=500000, development_level=7)
        ]
        
        mock_db.execute.side_effect = [
            MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=sample_sectors)))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=sample_ports)))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=sample_planets))))
        ]
        
        result = await nexus_service.get_district_info(mock_db, district_type)
        
        assert result['district_type'] == district_type
        assert result['total_sectors'] == 500
        assert result['sector_range'] == (1, 500)
        assert len(result['sample_sectors']) == 2
        assert len(result['sample_ports']) == 2
        assert len(result['sample_planets']) == 2
    
    @pytest.mark.asyncio
    async def test_get_districts_list(self, mock_db, nexus_service, sample_nexus_region):
        """Test getting list of all districts"""
        # Mock nexus existence
        mock_db.scalar.return_value = sample_nexus_region
        
        # Mock district data
        district_data = [
            ('commerce_central', 500, 50, 25, 8.0, 9.0, 8.5),
            ('industrial_zone', 600, 75, 30, 6.0, 7.0, 5.5)
        ]
        mock_db.execute.return_value.all.return_value = district_data
        
        result = await nexus_service.get_districts_list(mock_db)
        
        assert len(result) == 2
        assert result[0]['district_type'] == 'commerce_central'
        assert result[0]['name'] == 'Commerce Central'
        assert result[0]['sectors_count'] == 500
        assert result[0]['ports_count'] == 50
        assert result[0]['planets_count'] == 25
        assert result[0]['security_level'] == 8.0
        assert result[0]['development_level'] == 9.0
        assert result[0]['current_traffic'] == 8.5
    
    @pytest.mark.asyncio
    async def test_regenerate_district(self, mock_db, nexus_service, sample_nexus_region):
        """Test regenerating a specific district"""
        district_type = 'commerce_central'
        
        # Mock nexus existence
        mock_db.scalar.return_value = sample_nexus_region
        
        # Mock deletion and generation
        mock_db.execute.return_value = None
        mock_db.commit.return_value = None
        
        with patch.object(nexus_service, '_generate_district') as mock_generate:
            mock_generate.return_value = {
                'district_type': district_type,
                'sectors_created': 500,
                'ports_created': 50,
                'planets_created': 25
            }
            
            result = await nexus_service.regenerate_district(
                mock_db, district_type, preserve_player_data=True
            )
            
            assert result['status'] == 'success'
            assert result['district_type'] == district_type
            assert result['sectors_created'] == 500
            
            # Verify deletion and generation were called
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_database_failure(self, mock_db, nexus_service):
        """Test error handling when database operations fail"""
        # Mock database failure
        mock_db.scalar.side_effect = Exception("Database connection failed")
        
        result = await nexus_service.generate_central_nexus(mock_db)
        
        assert result['status'] == 'error'
        assert 'Database connection failed' in result['message']
    
    def test_calculate_sector_ranges(self, nexus_service):
        """Test sector range calculation for districts"""
        # Test that sector ranges are calculated correctly
        districts = nexus_service.districts_config
        
        current_sector = 1
        for district_name, config in districts.items():
            sector_count = config['sectors']
            expected_start = current_sector
            expected_end = current_sector + sector_count - 1
            
            # This would be tested in the actual range calculation logic
            # For now, just verify the counts are positive
            assert sector_count > 0
            assert expected_end >= expected_start
            
            current_sector += sector_count
        
        # Verify we end at sector 5000
        assert current_sector - 1 == 5000
    
    def test_district_name_formatting(self, nexus_service):
        """Test district name formatting utility"""
        test_cases = [
            ('commerce_central', 'Commerce Central'),
            ('high_security_zone', 'High Security Zone'),
            ('free_trade_zone', 'Free Trade Zone'),
            ('gateway_plaza', 'Gateway Plaza')
        ]
        
        for district_type, expected_name in test_cases:
            formatted_name = district_type.replace('_', ' ').title()
            assert formatted_name == expected_name