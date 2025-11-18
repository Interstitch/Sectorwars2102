#!/bin/bash
# Reset First Login for Testing
# This script clears the first login session for the current user so you can test again

echo "🔄 Resetting first login session..."

docker-compose exec -T database psql -U postgres -d sectorwars_dev <<SQL
-- Get your player ID
DO \$\$
DECLARE
    v_player_id uuid;
    v_session_id uuid;
BEGIN
    -- Find the player for user XelaNull
    SELECT p.id INTO v_player_id
    FROM players p
    JOIN users u ON p.user_id = u.id
    WHERE u.username = 'XelaNull';

    IF v_player_id IS NULL THEN
        RAISE NOTICE 'Player not found for user XelaNull';
        RETURN;
    END IF;

    -- Get current session ID
    SELECT current_session_id INTO v_session_id
    FROM player_first_login_states
    WHERE player_id = v_player_id;

    -- Clear the session reference
    UPDATE player_first_login_states
    SET current_session_id = NULL,
        has_completed_first_login = false
    WHERE player_id = v_player_id;

    RAISE NOTICE 'Reset first login state for player: %', v_player_id;

    -- If there was a session, delete it
    IF v_session_id IS NOT NULL THEN
        DELETE FROM dialogue_exchanges WHERE session_id = v_session_id;
        DELETE FROM ship_presentation_options WHERE session_id = v_session_id;
        DELETE FROM first_login_sessions WHERE id = v_session_id;
        RAISE NOTICE 'Deleted session: %', v_session_id;
    END IF;

    RAISE NOTICE '✅ First login reset complete! Refresh your browser.';
END \$\$;
SQL

echo ""
echo "✅ Done! Now refresh your browser to start a fresh first login session."
