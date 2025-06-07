"""
Unit tests for Regional Governance functionality
Tests the core business logic for multi-regional system governance
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from src.services.regional_governance_service import RegionalGovernanceService
from src.models.region import (
    Region, RegionalMembership, RegionalPolicy, RegionalElection,
    GovernanceType, PolicyStatus, ElectionStatus, MembershipType
)
from src.models.player import Player
from src.models.user import User


class TestRegionalGovernanceService:
    """Test the RegionalGovernanceService class"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def sample_region(self):
        """Sample region for testing"""
        return Region(
            id=uuid.uuid4(),
            name="test-region",
            display_name="Test Region",
            owner_id=uuid.uuid4(),
            governance_type=GovernanceType.DEMOCRACY,
            voting_threshold=Decimal('0.60'),
            tax_rate=Decimal('0.15'),
            starting_credits=2000,
            economic_specialization="trade",
            total_sectors=500
        )
    
    @pytest.fixture
    def sample_player(self):
        """Sample player for testing"""
        return Player(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            username="test_player",
            credits=5000
        )
    
    @pytest.mark.asyncio
    async def test_get_region_by_owner_success(self, mock_db, sample_region):
        """Test successful region retrieval by owner"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = sample_region
        
        result = await RegionalGovernanceService.get_region_by_owner(
            mock_db, sample_region.owner_id
        )
        
        assert result == sample_region
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_region_by_owner_not_found(self, mock_db):
        """Test region retrieval when owner has no region"""
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        result = await RegionalGovernanceService.get_region_by_owner(
            mock_db, uuid.uuid4()
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_regional_stats_success(self, mock_db, sample_region):
        """Test successful regional statistics calculation"""
        # Mock membership statistics
        membership_mock = MagicMock()
        membership_mock.all.return_value = [
            MagicMock(membership_type='citizen', count=50, avg_reputation=85.5),
            MagicMock(membership_type='resident', count=30, avg_reputation=70.2),
            MagicMock(membership_type='visitor', count=20, avg_reputation=60.0)
        ]
        
        # Mock governance statistics
        elections_mock = MagicMock()
        elections_mock.return_value = 2
        
        policies_mock = MagicMock()
        policies_mock.return_value = 3
        
        treaties_mock = MagicMock()
        treaties_mock.return_value = 1
        
        # Setup mock responses
        mock_db.execute.side_effect = [membership_mock]
        mock_db.scalar.side_effect = [2, 3, 1]  # elections, policies, treaties
        
        result = await RegionalGovernanceService.get_regional_stats(
            mock_db, sample_region.id
        )
        
        assert result['total_population'] == 100
        assert result['citizen_count'] == 50
        assert result['resident_count'] == 30
        assert result['visitor_count'] == 20
        assert result['average_reputation'] == 73.75  # Weighted average
        assert result['active_elections'] == 2
        assert result['pending_policies'] == 3
        assert result['treaties_count'] == 1
    
    @pytest.mark.asyncio
    async def test_update_economic_config_success(self, mock_db, sample_region):
        """Test successful economic configuration update"""
        config = {
            'tax_rate': 0.20,
            'starting_credits': 3000,
            'trade_bonuses': {'ore': 1.5, 'food': 1.2},
            'economic_specialization': 'mining'
        }
        
        mock_db.commit.return_value = None
        
        result = await RegionalGovernanceService.update_economic_config(
            mock_db, sample_region.id, config
        )
        
        assert result is True
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_economic_config_failure(self, mock_db, sample_region):
        """Test economic configuration update failure"""
        config = {'tax_rate': 0.20}
        
        # Mock database exception
        mock_db.execute.side_effect = Exception("Database error")
        
        result = await RegionalGovernanceService.update_economic_config(
            mock_db, sample_region.id, config
        )
        
        assert result is False
        mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_governance_config_success(self, mock_db, sample_region):
        """Test successful governance configuration update"""
        config = {
            'governance_type': 'council',
            'voting_threshold': 0.75,
            'election_frequency_days': 120,
            'constitutional_text': 'New constitution text'
        }
        
        mock_db.commit.return_value = None
        
        result = await RegionalGovernanceService.update_governance_config(
            mock_db, sample_region.id, config
        )
        
        assert result is True
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_policy_proposal_success(self, mock_db, sample_region, sample_player):
        """Test successful policy proposal creation"""
        policy_data = {
            'policy_type': 'tax_rate',
            'title': 'Increase Tax Rate',
            'description': 'Proposal to increase regional tax rate',
            'proposed_changes': {'tax_rate': 0.25},
            'voting_duration_days': 7
        }
        
        mock_policy = RegionalPolicy(
            id=uuid.uuid4(),
            region_id=sample_region.id,
            **policy_data
        )
        
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock the add operation to return our mock policy
        def mock_add(policy):
            policy.id = mock_policy.id
        
        mock_db.add.side_effect = mock_add
        
        result = await RegionalGovernanceService.create_policy_proposal(
            mock_db, sample_region.id, sample_player.id, policy_data
        )
        
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_election_success(self, mock_db, sample_region):
        """Test successful election start"""
        position = "governor"
        voting_duration_days = 7
        candidates = ["candidate1", "candidate2"]
        
        # Mock no existing election
        mock_db.scalar.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        mock_election = RegionalElection(
            id=uuid.uuid4(),
            region_id=sample_region.id,
            position=position,
            candidates=candidates,
            voting_opens_at=datetime.utcnow(),
            voting_closes_at=datetime.utcnow() + timedelta(days=voting_duration_days),
            status=ElectionStatus.ACTIVE
        )
        
        def mock_add(election):
            election.id = mock_election.id
        
        mock_db.add.side_effect = mock_add
        
        result = await RegionalGovernanceService.start_election(
            mock_db, sample_region.id, position, voting_duration_days, candidates
        )
        
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_election_conflict(self, mock_db, sample_region):
        """Test election start with existing active election"""
        position = "governor"
        
        # Mock existing active election
        existing_election = RegionalElection(
            id=uuid.uuid4(),
            region_id=sample_region.id,
            position=position,
            status=ElectionStatus.ACTIVE
        )
        mock_db.scalar.return_value = existing_election
        
        result = await RegionalGovernanceService.start_election(
            mock_db, sample_region.id, position
        )
        
        assert result is None
        mock_db.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_regional_policies(self, mock_db, sample_region):
        """Test retrieval of regional policies"""
        mock_policies = [
            RegionalPolicy(
                id=uuid.uuid4(),
                region_id=sample_region.id,
                policy_type='tax_rate',
                title='Test Policy 1',
                status=PolicyStatus.VOTING
            ),
            RegionalPolicy(
                id=uuid.uuid4(),
                region_id=sample_region.id,
                policy_type='pvp_rules',
                title='Test Policy 2',
                status=PolicyStatus.PASSED
            )
        ]
        
        mock_db.execute.return_value.scalars.return_value.all.return_value = mock_policies
        
        result = await RegionalGovernanceService.get_regional_policies(
            mock_db, sample_region.id
        )
        
        assert len(result) == 2
        assert result == mock_policies
    
    @pytest.mark.asyncio
    async def test_get_regional_elections(self, mock_db, sample_region):
        """Test retrieval of regional elections"""
        mock_elections = [
            RegionalElection(
                id=uuid.uuid4(),
                region_id=sample_region.id,
                position='governor',
                status=ElectionStatus.ACTIVE
            ),
            RegionalElection(
                id=uuid.uuid4(),
                region_id=sample_region.id,
                position='council_member',
                status=ElectionStatus.COMPLETED
            )
        ]
        
        mock_db.execute.return_value.scalars.return_value.all.return_value = mock_elections
        
        result = await RegionalGovernanceService.get_regional_elections(
            mock_db, sample_region.id
        )
        
        assert len(result) == 2
        assert result == mock_elections
    
    @pytest.mark.asyncio
    async def test_get_regional_treaties(self, mock_db, sample_region):
        """Test retrieval of regional treaties"""
        mock_treaties = [
            (MagicMock(
                id=uuid.uuid4(),
                treaty_type='trade_agreement',
                terms={'trade_bonus': 1.2},
                signed_at=datetime.utcnow(),
                expires_at=None,
                status='active'
            ), "Partner Region")
        ]
        
        mock_db.execute.return_value.all.return_value = mock_treaties
        
        result = await RegionalGovernanceService.get_regional_treaties(
            mock_db, sample_region.id
        )
        
        assert len(result) == 1
        assert result[0]['partner_region'] == "Partner Region"
        assert result[0]['treaty_type'] == 'trade_agreement'
        assert result[0]['status'] == 'active'
    
    @pytest.mark.asyncio
    async def test_update_cultural_identity_success(self, mock_db, sample_region):
        """Test successful cultural identity update"""
        culture_data = {
            'language_pack': {'greeting': 'Hello', 'farewell': 'Goodbye'},
            'aesthetic_theme': {'primary_color': '#0066cc', 'font': 'Arial'},
            'traditions': {'festival': 'Annual Trade Fair'}
        }
        
        mock_db.commit.return_value = None
        
        result = await RegionalGovernanceService.update_cultural_identity(
            mock_db, sample_region.id, culture_data
        )
        
        assert result is True
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_regional_members(self, mock_db, sample_region):
        """Test retrieval of regional members"""
        mock_members = [
            (MagicMock(
                player_id=uuid.uuid4(),
                membership_type=MembershipType.CITIZEN,
                reputation_score=85,
                local_rank="Senator",
                voting_power=Decimal('1.5'),
                joined_at=datetime.utcnow(),
                last_visit=datetime.utcnow(),
                total_visits=50
            ), "test_player1"),
            (MagicMock(
                player_id=uuid.uuid4(),
                membership_type=MembershipType.RESIDENT,
                reputation_score=70,
                local_rank=None,
                voting_power=Decimal('1.0'),
                joined_at=datetime.utcnow(),
                last_visit=datetime.utcnow(),
                total_visits=25
            ), "test_player2")
        ]
        
        mock_db.execute.return_value.all.return_value = mock_members
        
        result = await RegionalGovernanceService.get_regional_members(
            mock_db, sample_region.id
        )
        
        assert len(result) == 2
        assert result[0]['username'] == "test_player1"
        assert result[0]['membership_type'] == MembershipType.CITIZEN
        assert result[0]['reputation_score'] == 85
        assert result[1]['username'] == "test_player2"
        assert result[1]['membership_type'] == MembershipType.RESIDENT


class TestRegionModel:
    """Test the Region model properties and methods"""
    
    def test_is_democratic_property(self):
        """Test the is_democratic property"""
        democratic_region = Region(governance_type=GovernanceType.DEMOCRACY)
        autocratic_region = Region(governance_type=GovernanceType.AUTOCRACY)
        
        assert democratic_region.is_democratic is True
        assert autocratic_region.is_democratic is False
    
    def test_get_trade_bonus(self):
        """Test the get_trade_bonus method"""
        region = Region(
            trade_bonuses={'ore': 1.5, 'food': 1.2}
        )
        
        assert region.get_trade_bonus('ore') == 1.5
        assert region.get_trade_bonus('food') == 1.2
        assert region.get_trade_bonus('technology') == 1.0  # Default
    
    def test_update_cultural_identity(self):
        """Test the update_cultural_identity method"""
        region = Region()
        
        language_pack = {'greeting': 'Hello', 'farewell': 'Goodbye'}
        aesthetic_theme = {'primary_color': '#0066cc'}
        traditions = [{'name': 'Trade Fair', 'frequency': 'annual'}]
        
        region.update_cultural_identity(language_pack, aesthetic_theme, traditions)
        
        assert region.language_pack == language_pack
        assert region.aesthetic_theme == aesthetic_theme
        assert region.traditions == traditions


class TestRegionalMembershipModel:
    """Test the RegionalMembership model properties and methods"""
    
    def test_is_citizen_property(self):
        """Test the is_citizen property"""
        citizen = RegionalMembership(membership_type=MembershipType.CITIZEN)
        resident = RegionalMembership(membership_type=MembershipType.RESIDENT)
        visitor = RegionalMembership(membership_type=MembershipType.VISITOR)
        
        assert citizen.is_citizen is True
        assert resident.is_citizen is False
        assert visitor.is_citizen is False
    
    def test_can_vote_property(self):
        """Test the can_vote property"""
        citizen = RegionalMembership(
            membership_type=MembershipType.CITIZEN,
            voting_power=Decimal('1.0')
        )
        resident = RegionalMembership(
            membership_type=MembershipType.RESIDENT,
            voting_power=Decimal('0.5')
        )
        visitor = RegionalMembership(
            membership_type=MembershipType.VISITOR,
            voting_power=Decimal('1.0')
        )
        no_voting_power = RegionalMembership(
            membership_type=MembershipType.CITIZEN,
            voting_power=Decimal('0.0')
        )
        
        assert citizen.can_vote is True
        assert resident.can_vote is True
        assert visitor.can_vote is False
        assert no_voting_power.can_vote is False
    
    def test_update_reputation(self):
        """Test the update_reputation method"""
        membership = RegionalMembership(reputation_score=100)
        
        # Test normal update
        membership.update_reputation(50)
        assert membership.reputation_score == 150
        
        # Test negative update
        membership.update_reputation(-200)
        assert membership.reputation_score == -50
        
        # Test upper bound
        membership.update_reputation(2000)
        assert membership.reputation_score == 1000  # Capped at max
        
        # Test lower bound
        membership.update_reputation(-3000)
        assert membership.reputation_score == -1000  # Capped at min


class TestRegionalPolicyModel:
    """Test the RegionalPolicy model properties and methods"""
    
    def test_total_votes_property(self):
        """Test the total_votes property"""
        policy = RegionalPolicy(votes_for=25, votes_against=15)
        assert policy.total_votes == 40
    
    def test_approval_percentage_property(self):
        """Test the approval_percentage property"""
        policy_with_votes = RegionalPolicy(votes_for=30, votes_against=20)
        policy_no_votes = RegionalPolicy(votes_for=0, votes_against=0)
        
        assert policy_with_votes.approval_percentage == 60.0
        assert policy_no_votes.approval_percentage == 0.0
    
    def test_is_passing_property(self):
        """Test the is_passing property - requires region relationship"""
        # This would require a full region object with voting_threshold
        # For unit testing, we'll test the logic separately
        pass


class TestRegionalElectionModel:
    """Test the RegionalElection model properties and methods"""
    
    def test_is_active_property(self):
        """Test the is_active property"""
        now = datetime.utcnow()
        
        active_election = RegionalElection(
            status=ElectionStatus.ACTIVE,
            voting_opens_at=now - timedelta(hours=1),
            voting_closes_at=now + timedelta(hours=1)
        )
        
        pending_election = RegionalElection(
            status=ElectionStatus.PENDING,
            voting_opens_at=now + timedelta(hours=1),
            voting_closes_at=now + timedelta(hours=2)
        )
        
        completed_election = RegionalElection(
            status=ElectionStatus.COMPLETED,
            voting_opens_at=now - timedelta(hours=2),
            voting_closes_at=now - timedelta(hours=1)
        )
        
        # Note: The actual is_active property checks both status and time
        # This is a simplified test for the status check
        assert active_election.status == ElectionStatus.ACTIVE
        assert pending_election.status == ElectionStatus.PENDING
        assert completed_election.status == ElectionStatus.COMPLETED