#!/bin/bash
set -e

echo "WARNING: This script will reset the Alembic migration state and drop database tables."
echo "It should only be used in development environments."
echo "Press Ctrl+C to cancel or Enter to continue..."
read

echo "Checking current migration state..."
alembic current

echo "Connecting to database..."
# Drop existing enum types
python -c "
from src.core.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)
print('Current tables in database:', inspector.get_table_names())

enums_to_drop = ['ship_type', 'failure_type', 'upgrade_type', 'insurance_type', 'reputation_level']

with engine.connect() as conn:
    # First, drop all related tables
    tables_to_drop = [
        'player_ports', 'player_planets', 'ship_specifications', 
        'team_reputations', 'reputations', 'ships', 'players',
        'ports', 'planets', 'teams'
    ]
    
    for table in tables_to_drop:
        try:
            conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
            print(f'Dropped table: {table}')
        except Exception as e:
            print(f'Error dropping {table}: {e}')
    
    # Now drop all enum types
    for enum in enums_to_drop:
        try:
            conn.execute(text(f'DROP TYPE IF EXISTS {enum} CASCADE'))
            print(f'Dropped enum type: {enum}')
        except Exception as e:
            print(f'Error dropping {enum}: {e}')
            
    # Reset Alembic version to the previous migration
    try:
        # Check if b42e19a78c52 is the current version
        result = conn.execute(text(\"\"\"
            SELECT version_num FROM alembic_version WHERE version_num = 'b42e19a78c52'
        \"\"\"))
        
        if result.scalar():
            conn.execute(text(\"\"\"
                UPDATE alembic_version SET version_num = 'a69c2f372d7e'
                WHERE version_num = 'b42e19a78c52'
            \"\"\"))
            print('Reset Alembic version to a69c2f372d7e (player_credentials migration)')
        else:
            print('Current version is not b42e19a78c52, checking version...')
            result = conn.execute(text(\"\"\"SELECT version_num FROM alembic_version\"\"\"))
            version = result.scalar()
            print(f'Current Alembic version is: {version}')
    except Exception as e:
        print(f'Error resetting Alembic version: {e}')
    
    # Print remaining tables
    print('Remaining tables in database:', inspector.get_table_names())
"

echo "Migration state reset. You can now run 'alembic upgrade head' to apply migrations."
echo "Current Alembic version:"
alembic current 