# 🚀 SectorWars 2102 - Complete API Endpoint Inventory

**Generated**: 2025-11-16
**Total Endpoints**: 358
**Route Modules**: 40

## 📊 Summary by Category

| Category | Endpoints | Files |
|----------|-----------|-------|
| AI Systems | 9 | 1 |
| Admin Colonization | 3 | 1 |
| Admin Combat | 5 | 1 |
| Admin Comprehensive | 49 | 1 |
| Admin Core | 22 | 1 |
| Admin Drones | 8 | 1 |
| Admin Economy | 5 | 1 |
| Admin Enhanced | 6 | 1 |
| Admin Factions | 8 | 1 |
| Admin Fleets | 9 | 1 |
| Admin Messages | 4 | 1 |
| Admin Ships | 4 | 1 |
| Audit | 4 | 1 |
| Authentication | 16 | 1 |
| Combat | 4 | 1 |
| Debug (Dev Only) | 2 | 1 |
| Drones | 16 | 1 |
| Economy & Trading | 23 | 3 |
| Events | 8 | 1 |
| Factions | 8 | 1 |
| First Login | 7 | 1 |
| Fleets | 13 | 1 |
| Internationalization | 13 | 1 |
| Messages | 7 | 1 |
| Multi-Regional | 17 | 2 |
| Payment | 8 | 1 |
| Planets | 8 | 1 |
| Player | 8 | 2 |
| Sectors | 2 | 1 |
| Security (MFA) | 8 | 1 |
| System Status | 18 | 1 |
| Teams | 18 | 1 |
| Test (Dev Only) | 2 | 1 |
| User Management | 7 | 1 |
| WebSocket | 9 | 2 |

---

## AI Systems

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/market-analysis/{commodity_id}` | `get_market_analysis` | `ai.py` |
| GET | `/performance` | `get_ai_performance_stats` | `ai.py` |
| GET | `/profile` | `get_player_trading_profile` | `ai.py` |
| GET | `/recommendations` | `get_trading_recommendations` | `ai.py` |
| GET | `/recommendations/history` | `get_recommendation_history` | `ai.py` |
| POST | `/optimize-route` | `optimize_trading_route` | `ai.py` |
| POST | `/profile/trade-update` | `update_trading_data` | `ai.py` |
| POST | `/recommendations/{recommendation_id}/feedback` | `submit_recommendation_feedback` | `ai.py` |
| PUT | `/profile` | `update_ai_preferences` | `ai.py` |

## Admin Colonization

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/colonization/genesis-devices` | `get_genesis_devices` | `admin_colonization.py` |
| GET | `/colonization/planets` | `get_admin_colonization_planets` | `admin_colonization.py` |
| GET | `/colonization/production` | `get_colony_production` | `admin_colonization.py` |

## Admin Combat

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/balance` | `get_combat_balance_analytics` | `admin_combat.py` |
| GET | `/dashboard-summary` | `get_combat_dashboard_summary` | `admin_combat.py` |
| GET | `/disputes` | `get_combat_disputes` | `admin_combat.py` |
| GET | `/live` | `get_live_combat_feed` | `admin_combat.py` |
| POST | `/{combat_id}/intervene` | `intervene_in_combat` | `admin_combat.py` |

## Admin Comprehensive

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/ports/{port_id}` | `delete_port` | `admin_comprehensive.py` |
| DELETE | `/ships/{ship_id}` | `delete_ship` | `admin_comprehensive.py` |
| DELETE | `/warp-tunnels/{tunnel_id}` | `delete_warp_tunnel` | `admin_comprehensive.py` |
| GET | `/ai/behavior-analytics` | `get_ai_behavior_analytics` | `admin_comprehensive.py` |
| GET | `/ai/metrics` | `get_ai_system_metrics` | `admin_comprehensive.py` |
| GET | `/ai/models` | `get_ai_models` | `admin_comprehensive.py` |
| GET | `/ai/predictions` | `get_ai_predictions` | `admin_comprehensive.py` |
| GET | `/ai/predictions/accuracy` | `get_ai_prediction_accuracy` | `admin_comprehensive.py` |
| GET | `/ai/profiles` | `get_ai_player_profiles` | `admin_comprehensive.py` |
| GET | `/ai/route-optimization` | `get_ai_route_optimization_data` | `admin_comprehensive.py` |
| GET | `/analytics/dashboard` | `get_analytics_dashboard` | `admin_comprehensive.py` |
| GET | `/analytics/real-time` | `get_real_time_analytics` | `admin_comprehensive.py` |
| GET | `/planets` | `get_planets` | `admin_comprehensive.py` |
| GET | `/planets/comprehensive` | `get_planets_comprehensive` | `admin_comprehensive.py` |
| GET | `/players/comprehensive` | `get_players_comprehensive` | `admin_comprehensive.py` |
| GET | `/ports` | `get_ports` | `admin_comprehensive.py` |
| GET | `/ports/comprehensive` | `get_ports_comprehensive` | `admin_comprehensive.py` |
| GET | `/sectors` | `get_sectors` | `admin_comprehensive.py` |
| GET | `/sectors/{sector_id}/planet` | `get_sector_planet` | `admin_comprehensive.py` |
| GET | `/sectors/{sector_id}/port` | `get_sector_port` | `admin_comprehensive.py` |
| GET | `/sectors/{sector_id}/warp-tunnels` | `get_sector_warp_tunnels` | `admin_comprehensive.py` |
| GET | `/security/alerts` | `get_security_alerts` | `admin_comprehensive.py` |
| GET | `/security/player/{player_id}/risk` | `get_player_risk_assessment` | `admin_comprehensive.py` |
| GET | `/security/player/{player_id}/status` | `get_player_security_status` | `admin_comprehensive.py` |
| GET | `/security/report` | `get_security_report` | `admin_comprehensive.py` |
| GET | `/ships/comprehensive` | `get_ships_comprehensive` | `admin_comprehensive.py` |
| GET | `/system/health` | `get_system_health` | `admin_comprehensive.py` |
| GET | `/teams/comprehensive` | `get_teams_comprehensive` | `admin_comprehensive.py` |
| GET | `/universe/sectors/comprehensive` | `get_sectors_comprehensive` | `admin_comprehensive.py` |
| GET | `/warp-tunnels` | `get_warp_tunnels` | `admin_comprehensive.py` |
| GET | `/warp-tunnels/comprehensive` | `get_warp_tunnels_comprehensive` | `admin_comprehensive.py` |
| PATCH | `/ports/{port_id}` | `update_port` | `admin_comprehensive.py` |
| POST | `/ai/models/{model_id}/{action}` | `ai_model_action` | `admin_comprehensive.py` |
| POST | `/analytics/snapshot` | `create_analytics_snapshot` | `admin_comprehensive.py` |
| POST | `/players/create-bulk` | `create_players_from_all_users` | `admin_comprehensive.py` |
| POST | `/players/create-from-user` | `create_player_from_user` | `admin_comprehensive.py` |
| POST | `/ports` | `create_port` | `admin_comprehensive.py` |
| POST | `/ports/update-stock-levels` | `update_all_port_stock_levels` | `admin_comprehensive.py` |
| POST | `/sectors/{sector_id}/planet` | `create_planet_in_sector` | `admin_comprehensive.py` |
| POST | `/sectors/{sector_id}/port` | `create_port_in_sector` | `admin_comprehensive.py` |
| POST | `/sectors/{sector_id}/warp-tunnels` | `create_warp_tunnel` | `admin_comprehensive.py` |
| POST | `/security/cleanup` | `cleanup_security_data` | `admin_comprehensive.py` |
| POST | `/security/player/{player_id}/action` | `take_security_action` | `admin_comprehensive.py` |
| POST | `/ships` | `create_ship` | `admin_comprehensive.py` |
| POST | `/ships/{ship_id}/teleport` | `teleport_ship` | `admin_comprehensive.py` |
| PUT | `/players/{player_id}` | `update_player` | `admin_comprehensive.py` |
| PUT | `/sectors/{sector_id}` | `update_sector` | `admin_comprehensive.py` |
| PUT | `/ships/{ship_id}` | `update_ship` | `admin_comprehensive.py` |
| PUT | `/warp-tunnels/{tunnel_id}` | `update_warp_tunnel` | `admin_comprehensive.py` |

## Admin Core

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/galaxy/clear` | `clear_all_galaxy_data` | `admin.py` |
| DELETE | `/galaxy/{galaxy_id}` | `delete_galaxy` | `admin.py` |
| GET | `/alliances` | `get_all_alliances` | `admin.py` |
| GET | `/clusters` | `get_all_clusters` | `admin.py` |
| GET | `/colonies` | `get_all_colonies` | `admin.py` |
| GET | `/galaxy` | `get_galaxy_info` | `admin.py` |
| GET | `/galaxy/{galaxy_id}/zones` | `get_galaxy_zones` | `admin.py` |
| GET | `/players` | `get_all_players` | `admin.py` |
| GET | `/regions` | `get_all_regions` | `admin.py` |
| GET | `/sectors` | `get_all_sectors` | `admin.py` |
| GET | `/sectors/{sector_id}/planet` | `get_sector_planet` | `admin.py` |
| GET | `/sectors/{sector_id}/port` | `get_sector_port` | `admin.py` |
| GET | `/sectors/{sector_id}/ships` | `get_sector_ships` | `admin.py` |
| GET | `/stats` | `get_admin_stats` | `admin.py` |
| GET | `/teams` | `get_all_teams` | `admin.py` |
| GET | `/teams/analytics` | `get_teams_analytics` | `admin.py` |
| GET | `/users` | `get_all_users` | `admin.py` |
| GET | `/zones/{zone_id}/clusters` | `get_zone_clusters` | `admin.py` |
| PATCH | `/players/{player_id}` | `update_player` | `admin.py` |
| PATCH | `/ports/{port_id}` | `update_port` | `admin.py` |
| POST | `/galaxy/generate` | `generate_galaxy` | `admin.py` |
| POST | `/warp-tunnels/create` | `create_warp_tunnel` | `admin.py` |

## Admin Drones

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{drone_id}` | `delete_drone` | `admin_drones.py` |
| GET | `/` | `get_all_drones` | `admin_drones.py` |
| GET | `/sector/{sector_id}/summary` | `get_sector_drone_summary` | `admin_drones.py` |
| GET | `/statistics` | `get_drone_statistics` | `admin_drones.py` |
| GET | `/{drone_id}` | `get_drone_details` | `admin_drones.py` |
| PATCH | `/{drone_id}` | `update_drone` | `admin_drones.py` |
| POST | `/{drone_id}/force-recall` | `force_recall_drone` | `admin_drones.py` |
| POST | `/{drone_id}/restore` | `restore_destroyed_drone` | `admin_drones.py` |

## Admin Economy

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/dashboard-summary` | `get_dashboard_summary` | `admin_economy.py` |
| GET | `/market-data` | `get_market_data` | `admin_economy.py` |
| GET | `/metrics` | `get_economic_metrics` | `admin_economy.py` |
| GET | `/price-alerts` | `get_price_alerts` | `admin_economy.py` |
| POST | `/intervention` | `perform_market_intervention` | `admin_economy.py` |

## Admin Enhanced

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/sectors/enhanced` | `get_enhanced_sectors` | `admin_enhanced.py` |
| POST | `/galaxy/generate-enhanced` | `generate_enhanced_galaxy` | `admin_enhanced.py` |
| POST | `/planet/create` | `create_planet` | `admin_enhanced.py` |
| POST | `/port/create` | `create_port` | `admin_enhanced.py` |
| POST | `/warp-tunnel/create-enhanced` | `create_enhanced_warp_tunnel` | `admin_enhanced.py` |
| PUT | `/sector/{sector_id}` | `update_sector` | `admin_enhanced.py` |

## Admin Factions

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{faction_id}` | `delete_faction` | `admin_factions.py` |
| GET | `/` | `list_all_factions` | `admin_factions.py` |
| GET | `/missions/all` | `list_all_missions` | `admin_factions.py` |
| POST | `/` | `create_faction` | `admin_factions.py` |
| POST | `/{faction_id}/missions` | `create_faction_mission` | `admin_factions.py` |
| PUT | `/{faction_id}` | `update_faction` | `admin_factions.py` |
| PUT | `/{faction_id}/reputation` | `update_player_reputation` | `admin_factions.py` |
| PUT | `/{faction_id}/territory` | `update_faction_territory` | `admin_factions.py` |

## Admin Fleets

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{fleet_id}/force-dissolve` | `force_dissolve_fleet` | `admin_fleets.py` |
| GET | `/` | `get_all_fleets` | `admin_fleets.py` |
| GET | `/battles` | `get_all_battles` | `admin_fleets.py` |
| GET | `/battles/{battle_id}` | `get_battle_details` | `admin_fleets.py` |
| GET | `/stats` | `get_fleet_statistics` | `admin_fleets.py` |
| GET | `/{fleet_id}` | `get_fleet_details` | `admin_fleets.py` |
| GET | `/{fleet_id}/members` | `get_fleet_members` | `admin_fleets.py` |
| PATCH | `/{fleet_id}/morale` | `adjust_fleet_morale` | `admin_fleets.py` |
| POST | `/battles/{battle_id}/intervene` | `intervene_in_battle` | `admin_fleets.py` |

## Admin Messages

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/all` | `get_all_messages` | `admin_messages.py` |
| GET | `/flagged` | `get_flagged_messages` | `admin_messages.py` |
| GET | `/stats` | `get_message_statistics` | `admin_messages.py` |
| POST | `/{message_id}/moderate` | `moderate_message` | `admin_messages.py` |

## Admin Ships

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{ship_id}` | `delete_ship` | `admin_ships.py` |
| GET | `/health-report` | `get_fleet_health_report` | `admin_ships.py` |
| POST | `/create` | `create_ship` | `admin_ships.py` |
| POST | `/{ship_id}/emergency` | `emergency_ship_action` | `admin_ships.py` |

## Audit

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/logs` | `get_audit_logs` | `audit.py` |
| GET | `/users/{user_id}/activity` | `get_user_activity_summary` | `audit.py` |
| GET | `/violations` | `get_security_violations` | `audit.py` |
| POST | `/log` | `create_audit_log` | `audit.py` |

## Authentication

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/github` | `login_github` | `auth.py` |
| GET | `/github/callback` | `github_callback` | `auth.py` |
| GET | `/google` | `login_google` | `auth.py` |
| GET | `/google/callback` | `google_callback` | `auth.py` |
| GET | `/me` | `get_current_user_info` | `auth.py` |
| GET | `/steam` | `login_steam` | `auth.py` |
| GET | `/steam/callback` | `steam_callback` | `auth.py` |
| POST | `/login` | `login` | `auth.py` |
| POST | `/login/direct` | `login_direct` | `auth.py` |
| POST | `/login/json` | `login_json` | `auth.py` |
| POST | `/logout` | `logout` | `auth.py` |
| POST | `/me/token` | `get_user_by_token` | `auth.py` |
| POST | `/player/login` | `player_login` | `auth.py` |
| POST | `/player/login/json` | `player_login_json` | `auth.py` |
| POST | `/refresh` | `refresh_token` | `auth.py` |
| POST | `/register` | `register_user` | `auth.py` |

## Combat

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/balance` | `get_balance_metrics` | `combat.py` |
| GET | `/logs` | `get_combat_logs` | `combat.py` |
| GET | `/stats` | `get_combat_stats` | `combat.py` |
| POST | `/{combat_id}/resolve` | `resolve_combat_dispute` | `combat.py` |

## Debug (Dev Only)

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/debug/sector-check` | `check_sectors` | `debug.py` |
| GET | `/debug/user-state` | `get_user_state` | `debug.py` |

## Drones

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{deploymentId}/recall` | `recall_drones_contract` | `drones.py` |
| GET | `/` | `get_my_drones` | `drones.py` |
| GET | `/combat/history` | `get_combat_history` | `drones.py` |
| GET | `/deployed` | `get_deployed_drones_contract` | `drones.py` |
| GET | `/deployments/` | `get_my_deployments` | `drones.py` |
| GET | `/sector/{sector_id}` | `get_sector_drones` | `drones.py` |
| GET | `/team/{team_id}` | `get_team_drones` | `drones.py` |
| GET | `/types` | `get_drone_types` | `drones.py` |
| GET | `/{drone_id}` | `get_drone` | `drones.py` |
| POST | `/` | `create_drone` | `drones.py` |
| POST | `/combat/initiate` | `initiate_combat` | `drones.py` |
| POST | `/deploy` | `deploy_drones_contract` | `drones.py` |
| POST | `/{drone_id}/deploy` | `deploy_drone` | `drones.py` |
| POST | `/{drone_id}/recall` | `recall_drone` | `drones.py` |
| POST | `/{drone_id}/repair` | `repair_drone` | `drones.py` |
| POST | `/{drone_id}/upgrade` | `upgrade_drone` | `drones.py` |

## Economy & Trading

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/alerts/{alert_id}` | `delete_price_alert` | `economy.py` |
| GET | `/history` | `get_trading_history` | `trading.py` |
| GET | `/market-data` | `get_market_data` | `economy.py` |
| GET | `/market/{port_id}` | `get_market_info` | `trading.py` |
| GET | `/metrics` | `get_economic_metrics` | `economy.py` |
| GET | `/my-patterns` | `get_my_trading_patterns` | `quantum_trading.py` |
| GET | `/price-alerts` | `get_price_alerts` | `economy.py` |
| GET | `/price-history/{commodity}` | `get_price_history` | `economy.py` |
| GET | `/quantum-state` | `get_quantum_engine_state` | `quantum_trading.py` |
| GET | `/recommendations` | `get_quantum_recommendations` | `quantum_trading.py` |
| GET | `/transactions` | `get_recent_transactions` | `economy.py` |
| POST | `/buy` | `buy_resource` | `trading.py` |
| POST | `/collapse-quantum-trade/{trade_id}` | `collapse_quantum_trade` | `quantum_trading.py` |
| POST | `/create-alert` | `create_price_alert` | `economy.py` |
| POST | `/create-cascade` | `create_trade_cascade` | `quantum_trading.py` |
| POST | `/create-quantum-trade` | `create_quantum_trade` | `quantum_trading.py` |
| POST | `/dock` | `dock_at_port` | `trading.py` |
| POST | `/execute-cascade-step/{cascade_id}` | `execute_cascade_step` | `quantum_trading.py` |
| POST | `/ghost-trade` | `execute_ghost_trade` | `quantum_trading.py` |
| POST | `/intervention` | `price_intervention` | `economy.py` |
| POST | `/record-observation` | `record_market_observation` | `quantum_trading.py` |
| POST | `/sell` | `sell_resource` | `trading.py` |
| POST | `/undock` | `undock_from_port` | `trading.py` |

## Events

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{event_id}` | `delete_event` | `events.py` |
| GET | `/` | `get_events` | `events.py` |
| GET | `/stats` | `get_event_stats` | `events.py` |
| GET | `/templates` | `get_event_templates` | `events.py` |
| POST | `/` | `create_event` | `events.py` |
| POST | `/{event_id}/activate` | `activate_event` | `events.py` |
| POST | `/{event_id}/deactivate` | `deactivate_event` | `events.py` |
| PUT | `/{event_id}` | `update_event` | `events.py` |

## Factions

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/` | `list_factions` | `factions.py` |
| GET | `/missions` | `get_available_missions` | `factions.py` |
| GET | `/reputation` | `get_player_reputations` | `factions.py` |
| GET | `/{faction_id}/missions` | `get_faction_missions` | `factions.py` |
| GET | `/{faction_id}/pricing-modifier` | `get_pricing_modifier` | `factions.py` |
| GET | `/{faction_id}/reputation` | `get_faction_reputation` | `factions.py` |
| GET | `/{faction_id}/territory` | `get_faction_territory` | `factions.py` |
| POST | `/{faction_id}/missions/accept` | `accept_mission` | `factions.py` |

## First Login

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/session` | `reset_first_login_session` | `first_login.py` |
| GET | `/debug` | `debug_first_login_state` | `first_login.py` |
| GET | `/status` | `get_first_login_status` | `first_login.py` |
| POST | `/claim-ship` | `claim_ship` | `first_login.py` |
| POST | `/complete` | `complete_first_login` | `first_login.py` |
| POST | `/dialogue/{exchange_id}` | `answer_dialogue` | `first_login.py` |
| POST | `/session` | `start_first_login_session` | `first_login.py` |

## Fleets

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{fleet_id}` | `disband_fleet` | `fleets.py` |
| DELETE | `/{fleet_id}/remove-ship/{ship_id}` | `remove_ship_from_fleet` | `fleets.py` |
| GET | `/` | `get_team_fleets` | `fleets.py` |
| GET | `/battles` | `get_team_battles` | `fleets.py` |
| GET | `/my-fleets` | `get_my_fleets` | `fleets.py` |
| GET | `/{fleet_id}` | `get_fleet` | `fleets.py` |
| GET | `/{fleet_id}/members` | `get_fleet_members` | `fleets.py` |
| PATCH | `/{fleet_id}/commander` | `update_fleet_commander` | `fleets.py` |
| PATCH | `/{fleet_id}/formation` | `update_fleet_formation` | `fleets.py` |
| POST | `/` | `create_fleet` | `fleets.py` |
| POST | `/battles/{battle_id}/simulate-round` | `simulate_battle_round` | `fleets.py` |
| POST | `/{fleet_id}/add-ship` | `add_ship_to_fleet` | `fleets.py` |
| POST | `/{fleet_id}/initiate-battle` | `initiate_battle` | `fleets.py` |

## Internationalization

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/admin/languages/all` | `get_all_languages` | `translation.py` |
| GET | `/admin/progress/{language_code}` | `get_translation_progress` | `translation.py` |
| GET | `/detect` | `detect_language` | `translation.py` |
| GET | `/health` | `translation_health_check` | `translation.py` |
| GET | `/languages` | `get_supported_languages` | `translation.py` |
| GET | `/user/ai-context` | `get_ai_language_context` | `translation.py` |
| GET | `/user/preference` | `get_user_language_preference` | `translation.py` |
| GET | `/{language_code}` | `get_translations` | `translation.py` |
| GET | `/{language_code}/{namespace}` | `get_namespace_translations` | `translation.py` |
| POST | `/admin/bulk/{language_code}/{namespace}` | `bulk_import_translations` | `translation.py` |
| POST | `/admin/initialize` | `initialize_translation_data` | `translation.py` |
| POST | `/admin/translation/{language_code}/{namespace}` | `set_translation` | `translation.py` |
| POST | `/user/preference` | `set_user_language_preference` | `translation.py` |

## Messages

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{message_id}` | `delete_message` | `messages.py` |
| GET | `/conversations` | `get_conversations` | `messages.py` |
| GET | `/inbox` | `get_inbox` | `messages.py` |
| GET | `/team/{team_id}` | `get_team_messages` | `messages.py` |
| POST | `/send` | `send_message` | `messages.py` |
| POST | `/{message_id}/flag` | `flag_message` | `messages.py` |
| PUT | `/{message_id}/read` | `mark_message_read` | `messages.py` |

## Multi-Regional

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/districts` | `get_districts_info` | `nexus.py` |
| GET | `/districts/{district_type}` | `get_district_details` | `nexus.py` |
| GET | `/my-region` | `get_my_region` | `regional_governance.py` |
| GET | `/my-region/elections` | `get_regional_elections` | `regional_governance.py` |
| GET | `/my-region/members` | `get_regional_members` | `regional_governance.py` |
| GET | `/my-region/policies` | `get_regional_policies` | `regional_governance.py` |
| GET | `/my-region/stats` | `get_regional_stats` | `regional_governance.py` |
| GET | `/my-region/treaties` | `get_regional_treaties` | `regional_governance.py` |
| GET | `/stats` | `get_nexus_statistics` | `nexus.py` |
| GET | `/status` | `get_nexus_status` | `nexus.py` |
| POST | `/districts/{district_type}/regenerate` | `regenerate_district` | `nexus.py` |
| POST | `/generate` | `generate_central_nexus` | `nexus.py` |
| POST | `/my-region/elections` | `start_election` | `regional_governance.py` |
| POST | `/my-region/policies` | `create_policy` | `regional_governance.py` |
| PUT | `/my-region/culture` | `update_cultural_identity` | `regional_governance.py` |
| PUT | `/my-region/economy` | `update_economic_config` | `regional_governance.py` |
| PUT | `/my-region/governance` | `update_governance_config` | `regional_governance.py` |

## Payment

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/admin/subscriptions` | `admin_get_all_subscriptions` | `paypal.py` |
| GET | `/plans` | `get_subscription_plans` | `paypal.py` |
| GET | `/regions/available-names` | `check_region_name_availability` | `paypal.py` |
| GET | `/subscriptions` | `get_user_subscriptions` | `paypal.py` |
| GET | `/subscriptions/{subscription_id}` | `get_subscription_details` | `paypal.py` |
| POST | `/subscriptions/create` | `create_subscription` | `paypal.py` |
| POST | `/subscriptions/{subscription_id}/cancel` | `cancel_subscription` | `paypal.py` |
| POST | `/webhooks/paypal` | `handle_paypal_webhook` | `paypal.py` |

## Planets

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/owned` | `get_owned_planets` | `planets.py` |
| GET | `/{planetId}` | `get_planet_details` | `planets.py` |
| GET | `/{planetId}/siege-status` | `get_siege_status` | `planets.py` |
| POST | `/genesis/deploy` | `deploy_genesis_device` | `planets.py` |
| POST | `/{planetId}/buildings/upgrade` | `upgrade_building` | `planets.py` |
| PUT | `/{planetId}/allocate` | `allocate_colonists` | `planets.py` |
| PUT | `/{planetId}/defenses` | `update_defenses` | `planets.py` |
| PUT | `/{planetId}/specialize` | `set_specialization` | `planets.py` |

## Player

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/available-moves` | `get_available_moves` | `player.py` |
| GET | `/current-sector` | `get_current_sector` | `player.py` |
| GET | `/current-ship` | `get_current_ship` | `player.py` |
| GET | `/ships` | `get_player_ships` | `player.py` |
| GET | `/state` | `get_player_state` | `player.py` |
| GET | `/{combatId}/status` | `get_combat_status` | `player_combat.py` |
| POST | `/engage` | `engage_combat` | `player_combat.py` |
| POST | `/move/{sector_id}` | `move_to_sector` | `player.py` |

## Sectors

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/{sector_id}/planets` | `get_sector_planets` | `sectors.py` |
| GET | `/{sector_id}/ports` | `get_sector_ports` | `sectors.py` |

## Security (MFA)

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/attempts` | `get_mfa_attempts` | `mfa.py` |
| GET | `/backup-codes` | `get_backup_codes` | `mfa.py` |
| GET | `/status` | `get_mfa_status` | `mfa.py` |
| POST | `/check` | `check_mfa_code` | `mfa.py` |
| POST | `/disable` | `disable_mfa` | `mfa.py` |
| POST | `/generate` | `generate_mfa_secret` | `mfa.py` |
| POST | `/regenerate-backup-codes` | `regenerate_backup_codes` | `mfa.py` |
| POST | `/verify` | `verify_mfa_setup` | `mfa.py` |

## System Status

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/` | `status_root` | `status.py` |
| GET | `/ai/anthropic` | `anthropic_health` | `status.py` |
| GET | `/ai/anthropic/` | `anthropic_health` | `status.py` |
| GET | `/ai/openai` | `openai_health` | `status.py` |
| GET | `/ai/openai/` | `openai_health` | `status.py` |
| GET | `/ai/providers` | `ai_providers_health` | `status.py` |
| GET | `/ai/providers/` | `ai_providers_health` | `status.py` |
| GET | `/containers` | `containers_health` | `status.py` |
| GET | `/containers/` | `containers_health` | `status.py` |
| GET | `/database` | `database_health` | `status.py` |
| GET | `/database/` | `database_health` | `status.py` |
| GET | `/health` | `health_check` | `status.py` |
| GET | `/health/` | `health_check` | `status.py` |
| GET | `/ping` | `ping` | `status.py` |
| GET | `/ping` | `api_ping` | `status.py` |
| GET | `/ping/` | `api_ping` | `status.py` |
| GET | `/version` | `api_version` | `status.py` |
| GET | `/version/` | `api_version` | `status.py` |

## Teams

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{team_id}` | `delete_team` | `teams.py` |
| DELETE | `/{team_id}/members/{member_id}` | `remove_member` | `teams.py` |
| GET | `/{team_id}` | `get_team` | `teams.py` |
| GET | `/{team_id}/members` | `get_team_members` | `teams.py` |
| GET | `/{team_id}/messages` | `get_team_messages` | `teams.py` |
| GET | `/{team_id}/permissions` | `get_user_permissions` | `teams.py` |
| GET | `/{team_id}/treasury` | `get_treasury_balance` | `teams.py` |
| POST | `/create` | `create_team` | `teams.py` |
| POST | `/join` | `join_team` | `teams.py` |
| POST | `/leave` | `leave_team` | `teams.py` |
| POST | `/{team_id}/invite` | `invite_player` | `teams.py` |
| POST | `/{team_id}/messages` | `send_team_message` | `teams.py` |
| POST | `/{team_id}/transfer-leadership` | `transfer_leadership` | `teams.py` |
| POST | `/{team_id}/treasury/deposit` | `deposit_to_treasury` | `teams.py` |
| POST | `/{team_id}/treasury/transfer` | `transfer_to_player` | `teams.py` |
| POST | `/{team_id}/treasury/withdraw` | `withdraw_from_treasury` | `teams.py` |
| PUT | `/{team_id}` | `update_team` | `teams.py` |
| PUT | `/{team_id}/members/{member_id}/role` | `update_member_role` | `teams.py` |

## Test (Dev Only)

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/check-admin-exists` | `check_admin_exists` | `test.py` |
| POST | `/create-admin` | `create_admin` | `test.py` |

## User Management

| Method | Path | Function | Source |
|--------|------|----------|--------|
| DELETE | `/{user_id}` | `delete_user` | `users.py` |
| GET | `/` | `read_users` | `users.py` |
| GET | `/{user_id}` | `read_user` | `users.py` |
| POST | `/` | `create_user` | `users.py` |
| POST | `/admin` | `create_admin_user` | `users.py` |
| PUT | `/{user_id}` | `update_user` | `users.py` |
| PUT | `/{user_id}/password` | `reset_admin_password` | `users.py` |

## WebSocket

| Method | Path | Function | Source |
|--------|------|----------|--------|
| GET | `/health` | `websocket_health` | `enhanced_websocket.py` |
| GET | `/sector/{sector_id}/players` | `get_sector_players` | `websocket.py` |
| GET | `/stats` | `get_websocket_stats` | `websocket.py` |
| GET | `/team/{team_id}/players` | `get_team_players` | `websocket.py` |
| POST | `/broadcast` | `broadcast_message` | `websocket.py` |
| WEBSOCKET | `/admin` | `admin_websocket_endpoint` | `websocket.py` |
| WEBSOCKET | `/connect` | `websocket_endpoint` | `websocket.py` |
| WEBSOCKET | `/market-stream` | `public_market_stream` | `enhanced_websocket.py` |
| WEBSOCKET | `/trading/{player_id}` | `enhanced_trading_websocket` | `enhanced_websocket.py` |

---
*Auto-generated by _discover_api_endpoints.py*