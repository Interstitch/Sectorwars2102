# Phase 2: Regional Management Systems (Weeks 5-8)

*Status: NOT STARTED*  
*Duration: 4 weeks*  
*Dependencies: Phase 1 Complete*  
*Risk Level: MEDIUM - New feature development*

## 🎯 Phase Overview

Phase 2 implements the core regional management infrastructure, enabling the creation, provisioning, and administration of new 500-sector regions. This phase introduces the Regional Governor role and associated management tools.

## 📋 Week-by-Week Breakdown

### Week 5-6: Regional Provisioning Infrastructure

#### Automated Region Creation System
```python
class RegionalProvisioningService:
    """Handles automated creation and setup of new regions"""
    
    async def create_region(
        self,
        name: str,
        display_name: str,
        owner_id: str,
        config: RegionConfig
    ) -> Region:
        """Create a new 500-sector region with standard structure"""
        
        # Validate uniqueness and ownership
        await self._validate_region_creation(name, owner_id)
        
        # Create region record
        region = await self._create_region_record(
            name=name,
            display_name=display_name,
            owner_id=owner_id,
            config=config
        )
        
        # Generate spatial structure
        await self._generate_region_space(region)
        
        # Set up infrastructure
        await self._setup_regional_infrastructure(region)
        
        # Initialize economy
        await self._initialize_regional_economy(region)
        
        # Create nexus connection
        await self._establish_nexus_connection(region)
        
        # Activate region
        await self._activate_region(region)
        
        return region
    
    async def _generate_region_space(self, region: Region):
        """Generate 500-sector region with proper structure"""
        
        # Define cluster boundaries
        clusters = {
            'federation': range(1, 8),      # Sectors 1-7 (safe zone)
            'border': range(8, 250),        # Sectors 8-249 (main area)
            'frontier': range(250, 501)     # Sectors 250-500 (remote)
        }
        
        # Generate sectors with appropriate characteristics
        for cluster_name, sector_range in clusters.items():
            for sector_num in sector_range:
                await self._create_sector(
                    region_id=region.id,
                    sector_id=sector_num,
                    cluster=cluster_name,
                    properties=self._get_cluster_properties(cluster_name)
                )
        
        # Create natural warp tunnels within region
        await self._generate_warp_network(region, internal=True)
        
        # Place ports and planets according to distribution rules
        await self._distribute_resources(region)
```

#### Regional Configuration Management
```python
@dataclass
class RegionConfig:
    """Configuration options for regional customization"""
    
    # Economic settings
    tax_rate: float = 0.10  # 10% default tax
    trade_bonus: float = 1.0  # No bonus by default
    starting_credits: int = 1000
    starting_turns: int = 100
    starting_ship: str = "scout"
    
    # Gameplay settings
    pvp_enabled: bool = True
    pvp_protection_hours: int = 72  # New player protection
    max_ships_per_player: int = 10
    colonization_enabled: bool = True
    
    # Theme and flavor
    theme: str = "standard"
    faction_names: Dict[str, str] = field(default_factory=dict)
    port_name_prefix: str = ""
    welcome_message: str = "Welcome to our region!"
    
    # Governance
    immigration_policy: str = "open"  # open, approval, closed
    minimum_reputation: int = 0
    banned_players: List[str] = field(default_factory=list)
    moderator_ids: List[str] = field(default_factory=list)

class RegionalCustomizationService:
    """Handles regional customization within game framework"""
    
    async def apply_customization(self, region: Region, config: RegionConfig):
        """Apply customization while maintaining game balance"""
        
        # Validate configuration within allowed bounds
        validated_config = await self._validate_config(config)
        
        # Apply economic modifiers
        await self._apply_economic_rules(region, validated_config)
        
        # Customize factions and naming
        await self._customize_factions(region, validated_config)
        
        # Set governance rules
        await self._configure_governance(region, validated_config)
        
        # Create custom content
        await self._create_regional_content(region, validated_config)
```

#### Subscription and Billing Integration
```python
class RegionalSubscriptionService:
    """Manages regional ownership subscriptions"""
    
    async def create_subscription(
        self,
        user_id: str,
        region_name: str,
        payment_method: PaymentMethod
    ) -> Subscription:
        """Create regional ownership subscription"""
        
        # Create Stripe subscription
        stripe_subscription = await stripe.Subscription.create(
            customer=user_id,
            items=[{
                'price': REGIONAL_SUBSCRIPTION_PRICE_ID,  # $25/month
                'quantity': 1,
                'metadata': {
                    'region_name': region_name,
                    'type': 'regional_ownership'
                }
            }],
            payment_method=payment_method,
            metadata={
                'user_id': user_id,
                'region_name': region_name
            }
        )
        
        # Create internal subscription record
        subscription = await self._create_subscription_record(
            user_id=user_id,
            stripe_subscription_id=stripe_subscription.id,
            region_name=region_name,
            status='active'
        )
        
        # Trigger region provisioning
        await self._trigger_provisioning(subscription)
        
        return subscription
    
    async def handle_subscription_webhook(self, event: stripe.Event):
        """Handle Stripe subscription lifecycle events"""
        
        if event.type == 'customer.subscription.created':
            await self._handle_subscription_created(event.data.object)
        elif event.type == 'customer.subscription.updated':
            await self._handle_subscription_updated(event.data.object)
        elif event.type == 'customer.subscription.deleted':
            await self._handle_subscription_cancelled(event.data.object)
        elif event.type == 'invoice.payment_failed':
            await self._handle_payment_failed(event.data.object)
```

### Week 7-8: Regional Administration Interface

#### Admin UI Regional Management
```typescript
// Regional selection and management interface
interface RegionalAdminDashboard {
  // Galaxy Administrator view
  galaxyAdmin: {
    regionList: RegionListView;
    regionCreation: RegionCreationWizard;
    regionMonitoring: RegionHealthDashboard;
    governorManagement: GovernorManagementPanel;
    nexusManagement: NexusControlPanel;
  };
  
  // Regional Governor view
  regionalGovernor: {
    dashboard: GovernorDashboard;
    economyManager: EconomyControlPanel;
    playerManager: PlayerManagementPanel;
    contentEditor: ContentCreationTools;
    analyticsViewer: RegionalAnalytics;
  };
}

// Region creation wizard component
const RegionCreationWizard: React.FC = () => {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState<RegionConfig>({});
  
  const steps = [
    { title: 'Basic Info', component: BasicInfoStep },
    { title: 'Economic Settings', component: EconomicSettingsStep },
    { title: 'Gameplay Rules', component: GameplayRulesStep },
    { title: 'Theme & Flavor', component: ThemeCustomizationStep },
    { title: 'Review & Create', component: ReviewCreateStep }
  ];
  
  return (
    <WizardContainer>
      <WizardProgress current={step} total={steps.length} />
      <WizardContent>
        {React.createElement(steps[step - 1].component, {
          config,
          onUpdate: setConfig,
          onNext: () => setStep(step + 1),
          onBack: () => setStep(step - 1),
          onSubmit: handleRegionCreation
        })}
      </WizardContent>
    </WizardContainer>
  );
};
```

#### Regional Governor Control Panel
```typescript
// Comprehensive governor dashboard
const GovernorDashboard: React.FC<{regionId: string}> = ({ regionId }) => {
  const { region, loading } = useRegion(regionId);
  const { metrics } = useRegionalMetrics(regionId);
  
  if (loading) return <LoadingSpinner />;
  
  return (
    <DashboardLayout>
      <DashboardHeader>
        <h1>{region.displayName} Control Center</h1>
        <RegionStatus status={region.status} />
      </DashboardHeader>
      
      <MetricsGrid>
        <MetricCard
          title="Active Players"
          value={metrics.activePlayers}
          change={metrics.playerGrowth}
          icon={<UsersIcon />}
        />
        <MetricCard
          title="Economic Health"
          value={`${metrics.economicScore}/100`}
          status={getEconomicStatus(metrics.economicScore)}
          icon={<EconomyIcon />}
        />
        <MetricCard
          title="Monthly Revenue"
          value={`$${metrics.monthlyRevenue}`}
          subtext={`Max: $25 (${metrics.payingPlayers} subscribers)`}
          icon={<RevenueIcon />}
        />
        <MetricCard
          title="Satisfaction"
          value={`${metrics.playerSatisfaction}%`}
          trend={metrics.satisfactionTrend}
          icon={<SatisfactionIcon />}
        />
      </MetricsGrid>
      
      <QuickActions>
        <ActionButton onClick={() => navigate('/economy')}>
          Manage Economy
        </ActionButton>
        <ActionButton onClick={() => navigate('/players')}>
          Player Management
        </ActionButton>
        <ActionButton onClick={() => navigate('/content')}>
          Create Content
        </ActionButton>
        <ActionButton onClick={() => navigate('/events')}>
          Schedule Event
        </ActionButton>
      </QuickActions>
      
      <DashboardPanels>
        <RecentActivityFeed regionId={regionId} />
        <TopPlayersLeaderboard regionId={regionId} />
        <EconomicIndicators regionId={regionId} />
        <UpcomingEvents regionId={regionId} />
      </DashboardPanels>
    </DashboardLayout>
  );
};
```

#### Economic Management Tools
```typescript
interface EconomyControlPanel {
  // Tax configuration
  taxSettings: {
    tradeTax: number;        // 0-25%
    dockingFees: number;     // 0-100 credits
    planetTax: number;       // 0-20%
    combatTax: number;       // 0-15%
  };
  
  // Trade policies
  tradePolicies: {
    priceModifiers: Map<ResourceType, number>;
    bannedGoods: ResourceType[];
    tradeAgreements: RegionalTradeAgreement[];
    customsRules: CustomsPolicy[];
  };
  
  // Banking configuration
  bankingSettings: {
    interestRate: number;    // -5% to +10%
    loanAvailable: boolean;
    maxLoanAmount: number;
    insuranceRates: Map<AssetType, number>;
  };
  
  // Economic events
  economicEvents: {
    scheduled: EconomicEvent[];
    templates: EventTemplate[];
    history: PastEvent[];
  };
}

// Economic management implementation
const EconomyManager: React.FC = () => {
  const [taxSettings, setTaxSettings] = useState<TaxSettings>({});
  const [showProjection, setShowProjection] = useState(false);
  
  const handleTaxChange = async (taxType: string, value: number) => {
    // Validate within allowed ranges
    const validated = validateTaxRate(taxType, value);
    
    // Show economic projection
    const projection = await calculateEconomicImpact({
      ...taxSettings,
      [taxType]: validated
    });
    
    setShowProjection(true);
    setProjectedImpact(projection);
  };
  
  return (
    <EconomyPanel>
      <TaxConfiguration
        settings={taxSettings}
        onChange={handleTaxChange}
        limits={TAX_LIMITS}
      />
      
      {showProjection && (
        <EconomicProjection
          current={currentMetrics}
          projected={projectedImpact}
          onApply={applyTaxChanges}
          onCancel={() => setShowProjection(false)}
        />
      )}
      
      <TradeConfiguration
        policies={tradePolicies}
        onUpdate={updateTradePolicies}
      />
      
      <BankingConfiguration
        settings={bankingSettings}
        onUpdate={updateBankingSettings}
      />
      
      <EconomicEventScheduler
        events={economicEvents}
        onSchedule={scheduleEconomicEvent}
      />
    </EconomyPanel>
  );
};
```

## 🔧 Technical Implementation Details

### Regional Lifecycle Management
```python
class RegionalLifecycleManager:
    """Manages the complete lifecycle of regions"""
    
    async def provision_region(self, subscription: Subscription):
        """Provision new region after payment confirmed"""
        try:
            # Create region
            region = await self.provisioning_service.create_region(
                name=subscription.region_name,
                owner_id=subscription.user_id,
                config=subscription.initial_config
            )
            
            # Set up infrastructure
            await self._setup_infrastructure(region)
            
            # Initialize services
            await self._initialize_services(region)
            
            # Notify owner
            await self._notify_owner_ready(region)
            
            # Update subscription
            await self._update_subscription_active(subscription, region)
            
        except Exception as e:
            await self._handle_provisioning_failure(subscription, e)
    
    async def suspend_region(self, region_id: str, reason: str):
        """Suspend region (payment failure, violation, etc)"""
        region = await self.get_region(region_id)
        
        # Notify players
        await self._broadcast_suspension_notice(region, reason)
        
        # Disable new logins
        await self._disable_region_access(region)
        
        # Give grace period
        await self._schedule_shutdown(region, grace_hours=72)
        
        # Update status
        region.status = 'suspended'
        await self.save_region(region)
    
    async def delete_region(self, region_id: str):
        """Permanently delete region"""
        region = await self.get_region(region_id)
        
        # Export player data
        await self._export_player_assets(region)
        
        # Transfer players to refugee status
        await self._evacuate_players(region)
        
        # Archive region data
        await self._archive_region(region)
        
        # Delete spatial data
        await self._delete_sectors(region)
        
        # Clean up infrastructure
        await self._cleanup_infrastructure(region)
        
        # Mark deleted
        region.status = 'deleted'
        region.deleted_at = datetime.utcnow()
        await self.save_region(region)
```

### Performance Monitoring
```python
class RegionalPerformanceMonitor:
    """Monitors performance across all regions"""
    
    async def collect_metrics(self):
        """Collect performance metrics for all regions"""
        regions = await self.get_all_active_regions()
        
        for region in regions:
            metrics = await self._collect_region_metrics(region)
            await self._store_metrics(region.id, metrics)
            
            # Check performance thresholds
            if metrics.response_time > 500:  # ms
                await self._alert_performance_issue(region, metrics)
            
            if metrics.error_rate > 0.01:  # 1%
                await self._alert_error_rate(region, metrics)
    
    async def _collect_region_metrics(self, region: Region):
        return RegionMetrics(
            response_time=await self._measure_response_time(region),
            error_rate=await self._calculate_error_rate(region),
            active_players=await self._count_active_players(region),
            database_load=await self._measure_db_load(region),
            memory_usage=await self._measure_memory(region)
        )
```

## ✅ Acceptance Criteria

### Provisioning Requirements
- [ ] Regions created within 60 seconds of payment
- [ ] All 500 sectors properly generated
- [ ] Federation/Border/Frontier structure correct
- [ ] Warp gate to Central Nexus established
- [ ] Initial resources distributed properly

### Management Requirements
- [ ] Governor dashboard fully functional
- [ ] Economic controls within balance limits
- [ ] Player management tools operational
- [ ] Content creation interface working
- [ ] Analytics dashboard accurate

### Billing Requirements
- [ ] Stripe integration complete
- [ ] Subscription lifecycle handled
- [ ] Payment failures gracefully managed
- [ ] Revenue sharing calculated correctly
- [ ] Billing dashboard accurate

### Quality Requirements
- [ ] Regional isolation maintained
- [ ] Performance targets met
- [ ] Security audit passed
- [ ] UI/UX testing complete
- [ ] Documentation updated

## 🚀 Implementation Checklist

### Week 5-6 Tasks
- [ ] Build region provisioning service
- [ ] Implement 500-sector generation
- [ ] Create resource distribution algorithm
- [ ] Build configuration management
- [ ] Integrate subscription billing
- [ ] Test automated provisioning

### Week 7-8 Tasks
- [ ] Create governor dashboard UI
- [ ] Build economic management tools
- [ ] Implement player management interface
- [ ] Create content editor
- [ ] Build analytics dashboard
- [ ] Complete integration testing

### Documentation
- [ ] Regional creation guide
- [ ] Governor handbook
- [ ] Economic management guide
- [ ] API documentation updates
- [ ] Billing integration docs

## 🎯 Success Metrics

### Performance Targets
- Region creation: < 60 seconds
- Dashboard load time: < 2 seconds
- API response time: < 200ms
- Concurrent regions: 100+

### Business Targets
- Provisioning success rate: > 99%
- Governor satisfaction: > 4.5/5
- Revenue accuracy: 100%
- Churn rate: < 5% monthly

## 🚨 Risk Mitigation

### High-Risk Areas
1. **Billing Integration**: Extensive testing, manual fallbacks
2. **Region Generation**: Performance optimization, caching
3. **Governor Tools**: Gradual feature rollout, feedback loops
4. **Economic Balance**: Simulation testing, adjustment tools

### Contingency Plans
- Manual provisioning backup process
- Governor support hotline
- Economic intervention tools
- Emergency region suspension

---

*Phase 2 enables the core business model by allowing entrepreneurial players to create and manage their own regions.*