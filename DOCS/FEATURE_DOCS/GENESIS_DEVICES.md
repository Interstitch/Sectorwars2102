# Genesis Devices — Sector Wars 2102

This document describes the Genesis Device system for Sector Wars 2102, including acquisition, usage, ship integration, UI/UX, and security. Genesis Devices are the only way to create new planets.

## Overview

Genesis Devices are rare, highly advanced technological marvels that allow players to create new planets in empty sectors. These legendary devices harness quantum energy to transform space matter into habitable worlds. They are the pinnacle of scientific achievement, extremely difficult to obtain, and represent one of the most significant investments a player can make in the game.

## Acquisition & Storage

- **Purchase Location:** Genesis Devices can only be purchased at special Class-9 Research Stations, which are exceptionally rare in the galaxy.
- **Cost:** 25,000 credits per device, making them a significant but achievable investment for dedicated players.
- **Limited Stock:** Research Stations stock only 1-3 Genesis Devices at a time, with a 7-day refresh period.
- **Ship Capacity:**
  - Each ship type has a maximum Genesis Device capacity (`maxGenesis`).
  - Most standard ships cannot carry Genesis Devices due to their specialized containment requirements.
  - Only Colony Ships and Carriers can transport multiple devices, with Defenders having limited capacity.
  - See ship data model for details.
- **Purchase Rules:**
  - Cannot exceed ship's `maxGenesis`.
  - Attempting to purchase more than available space results in an error.
  - Players must have a minimum reputation level with the Federation to purchase Genesis Devices.

## Usage — Planet Creation

- **Requirement:** Genesis Devices are required to create a new planet:
  - **Basic Planet Creation:** Requires 1 Genesis Device
  - **Enhanced Planet Creation:** 3 Genesis Devices (increases chances of better planet types)
  - **Advanced Planet Creation:** 5 Genesis Devices on a Colony Ship (sacrifices the ship)
- **Process Types:**
  - **Standard Genesis (1 or 3 devices):**
    1. Player must be in an empty, non-protected sector
    2. Player must have the required number of Genesis Devices on their ship
    3. Player initiates the Genesis Sequence, which takes 48 real-time hours to complete
    4. Player must remain in the sector during the entire Genesis Sequence
    5. Upon completion, the Genesis Devices are consumed, and a basic planet is generated
    6. The sequence can be aborted, but all Genesis Devices are lost if canceled mid-process
  - **Colony Ship Sacrifice (5 devices):**
    1. Player must be in an empty, non-protected sector
    2. Player must have a Colony Ship with exactly 5 Genesis Devices
    3. Player initiates the Advanced Genesis Sequence
    4. The Colony Ship and all Genesis Devices are immediately consumed
    5. A new planet is instantly created with a Settlement-level colony (Phase 2)
    6. The planet starts with 5,000 population and a Level 2 Citadel
    7. This method bypasses the 48-hour terraforming process
- **Protected Sectors:** Planets cannot be created in protected sectors (e.g., sectors 1–7) or sectors within 5 jumps of Federation Space.
- **Randomization:** The resulting planet type is completely random and cannot be influenced except by using more Genesis Devices (see probabilities below).
- **Genesis Teams:** Players can form temporary "Genesis Teams" where multiple players contribute Genesis Devices to the creation process, sharing ownership of the resulting planet.

## Ship Integration

- **Ship Model Fields:**
  - `genesis`: Current Genesis Device count.
  - `maxGenesis`: Maximum Genesis Devices the ship can carry.
- **Ship Specialization:**
  - **Colony Ship:** Can carry up to 5 Genesis Devices, leveraging its terraforming expertise.
  - **Carrier:** Can carry up to 5 Genesis Devices, using its extensive storage capabilities.
  - **Defender:** Can carry up to 3 Genesis Devices, with specialized shielding systems.
  - **Cargo Hauler:** Can carry up to 2 Genesis Devices.
  - **Warp Jumper:** Can carry 1 Genesis Device using quantum field stabilization.
- **Strategic Choice:** Players dedicated to planet creation must invest in Colony Ships for maximum Genesis capacity.
- **Spatial Requirements:** Genesis Devices require specialized containment fields that consume significant ship space:
  - Each Genesis Device occupies the equivalent of 50 cargo units.
  - Ships carrying Genesis Devices suffer a 20% reduction in maximum travel speed due to safety protocols.
- **Equipment Competition:** Genesis Devices compete with other equipment for ship resources:
  - Ships carrying Genesis Devices have a 50% reduction in drone capacity.
  - Maximum hull and shield points are reduced by 100 points each when carrying Genesis Devices due to power requirements.

## Planet Type Probabilities

### Basic Genesis (1 Device)

| Planet Type | Description | Probability |
|-------------|-------------|-------------|
| D_CLASS     | Barren, rocky world with minimal resources | 30% |
| K_CLASS     | Desert planet with limited habitability | 25% |
| L_CLASS     | Mountainous with basic vegetation | 20% |
| M_CLASS     | Earth-like world, fully habitable | 10% |
| H_CLASS     | Volcanic planet with valuable mineral deposits | 8% |
| C_CLASS     | Ice world with subsurface resources | 7% |

### Enhanced Genesis (3 Devices)

| Planet Type | Description | Probability |
|-------------|-------------|-------------|
| D_CLASS     | Barren, rocky world with minimal resources | 15% |
| K_CLASS     | Desert planet with limited habitability | 20% |
| L_CLASS     | Mountainous with basic vegetation | 25% |
| M_CLASS     | Earth-like world, fully habitable | 20% |
| H_CLASS     | Volcanic planet with valuable mineral deposits | 10% |
| C_CLASS     | Ice world with subsurface resources | 10% |

### Advanced Genesis (5 Devices)

| Planet Type | Description | Probability |
|-------------|-------------|-------------|
| D_CLASS     | Barren, rocky world with minimal resources | 5% |
| K_CLASS     | Desert planet with limited habitability | 15% |
| L_CLASS     | Mountainous with basic vegetation | 20% |
| M_CLASS     | Earth-like world, fully habitable | 30% |
| H_CLASS     | Volcanic planet with valuable mineral deposits | 15% |
| C_CLASS     | Ice world with subsurface resources | 15% |

- Planet type is completely random but influenced by the number of Genesis Devices used
- Even with Advanced Genesis, there's no guarantee of getting an M-Class planet
- The risk-reward nature of Genesis Devices creates dynamic gameplay decisions

## UI/UX

- **Purchase Interface:**
  - Displays dramatic visuals emphasizing the rarity and power of Genesis Devices.
  - Shows ship's Genesis capacity, current count, and available space.
  - Includes Federation reputation requirements and warnings about device instability.
  - Indicates next inventory refresh date at the Research Station.
  - Features animated visual effects when a Genesis Device is purchased.
- **Genesis Sequence Interface:**
  - Interactive control panel for initiating the Genesis Sequence.
  - Two distinct modes:
    - **Standard Genesis**: 48-hour terraforming process with real-time countdown
    - **Colony Ship Sacrifice**: Immediate planet creation with dramatic visual effect
  - Option to select Basic (1), Enhanced (3), or Colony Ship Sacrifice (5) Genesis procedures.
  - Visual representation of the forming planet with progressive stages in Standard mode.
  - Emergency abort option with clear warnings for Standard mode.
  - Very clear warnings about permanent ship loss for Colony Ship Sacrifice mode.
- **Team Coordination Interface:**
  - Team formation option for multi-player Genesis operations.
  - Contribution tracking showing which player provided which devices.
  - Ownership agreement system for the resulting planet.
  - Communication panel for coordinating the 48-hour process.
  - Ship positioning display showing the vessel carrying the Genesis Devices.
- **Mobile Optimization:**
  - Large, touch-friendly controls.
  - Push notifications for Genesis Sequence milestones and completion.
  - Visual and audio feedback for critical Genesis events.

## Business Logic & Rules

- **Purchase:**
  - Verify player Federation reputation level (minimum Level 8).
  - Confirm Research Station has inventory available.
  - Verify ship is a compatible type (Colony Ship, Carrier, Defender, Cargo Hauler, or Warp Jumper).
  - Deduct 25,000 credits per device, add devices to ship, enforce capacity limits.
  - Set next inventory refresh date (7 real-time days).
- **Usage:**
  - **Standard Genesis (1 or 3 devices):**
    - Verify sufficient devices for selected Genesis type.
    - Confirm ship is one of the compatible types.
    - Confirm sector eligibility (empty, not protected, beyond 5 jumps from Federation Space).
    - Lock player to sector during the 48-hour Genesis Sequence.
    - Display progressive visual changes to the sector during formation.
    - Apply turn penalties during Genesis Sequence (limited to 50 turns per day).
    - Generate planet type based on corresponding probability table.
    - Colony Ships reduce sequence time by 30% due to their Terraforming Modules special ability.
  - **Colony Ship Sacrifice (5 devices):**
    - Verify ship is specifically a Colony Ship with exactly 5 Genesis Devices.
    - Confirm sector eligibility (empty, not protected, beyond 5 jumps from Federation Space).
    - Process transaction atomically: consume ship and all devices, create planet.
    - Generate planet type with improved probabilities.
    - Create Settlement-level colony (Phase 2) with 5,000 population.
    - Construct Level 2 Citadel automatically.
    - Set ownership to the player who sacrificed the Colony Ship.
- **Team Operations:**
  - **Standard Genesis Teams:**
    - Verify all team members are present in the sector.
    - Verify at least one ship is a compatible type.
    - Collect required Genesis Devices from multiple ships.
    - Create shared ownership record with contribution percentages.
    - Apply economic benefits proportionally to contribution levels.
    - Colony Ship bonuses apply to the entire team operation if at least one team member uses one.
  - **Colony Ship Sacrifice Team Mode:**
    - Requires one player to sacrifice their Colony Ship with 5 Genesis Devices.
    - Other team members must be present in the sector during sacrifice.
    - The sacrificing player receives 50% ownership, remaining 50% distributed based on team agreement.
    - Team members can contribute resources to compensate the player who lost their ship.
    - A special shared ownership deed is created, recorded in all players' inventories.
- **Edge Cases:**
  - Cannot create a planet if another player attempts creation in the same sector (transaction locked).
  - Genesis Sequence fails if any team member leaves the sector, resulting in loss of all devices.
  - Sequence canceled if the sector comes under attack, with 50% chance of device recovery.
  - Anti-monopoly rule: Players cannot own more than 25% of planets in any region.

## Security & Anti-Cheat

- **Transactional Safety:** 
  - All Genesis operations use atomic database transactions with rollback capability.
  - Multi-phase commit process for team-based Genesis operations.
  - Transaction isolation level set to SERIALIZABLE for Genesis Sequences.
- **Server Validation:** 
  - Continuous server verification during the 48-hour Genesis Sequence.
  - Heartbeat system ensures players remain in the sector.
  - Server-side randomization for planet type generation using cryptographically secure RNG.
- **Comprehensive Logging:**
  - Detailed audit trail for all Genesis Device transactions.
  - Time-stamped sequence of events during planet creation.
  - Ownership validation for shared planets.
  - Block-chain style verification for Genesis Device origin and authenticity.
- **Rate Limiting:**
  - Maximum of 3 Genesis Device purchases per real-time week per account.
  - Players can participate in a maximum of 1 Genesis Sequence every 14 days.
  - Guild-level caps on planet creation to prevent domination.
- **Anti-Duplication & Exploitation:**
  - Genesis Device serial number tracking and validation.
  - Advanced detection for client manipulation attempts.
  - Quantum entanglement signatures verify device authenticity.
  - Server-side verification of all Genesis parameters.
  - Challenge-response protocol for client-server Genesis communications.

## See Also

- [Planetary Colonization](./PLANETARY_COLONIZATION.md)
- [Planetary Production](./PLANETARY_PRODUCTION.md)
- [Planetary Defense](./PLANETARY_DEFENSE.md)
- [Galaxy Generation](./GALAXY_GENERATION.md)
- [Resource Types](./RESOURCE_TYPES.md)

## Game Impact

Genesis Devices represent one of the most significant investments in Sector Wars 2102, creating dynamic gameplay through:

- **Strategic Expansion:** Players can establish presence in previously uninhabitable sectors
- **Economic Commitment:** The significant cost (minimum 25,000 credits for Basic Genesis plus ship investment) is achievable for most active players
- **Team Cooperation:** Encourages multi-player collaboration for shared planet creation
- **High-Risk Gameplay:** The random nature of planet types creates tension and excitement
- **Long-Term Planning:** The 48-hour creation process and substantial investment promote strategic thinking
- **Territorial Control:** Created planets become focal points for regional control and development
- **Strategic Decisions:** Players must choose between:
  - Standard Genesis: Lower cost, longer process, basic colony
  - Colony Ship Sacrifice: Higher upfront investment, immediate colony, advanced starting position

### Colony Ship Sacrifice Strategy

The Colony Ship sacrifice mechanic represents a major strategic decision point:

- **Pros:**
  - Instant planet creation (no 48-hour waiting period)
  - Begins with a Settlement-level colony instead of Outpost
  - 5,000 starting population (50x more than standard colonization)
  - Level 2 Citadel already built (saving resources and time)
  - Better weighted chances for desirable planet types

- **Cons:**
  - Permanent loss of a Colony Ship (significant investment)
  - Requires all 5 Genesis Devices on a single ship
  - Higher upfront cost (ship + 5 devices)
  - More difficult to organize as a team operation

This mechanic creates meaningful strategic decisions for players between patience and immediate results, differentiating the gameplay styles of different player types and teams. It's particularly valuable for aggressive expansion strategies or establishing a foothold in contested regions quickly.

Genesis Devices transform the gameplay from simple trading and combat into a complex, long-term strategic experience where players can literally reshape the galaxy to their advantage—if they're willing to accept the substantial costs and risks involved.