# Sector Wars 2102 - Database Schema v1 (Iteration 1 Conceptual)

**Document Owner:** Developer (Simulated)
**Date:** May 10, 2025

This document outlines the conceptual first version of the database schema for Sector Wars 2102. This is intended as a starting point and will be significantly expanded and refined. Specific data types and constraints will be detailed in future iterations as features are fleshed out.

## Core Tables:

**1. `users`**
    *   `user_id` (Primary Key, e.g., UUID or SERIAL)
    *   `username` (Unique, Indexed)
    *   `password_hash`
    *   `email` (Unique, Indexed)
    *   `created_at`
    *   `last_login_at`

**2. `players` (Represents a player's in-game persona/captain)**
    *   `player_id` (Primary Key, e.g., UUID or SERIAL)
    *   `user_id` (Foreign Key to `users.user_id`)
    *   `captain_name` (Unique, Indexed)
    *   `credits` (e.g., BIGINT, default 0)
    *   `current_ship_id` (Foreign Key to `player_ships.player_ship_id`, nullable if player has no active ship initially)
    *   `current_sector_id` (Foreign Key to `sectors.sector_id`)
    *   `created_at`

**3. `ship_types` (Static data defining available ship classes/models)**
    *   `ship_type_id` (Primary Key, e.g., SERIAL or predefined ID)
    *   `name` (e.g., "Pathfinder Mk I", "Bulkhead Hauler")
    *   `class_name` (e.g., "Scout", "Freighter")
    *   `base_cargo_capacity`
    *   `base_fuel_capacity`
    *   `base_hull_strength`
    *   `base_shield_strength`
    *   `base_weapon_slots`
    *   `base_module_slots`
    *   `description`
    *   `cost`

**4. `player_ships` (Instances of ships owned by players)**
    *   `player_ship_id` (Primary Key, e.g., UUID or SERIAL)
    *   `player_id` (Foreign Key to `players.player_id`)
    *   `ship_type_id` (Foreign Key to `ship_types.ship_type_id`)
    *   `custom_name` (Nullable, player-given name for the ship)
    *   `current_hull`
    *   `current_shield`
    *   `current_fuel`
    *   `current_cargo_json` (e.g., JSONB to store item_id: quantity pairs)
    *   `location_sector_id` (Foreign Key to `sectors.sector_id` - if ship is not the player's current ship and is parked)
    *   `acquired_at`

**5. `sectors` (Represents star systems or regions in space)**
    *   `sector_id` (Primary Key, e.g., SERIAL or predefined ID)
    *   `name` (e.g., "Sol Core", "Alpha Centauri Fringe")
    *   `coordinates_x` (Integer)
    *   `coordinates_y` (Integer)
    *   `description`
    *   `security_level` (e.g., enum: high, medium, low, lawless)
    *   `services_json` (e.g., JSONB, flags for station, trade post, shipyard)

**6. `sector_connections` (Defines jump gates or connections between sectors)**
    *   `connection_id` (Primary Key)
    *   `sector_a_id` (Foreign Key to `sectors.sector_id`)
    *   `sector_b_id` (Foreign Key to `sectors.sector_id`)
    *   `is_two_way` (Boolean, default true)

**7. `resource_types` (Static data for tradable/minable resources)**
    *   `resource_type_id` (Primary Key)
    *   `name` (e.g., "Iron Ore", "Helium-3", "Ancient Artifacts")
    *   `base_value`
    *   `description`

**8. `stations` (Planets, space stations, trade posts within sectors)**
    *   `station_id` (Primary Key)
    *   `sector_id` (Foreign Key to `sectors.sector_id`)
    *   `name`
    *   `type` (e.g., enum: planet, trading_outpost, mining_station, shipyard)
    *   `services_offered_json` (e.g., trade, repair, missions, ship market)
    *   `faction_id` (Foreign Key to `factions.faction_id`, nullable)

**9. `station_market` (Dynamic prices and availability of goods at stations)**
    *   `station_market_id` (Primary Key)
    *   `station_id` (Foreign Key to `stations.station_id`)
    *   `resource_type_id` (Foreign Key to `resource_types.resource_type_id`)
    *   `quantity_available`
    *   `buy_price`
    *   `sell_price`
    *   `last_updated_at`

**10. `factions` (As per game design doc)**
    *   `faction_id` (Primary Key)
    *   `name` (e.g., "Terran Remnant Compact")
    *   `description`
    *   `default_disposition_to_player` (e.g., enum: friendly, neutral, hostile)

## Relationships (Summary):

*   A `user` can have one `player` profile.
*   A `player` has a `current_ship` (which is a `player_ship`) and is in a `current_sector`.
*   A `player_ship` is of a specific `ship_type` and belongs to a `player`.
*   `sectors` can contain multiple `stations`.
*   `stations` can have `station_market` entries for various `resource_types`.
*   `stations` can be controlled by a `faction`.
*   `sector_connections` link two `sectors`.

## Next Steps (for Developer in Iteration 2):

*   Refine data types (e.g., VARCHAR(255), INT, BOOLEAN, TIMESTAMP, JSONB).
*   Add appropriate constraints (NOT NULL, UNIQUE, CHECK).
*   Define indexes for performance.
*   Create SQL DDL scripts to generate this schema.
*   Consider tables for ship modules/equipment, missions, player reputation with factions.
