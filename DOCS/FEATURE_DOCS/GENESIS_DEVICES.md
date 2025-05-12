# Genesis Devices — Sector Wars 2102

This document describes the Genesis Device system for Sector Wars 2102, including acquisition, usage, ship integration, UI/UX, and security. Genesis Devices are the only way to create new planets.

## Overview

Genesis Devices are special consumable items that allow players to create new planets in empty sectors. They are purchased at starbases, stored on ships, and consumed during the planet creation process.

## Acquisition & Storage

- **Purchase Location:** Genesis Devices can be purchased at equipped starbases (not all ports).
- **Cost:** 5,000 credits per device.
- **Unlimited Stock:** Always available at eligible starbases.
- **Ship Capacity:**
  - Each ship type has a maximum Genesis Device capacity (`maxGenesis`).
  - Some ships cannot carry Genesis Devices (e.g., basic combat ships).
  - See ship data model for details.
- **Purchase Rules:**
  - Cannot exceed ship's `maxGenesis`.
  - Attempting to purchase more than available space results in an error.

## Usage — Planet Creation

- **Requirement:** One Genesis Device is consumed for each new planet created.
- **Process:**
  1. Player must be in an empty, non-protected sector.
  2. Player must have at least one Genesis Device on their ship.
  3. Player initiates planet creation (UI or API).
  4. Genesis Device is consumed, and a new planet is generated.
- **Protected Sectors:** Planets cannot be created in protected sectors (e.g., sectors 1–7).
- **Randomization:** The resulting planet type is determined randomly, with weighted probabilities (see below).

## Ship Integration

- **Ship Model Fields:**
  - `genesis`: Current Genesis Device count.
  - `maxGenesis`: Maximum Genesis Devices the ship can carry.
- **Strategic Choice:** Players may upgrade to ships with higher Genesis capacity for large-scale colonization.
- **Equipment Competition:** Genesis Devices share space with other equipment (fighters, mines, etc.), requiring resource planning.

## Planet Type Probabilities

| Planet Type | Probability |
|-------------|-------------|
| M_CLASS     | 30%         |
| L_CLASS     | 20%         |
| O_CLASS     | 20%         |
| K_CLASS     | 15%         |
| H_CLASS     | 7%          |
| C_CLASS     | 5%          |
| U_CLASS     | 3%          |

- More desirable planet types (M_CLASS) are more common; rare types (U_CLASS) are less likely.

## UI/UX

- **Purchase Interface:**
  - Shows ship's Genesis capacity, current count, and available space.
  - Quantity selector is limited to available space.
  - Clear error messages for over-capacity or incompatible ships.
- **Planet Creation Interface:**
  - Disabled if no Genesis Devices are available.
  - Shows number of Genesis Devices remaining.
  - Success/failure feedback after creation attempt.
- **Mobile Optimization:**
  - Large, touch-friendly controls.
  - Visual feedback for device consumption and planet creation.

## Business Logic & Rules

- **Purchase:**
  - Deduct credits, add devices to ship, enforce capacity.
- **Usage:**
  - Device is consumed only if planet creation succeeds.
  - All checks (sector emptiness, protected status, device count) are server-side.
- **Edge Cases:**
  - Cannot create a planet if another player creates one in the same sector first (race condition safe).
  - Genesis Devices are not refunded if creation fails due to player error (e.g., leaving sector mid-process).

## Security & Anti-Cheat

- **Transactional Safety:** All purchases and usage are wrapped in database transactions.
- **Server Validation:** Server checks all requirements before consuming a device or creating a planet.
- **Logging:** All Genesis Device purchases and usages are logged for audit.
- **Rate Limiting:**
  - Limits on purchase frequency and usage to prevent abuse.
  - Cooldown period between planet creations.
- **Anti-Duplication:**
  - Prevents device count exploits via transaction integrity.

## Testing & QA

- **Test Cases:**
  - Purchase for compatible/incompatible ships.
  - Capacity enforcement.
  - Device consumption on planet creation.
  - UI feedback for all error/success states.
  - Random planet type distribution.
- **Automated Tests:** See test suite for Genesis Device purchase and usage scenarios.

## See Also

- [Planetary Colonization](./PLANETARY_COLONIZATION.md)
- [Planetary Production](./PLANETARY_PRODUCTION.md)
- [Planetary Defense](./PLANETARY_DEFENSE.md)
