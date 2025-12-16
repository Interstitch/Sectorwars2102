# Unused API Endpoints Analysis

**Generated:** 2025-12-16
**Total Unused:** 19 endpoints

This document identifies API endpoints that have no detected frontend callers in player-client or admin-ui.
Each endpoint is analyzed for purpose, reason for being unused, and recommended action.

---

## Summary

| Category | Count | Recommendation |
|----------|-------|----------------|
| Admin endpoints awaiting UI | 10 | KEEP - Wire up frontend |
| Player endpoints awaiting UI | 6 | KEEP - Wire up frontend |
| Potentially redundant | 2 | REVIEW - May be obsolete |
| Security-critical | 1 | KEEP - Essential feature |

---

## Detailed Analysis

### 1. Drones API

#### `GET /api/drones/{drone_id}` - get_drone
**File:** `drones.py:226-248`

**What it does:**
Retrieves detailed information about a specific drone by its UUID. Verifies ownership before returning data.

**Why unused:**
The frontend currently lists all player drones via `GET /api/drones/` and doesn't implement a "drone detail" view. The UI likely shows drone info inline in the list rather than a dedicated detail page.

**Recommendation:** `KEEP`
- Useful for future drone detail modal or expanded view
- Required for deep-linking to specific drone (e.g., from combat logs)
- Already implemented and tested

---

### 2. Economy API (Admin)

#### `GET /admin/economy/price-history/{commodity}` - get_price_history
**File:** `economy.py:208-246`

**What it does:**
Returns historical price data for a specific commodity across all ports. Supports filtering by port and time range. Data is formatted for charting (timestamp, buy_price, sell_price).

**Why unused:**
The admin economy dashboard doesn't currently render price history charts. The endpoint is ready but the visualization UI isn't implemented.

**Recommendation:** `KEEP`
- Essential for economy monitoring and market manipulation detection
- Already handles query parameters for filtering
- Wire up to a chart component in admin-ui (e.g., Recharts)

#### `POST /admin/economy/create-alert` - create_price_alert
**File:** `economy.py:361-382`

**What it does:**
Creates a new price monitoring alert that triggers when commodity prices cross specified thresholds. Tracks alert_type (price_spike, shortage, etc.), threshold_value, and station.

**Why unused:**
Admin UI displays existing alerts via `GET /price-alerts` but lacks a "Create Alert" button/form.

**Recommendation:** `KEEP`
- Critical for proactive economy management
- Enables automated price spike detection
- Wire up "Add Alert" form in admin economy dashboard

---

### 3. Events API (Admin)

#### `PUT /admin/events/{event_id}` - update_event
**File:** `events.py:288-359`

**What it does:**
Updates an existing game event's title, description, type, timing, affected regions, and effects. Replaces all effects with new ones provided.

**Why unused:**
Admin UI has event creation (`POST /`) but editing existing events isn't wired up. Users can only activate/deactivate, not modify.

**Recommendation:** `KEEP`
- Essential for event management (fix typos, adjust timing)
- Already handles all event fields
- Add "Edit" button to event cards in admin-ui

#### `DELETE /admin/events/{event_id}` - delete_event
**File:** `events.py:420-442`

**What it does:**
Deletes an event and all associated effects/participations. Prevents deletion of active events (must deactivate first).

**Why unused:**
Admin UI lacks delete button on event cards. Events accumulate without cleanup option.

**Recommendation:** `KEEP`
- Required for cleanup of old/failed events
- Has proper safety check (can't delete active)
- Add "Delete" button with confirmation modal

---

### 4. Fleets API (Player)

#### `GET /api/fleets/my-fleets` - get_my_fleets
**File:** `fleets.py:181-211`

**What it does:**
Returns all fleets where the player has ships assigned, regardless of team. Different from `GET /` which returns team fleets.

**Why unused:**
Frontend uses `GET /api/fleets/` (team fleets) exclusively. This endpoint is useful when a player's ships might be in fleets from allied teams.

**Recommendation:** `KEEP`
- Needed for "My Ships in Fleets" view
- Supports cross-team fleet participation scenarios
- Consider adding to fleet management UI

#### `GET /api/fleets/{fleet_id}` - get_fleet
**File:** `fleets.py:214-252`

**What it does:**
Returns detailed information about a specific fleet including total stats (firepower, shields, hull), commander info, and member count.

**Why unused:**
Fleet list shows summary info; no "Fleet Detail" view implemented. Missing import for `Fleet` model would cause runtime error.

**Recommendation:** `KEEP` (with fix)
- Essential for fleet detail view
- **BUG:** Line 223 references `Fleet` but it's imported at line 542 (bottom of file) - may cause runtime issues
- Wire up fleet detail modal/page

#### `DELETE /api/fleets/{fleet_id}` - disband_fleet
**File:** `fleets.py:411-436`

**What it does:**
Disbands a fleet, releasing all ships back to individual ownership. Only fleet commander or team leader can perform this action.

**Why unused:**
Fleet UI shows fleets but lacks "Disband" button. Fleet lifecycle management incomplete.

**Recommendation:** `KEEP`
- Essential for fleet cleanup after battles
- Proper permission checks in place
- Add "Disband" button with confirmation

---

### 5. Messages API (Player)

#### `DELETE /messages/{message_id}` - delete_message
**File:** `messages.py:148-168`

**What it does:**
Soft-deletes a message from the player's inbox. Uses MessageService.delete_message() which marks as deleted rather than removing.

**Why unused:**
Inbox UI displays messages but lacks delete functionality. Messages accumulate indefinitely.

**Recommendation:** `KEEP`
- Important for inbox management
- Uses soft-delete (reversible)
- Add delete button/swipe action in message list

---

### 6. MFA API (Admin)

#### `POST /auth/mfa/regenerate-backup-codes` - regenerate_backup_codes
**File:** `mfa.py:222-241`

**What it does:**
Generates new backup codes for an admin user, invalidating all previous codes. Returns the new codes which should be displayed once and stored securely.

**Why unused:**
Admin MFA settings UI has setup flow but not backup code regeneration option.

**Recommendation:** `KEEP` (Security-Critical)
- Essential security feature for MFA recovery
- Required when backup codes are exhausted/compromised
- Add "Regenerate Backup Codes" button in MFA settings

---

### 7. Teams API (Player)

#### `GET /teams/{team_id}` - get_team
**File:** `teams.py:152-183`

**What it does:**
Returns full team details including name, description, tag, leader, member count, ratings, and treasury balance. Public endpoint (no auth required).

**Why unused:**
Frontend likely fetches team info through player context or uses different approach. May also be called but with different URL pattern.

**Recommendation:** `KEEP`
- Essential for team profile views
- Public endpoint enables team discovery
- Used for viewing other teams' public info

#### `PUT /teams/{team_id}` - update_team
**File:** `teams.py:186-239`

**What it does:**
Updates team settings: description, tag, logo, recruitment status, max members, join requirements, resource sharing. Only leader/officers can update.

**Why unused:**
Team settings UI not implemented in player-client. Team creation exists but not editing.

**Recommendation:** `KEEP`
- Essential for team management
- Proper permission validation
- Build team settings page in player-client

#### `DELETE /teams/{team_id}` - delete_team
**File:** `teams.py:242-256`

**What it does:**
Deletes a team entirely. Only the team leader can perform this action.

**Why unused:**
No "Delete Team" option in UI. High-impact action may be intentionally hidden.

**Recommendation:** `KEEP`
- Required for team cleanup
- Proper permission check (leader only)
- Add with strong confirmation dialog

#### `POST /teams/{team_id}/transfer-leadership` - transfer_leadership
**File:** `teams.py:429-452`

**What it does:**
Transfers team leadership to another team member. Current leader loses leadership role.

**Why unused:**
Advanced team management feature not in UI. Leadership succession not implemented.

**Recommendation:** `KEEP`
- Important for leader handoff (inactive leaders, planned succession)
- Proper validation (new leader must be member)
- Add to team management settings

---

### 8. Translation API (i18n)

#### `GET /i18n/{language_code}` - get_translations
**File:** `translation.py:91-106`

**What it does:**
Returns all translations for a language, optionally filtered by namespace and with translator context included.

**Why unused:**
Frontend likely uses i18next with direct JSON file loading rather than API calls. Translations may be bundled at build time.

**Recommendation:** `REVIEW`
- May be redundant if using static i18n files
- Useful for dynamic/admin-managed translations
- Keep if planning database-driven translations; remove if purely file-based

#### `GET /i18n/{language_code}/{namespace}` - get_namespace_translations
**File:** `translation.py:109-123`

**What it does:**
Returns translations for a specific namespace (e.g., "common", "trading", "combat") in a language.

**Why unused:**
Same reason as above - frontend may use bundled translation files.

**Recommendation:** `REVIEW`
- More targeted than full language fetch
- Useful for lazy-loading translation namespaces
- Keep if i18n backend is planned; else remove

---

### 9. Users API (Admin)

#### `GET /admin/users/{user_id}` - read_user
**File:** `users.py:138-153`

**What it does:**
Returns a specific user by UUID. Admin-only endpoint for user management.

**Why unused:**
Admin UI lists all users via `GET /admin/users/` but doesn't drill into individual user details.

**Recommendation:** `KEEP`
- Essential for user management
- Needed for user detail/edit modal
- Wire up to user list row click/expand

#### `PUT /admin/users/{user_id}` - update_user
**File:** `users.py:156-207`

**What it does:**
Updates user details: username, email, is_active status. Validates uniqueness constraints. Updates timestamp.

**Why unused:**
Admin user list is display-only. No edit functionality implemented.

**Recommendation:** `KEEP`
- Essential for user management
- Handles validation (unique username/email)
- Build user edit form in admin-ui

#### `DELETE /admin/users/{user_id}` - delete_user
**File:** `users.py:210-239`

**What it does:**
Soft-deletes a user (sets deleted=true). Prevents self-deletion.

**Why unused:**
Admin user list lacks delete button. User cleanup not implemented.

**Recommendation:** `KEEP`
- Required for user management
- Uses soft-delete (recoverable)
- Prevents accidental self-deletion
- Add delete button with confirmation

---

## Action Items

### High Priority (Security/Core Features)
1. ☐ Wire up MFA backup code regeneration in admin settings
2. ☐ Implement admin user CRUD operations in admin-ui

### Medium Priority (Complete Feature Sets)
3. ☐ Add team settings page with update/delete capabilities
4. ☐ Implement fleet detail view and disband functionality
5. ☐ Add message deletion to inbox UI
6. ☐ Implement event editing and deletion in admin events

### Low Priority (Nice to Have)
7. ☐ Add drone detail modal
8. ☐ Implement price history charts in admin economy
9. ☐ Add price alert creation form
10. ☐ Review i18n strategy (API vs file-based)

---

## Potential Bugs Found

1. **fleets.py:223** - References `Fleet` model before import (import at line 542)
   - May cause `NameError` at runtime
   - Move import to top of file

---

*Last reviewed: 2025-12-16*
