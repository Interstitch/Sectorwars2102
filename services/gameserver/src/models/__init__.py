from src.models.user import User
from src.models.admin_credentials import AdminCredentials
from src.models.player_credentials import PlayerCredentials
from src.models.oauth_account import OAuthAccount
from src.models.refresh_token import RefreshToken
from src.models.player import Player
from src.models.ship import Ship, ShipSpecification, ShipType, FailureType, UpgradeType, InsuranceType, ShipStatus
from src.models.reputation import Reputation, TeamReputation, ReputationLevel
from src.models.team import Team, TeamReputationHandling, TeamRecruitmentStatus
from src.models.team_member import TeamMember, TeamRole
from src.models.planet import Planet, player_planets
from src.models.port import Port, player_ports

# New models
from src.models.galaxy import Galaxy, GalaxyRegion, RegionType
from src.models.region import Region, RegionalMembership, RegionalPolicy, RegionalElection, RegionalVote, RegionalTreaty, InterRegionalTravel
from src.models.cluster import Cluster, ClusterType
from src.models.sector import Sector, SectorType, sector_warps
from src.models.warp_tunnel import WarpTunnel, WarpTunnelType, WarpTunnelStatus
from src.models.resource import Resource, ResourceType, ResourceQuality, Market
from src.models.combat_log import CombatLog, CombatStats
from src.models.game_event import GameEvent, EventTemplate, EventEffect, EventParticipation
from src.models.market_transaction import MarketTransaction as EnhancedMarketTransaction, MarketPrice, PriceHistory, EconomicMetrics, PriceAlert
from src.models.genesis_device import GenesisDevice, GenesisType, GenesisStatus, PlanetFormation
from src.models.first_login import FirstLoginSession, DialogueExchange, PlayerFirstLoginState, ShipChoice, NegotiationSkillLevel, DialogueOutcome
from src.models.ai_trading import AIMarketPrediction, PlayerTradingProfile, AIRecommendation, AIModelPerformance, AITrainingData
from src.models.audit_log import AuditLog
from src.models.message import Message
from src.models.faction import Faction, FactionType, FactionMission
from src.models.drone import Drone, DroneType, DroneStatus, DroneDeployment, DroneCombat
from src.models.fleet import Fleet, FleetMember, FleetBattle, FleetBattleCasualty, FleetRole, FleetStatus, BattlePhase
from src.models.mfa import MFASecret, MFAAttempt
from src.models.translation import (
    Language, TranslationNamespace, TranslationKey, 
    UserLanguagePreference, TranslationAuditLog, TranslationProgress
)