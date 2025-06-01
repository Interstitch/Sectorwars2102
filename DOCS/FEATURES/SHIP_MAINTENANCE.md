# Ship Maintenance System

## Overview

The Ship Maintenance System adds strategic depth to ship ownership in Sector Wars 2102. Ships require regular maintenance to remain in optimal condition. Neglected ships suffer performance penalties, while well-maintained vessels gain bonuses and longevity.

## Core Mechanics

### Maintenance Rating

- Each ship has a Maintenance Rating from 0-100%
- New ships start at 100% Maintenance Rating
- Rating decreases by 1-3% per day depending on ship class:
  - Light Freighter: -1% per day
  - Cargo Hauler: -2% per day
  - Fast Courier: -1% per day
  - Colony Ship: -2% per day
  - Defender: -2% per day
  - Carrier: -3% per day
  - Scout Ship: -1% per day
  - Warp Jumper: -3% per day

### Performance Impacts

Maintenance Rating directly affects ship performance:

| Rating Range | Effects |
|--------------|---------|
| 90-100% | +5% to speed, +5% to combat effectiveness, -5% to fuel consumption |
| 75-89% | No bonuses or penalties (standard performance) |
| 50-74% | -5% to speed, -5% to combat effectiveness, +5% to fuel consumption |
| 25-49% | -15% to speed, -20% to combat effectiveness, +20% to fuel consumption, 5% chance of minor system failure per jump |
| 10-24% | -30% to speed, -40% to combat effectiveness, +50% to fuel consumption, 15% chance of major system failure per jump |
| 0-9% | -50% to speed, -75% to combat effectiveness, +100% to fuel consumption, 30% chance of catastrophic failure per jump |

### System Failures

System failures become possible when Maintenance Rating drops below 50%:

- **Minor System Failure**: Temporary loss of a non-critical system (sensors, shields, etc.)
- **Major System Failure**: Ship becomes immobilized in current sector, requiring repair before movement
- **Catastrophic Failure**: Ship structure is compromised, resulting in a 20% chance of complete destruction, otherwise reducing to 1% hull integrity

## Maintenance Services

### Port Maintenance

Players can maintain ships at any port with shipyard facilities:

- **Basic Maintenance**: Available at all ports with shipyards
  - Cost: 5% of ship value per 10% Maintenance Rating increase
  - Duration: 6 hours per 10% increase

- **Emergency Repairs**: Available at all ports with shipyards
  - Cost: 10% of ship value per 10% Maintenance Rating increase
  - Duration: 2 hours per 10% increase
  - Availability: Usable even during system failures

- **Premium Service**: Available at Class I and Military ports only
  - Cost: 15% of ship value per 10% Maintenance Rating increase
  - Duration: 1 hour per 10% increase
  - Bonus: Ship receives +2% temporary boost to speed and combat effectiveness for 48 hours

### Self-Maintenance

Players can perform maintenance themselves:

- Requires a Maintenance Kit (5,000 credits, takes up 1 cargo space)
- Each kit can restore up to 25% Maintenance Rating
- Process takes 12 hours of game time
- Self-maintenance incurs a 15% chance of error, reducing effectiveness to 15% rather than 25%

## Strategic Considerations

### Long Expeditions

For players undertaking long journeys away from ports:

- Pack maintenance kits based on expected trip duration
- Consider ship maintenance rating when planning routes
- Factor in higher fuel consumption of poorly maintained ships

### Maintenance-Focused Builds

Players can specialize in low-maintenance ship configurations:

- **Ship Modifications**: Special upgrades that reduce maintenance decay rate by 25-50%
- **Automated Maintenance Systems**: Module that automatically uses maintenance kits when rating drops below 65%

### Fleet Management

Managing the maintenance of multiple ships requires strategic planning:

- Stagger maintenance schedules to avoid simultaneous downtime
- Consider scrapping ships with excessive maintenance costs
- Prioritize critical vessels during resource constraints

## Economic Impact

The maintenance system creates several economic considerations:

- Regular maintenance creates a credit sink in the game economy
- Creates market demand for maintenance kits
- Introduces trade-offs between maintenance costs and ship performance
- Encourages port visits, stimulating local economies

## Player Notifications

Players receive notifications about ship maintenance:

- Warning at 75% Maintenance Rating
- Urgent warning at 50% Maintenance Rating
- Critical warning at 25% Maintenance Rating
- Emergency alert at 10% Maintenance Rating
- Failure notifications when systems malfunction

## Ship Insurance

Players can purchase insurance policies for their ships at friendly ports:

- **Basic Insurance**: Covers 50% of ship value, 5% deductible
- **Standard Insurance**: Covers 75% of ship value, 10% deductible
- **Premium Insurance**: Covers 90% of ship value, 15% deductible

Insurance payouts are made immediately when a ship is destroyed, allowing for rapid acquisition of a replacement vessel. The insurance cost scales with ship value, with more expensive ships requiring higher premiums.