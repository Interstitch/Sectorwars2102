# Enhanced AI Provider System Implementation Plan
*Date: 2025-05-24*

## Overview

Enhance the existing AI dialogue service to provide robust multi-provider support with dynamic fallback logic that includes sophisticated manual fallback scenarios incorporating cat mentions and ship tier difficulty.

## Current State Analysis

✅ **Libraries Already Installed:**
- `anthropic==0.18.1` 
- `openai==1.12.0`

✅ **Existing Infrastructure:**
- Comprehensive AI dialogue service with fallback logic
- Security protections (rate limiting, prompt injection detection)
- Full integration with first login experience
- AI trading and market analysis services

## Requirements

### 1. Provider Priority Enhancement
- **Primary**: OpenAI (cheaper for this use case)
- **Secondary**: Anthropic Claude (higher quality fallback)
- **Tertiary**: Enhanced manual fallback (dynamic, cat-aware)

### 2. Cat Boost Logic
Per documentation: "if the player mentions the cat in their responses, we should give them a boost/boon to persuading the guard"

### 3. Ship Tier Difficulty
Per documentation: "the guard should be more skeptical than if the player is trying to convince the guard of a light freighter (due to the higher tier vs lower tier ship)"

### 4. Manual Fallback Enhancement
- Dynamic response generation based on dialogue context
- Ship tier-based skepticism scaling
- Cat mention detection and persuasion boost
- Realistic guard personality simulation

## Technical Design

### Enhanced AI Provider Service

```python
class AIProviderService:
    """Enhanced AI provider with robust fallback chain"""
    
    def __init__(self):
        self.providers = [
            OpenAIProvider(),
            AnthropicProvider(), 
            EnhancedManualProvider()
        ]
    
    async def analyze_response(self, context: DialogueContext) -> ResponseAnalysis:
        """Try providers in order until success"""
        
    async def generate_question(self, context: DialogueContext) -> GuardResponse:
        """Generate guard question with provider fallback"""
```

### Enhanced Manual Fallback

```python
class EnhancedManualProvider:
    """Sophisticated rule-based AI simulation"""
    
    def detect_cat_mention(self, response: str) -> bool:
        """Detect cat references for persuasion boost"""
        
    def calculate_ship_tier_difficulty(self, claimed_ship: ShipType) -> float:
        """Calculate difficulty modifier based on ship value"""
        
    def generate_dynamic_response(self, context: DialogueContext) -> str:
        """Generate contextual guard responses"""
        
    def simulate_guard_personality(self, context: DialogueContext) -> GuardPersonality:
        """Simulate realistic guard behavior patterns"""
```

### Ship Tier Difficulty Matrix

| Ship Type | Tier | Base Difficulty | Guard Skepticism |
|-----------|------|----------------|------------------|
| Escape Pod | 1 | 0.3 | Low |
| Light Freighter | 2 | 0.6 | Medium |
| Scout Ship | 3 | 0.7 | Medium-High |
| Fast Courier | 3 | 0.75 | Medium-High |
| Cargo Hauler | 4 | 0.8 | High |
| Defender | 5 | 0.9 | Very High |
| Colony Ship | 6 | 0.92 | Extreme |
| Carrier | 7 | 0.95 | Maximum |

### Cat Boost Mechanics

```python
CAT_BOOST_PHRASES = [
    "cat", "orange cat", "kitten", "feline",
    "furry", "whiskers", "purr", "meow"
]

def apply_cat_boost(base_score: float, response: str) -> float:
    """Apply cat mention boost to persuasion"""
    if detect_cat_mention(response):
        return min(1.0, base_score + 0.15)  # 15% boost, capped at 1.0
    return base_score
```

## Implementation Tasks

### Phase 3: Implementation
1. ✅ Libraries already installed 
2. 🔄 Enhance AI provider service with OpenAI-first fallback
3. 🔄 Implement enhanced manual fallback provider
4. 🔄 Add cat detection and boost logic
5. 🔄 Implement ship tier difficulty scaling
6. 🔄 Update dialogue service to use new provider chain
7. 🔄 Add environment variable support for provider preferences

### Phase 4: Testing
1. Test OpenAI provider functionality
2. Test Anthropic fallback scenarios  
3. Test manual fallback with various dialogue contexts
4. Verify cat boost mechanics
5. Validate ship tier difficulty scaling
6. End-to-end testing of all provider scenarios

### Phase 5: Documentation
1. Update FIRST_LOGIN.md with new provider details
2. Document cat boost and ship tier mechanics
3. Add troubleshooting guide for provider issues

## File Changes Required

### New Files
- `src/services/ai_provider_service.py` - Enhanced provider abstraction
- `src/services/enhanced_manual_provider.py` - Sophisticated fallback logic

### Modified Files  
- `src/services/ai_dialogue_service.py` - Updated to use new provider system
- `src/services/first_login_service.py` - Integration with enhanced providers
- `src/core/config.py` - Add provider preference configuration

### Environment Variables
```bash
# Provider preferences (optional)
AI_PROVIDER_PRIMARY=openai
AI_PROVIDER_SECONDARY=anthropic
AI_PROVIDER_FALLBACK=manual

# API Keys (existing)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Success Criteria

1. ✅ OpenAI is tried first for all AI operations
2. ✅ Anthropic is used as secondary fallback
3. ✅ Enhanced manual fallback provides convincing AI simulation
4. ✅ Cat mentions provide 15% persuasion boost
5. ✅ Ship tier difficulty scales guard skepticism appropriately
6. ✅ All provider scenarios work seamlessly
7. ✅ No degradation in user experience during provider failures

## Risk Mitigation

- **API Rate Limits**: Implement exponential backoff and provider switching
- **Cost Management**: OpenAI first reduces costs while maintaining quality  
- **Fallback Quality**: Enhanced manual provider maintains immersion
- **Configuration**: Environment variables allow runtime provider control

---
*Implementation follows CLAUDE.md 6-phase methodology*