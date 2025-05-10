# AI Spec: Sector Wars 2102 - Database Schema v1 (Iteration 1 Conceptual)

**Source Document:** `docs/developer_requirements/database_schema_v1.md`
**Date:** May 10, 2025

## Core Tables (Primary Key, Key Fields):
1.  **`users`**: `user_id`, `username`, `password_hash`, `email`.
2.  **`players`**: `player_id`, `user_id` (FK), `captain_name`, `credits`, `current_ship_id` (FK), `current_sector_id` (FK).
3.  **`ship_types`** (Static): `ship_type_id`, `name`, `class_name`, `base_stats` (cargo, fuel, hull, etc.), `cost`.
4.  **`player_ships`**: `player_ship_id`, `player_id` (FK), `ship_type_id` (FK), `custom_name`, `current_stats` (hull, shield, fuel), `current_cargo_json`.
5.  **`sectors`**: `sector_id`, `name`, `coordinates_x`, `coordinates_y`, `security_level`, `services_json`.
6.  **`sector_connections`**: `connection_id`, `sector_a_id` (FK), `sector_b_id` (FK).
7.  **`resource_types`** (Static): `resource_type_id`, `name`, `base_value`.
8.  **`stations`**: `station_id`, `sector_id` (FK), `name`, `type`, `services_offered_json`, `faction_id` (FK).
9.  **`station_market`**: `station_market_id`, `station_id` (FK), `resource_type_id` (FK), `quantity_available`, `buy_price`, `sell_price`.
10. **`factions`**: `faction_id`, `name`, `default_disposition_to_player`.

## Key Relationships:
- User -> Player
- Player -> PlayerShip (current)
- PlayerShip -> ShipType
- Player located in Sector
- Sector contains Stations
- Station has Market for Resources
- Station can be controlled by Faction
- Sectors linked by SectorConnections
