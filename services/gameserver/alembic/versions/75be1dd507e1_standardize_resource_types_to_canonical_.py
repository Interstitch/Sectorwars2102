"""standardize resource types to canonical list

This migration updates the resource_type enum to match the canonical resource list
defined in FEATURES/DEFINITIONS/RESOURCE_TYPES.md

OLD resources (12 total):
- FUEL, ORGANICS, EQUIPMENT, POPULATION, ORE, MINERALS, LUXURY_GOODS, TECHNOLOGY,
  MEDICAL_SUPPLIES, INDUSTRIAL_MATERIALS, QUANTUM_COMPONENTS, EXOTIC_MATTER

NEW resources (15 total, aligned with RESOURCE_TYPES.md):
- Core Commodities (7): ORE, BASIC_FOOD, GOURMET_FOOD, FUEL, TECHNOLOGY,
  EXOTIC_TECHNOLOGY, LUXURY_GOODS
- Strategic Resources (4): POPULATION, QUANTUM_SHARDS, QUANTUM_CRYSTALS, COMBAT_DRONES
- Rare Materials (2): PRISMATIC_ORE, PHOTONIC_CRYSTALS

Revision ID: 75be1dd507e1
Revises: a1b2c3d4e5f6
Create Date: 2025-11-16 15:27:33.493160

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '75be1dd507e1'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Replace old resource_type enum with canonical resource list.

    Strategy: Create temporary enum → Update columns → Drop old → Rename new
    This preserves any existing data while updating the enum definition.
    """

    # Step 1: Create temporary enum with new canonical values
    op.execute("""
        CREATE TYPE resource_type_new AS ENUM (
            'ORE',
            'BASIC_FOOD',
            'GOURMET_FOOD',
            'FUEL',
            'TECHNOLOGY',
            'EXOTIC_TECHNOLOGY',
            'LUXURY_GOODS',
            'POPULATION',
            'QUANTUM_SHARDS',
            'QUANTUM_CRYSTALS',
            'COMBAT_DRONES',
            'PRISMATIC_ORE',
            'PHOTONIC_CRYSTALS'
        )
    """)

    # Step 2: Update resources table - map old values to new equivalents where possible
    # ORGANICS → BASIC_FOOD, MINERALS → ORE, others may fail for legacy data (expected for fresh DB)
    op.execute("""
        ALTER TABLE resources
        ALTER COLUMN type TYPE resource_type_new
        USING (
            CASE type::text
                WHEN 'ORGANICS' THEN 'BASIC_FOOD'::resource_type_new
                WHEN 'MINERALS' THEN 'ORE'::resource_type_new
                WHEN 'EQUIPMENT' THEN 'TECHNOLOGY'::resource_type_new
                WHEN 'MEDICAL_SUPPLIES' THEN 'BASIC_FOOD'::resource_type_new
                WHEN 'INDUSTRIAL_MATERIALS' THEN 'ORE'::resource_type_new
                WHEN 'QUANTUM_COMPONENTS' THEN 'QUANTUM_SHARDS'::resource_type_new
                WHEN 'EXOTIC_MATTER' THEN 'EXOTIC_TECHNOLOGY'::resource_type_new
                ELSE type::text::resource_type_new
            END
        )
    """)

    # Step 3: Update market_transactions table with same mapping
    op.execute("""
        ALTER TABLE market_transactions
        ALTER COLUMN resource_type TYPE resource_type_new
        USING (
            CASE resource_type::text
                WHEN 'ORGANICS' THEN 'BASIC_FOOD'::resource_type_new
                WHEN 'MINERALS' THEN 'ORE'::resource_type_new
                WHEN 'EQUIPMENT' THEN 'TECHNOLOGY'::resource_type_new
                WHEN 'MEDICAL_SUPPLIES' THEN 'BASIC_FOOD'::resource_type_new
                WHEN 'INDUSTRIAL_MATERIALS' THEN 'ORE'::resource_type_new
                WHEN 'QUANTUM_COMPONENTS' THEN 'QUANTUM_SHARDS'::resource_type_new
                WHEN 'EXOTIC_MATTER' THEN 'EXOTIC_TECHNOLOGY'::resource_type_new
                ELSE resource_type::text::resource_type_new
            END
        )
    """)

    # Step 4: Drop old enum type
    op.execute("DROP TYPE resource_type")

    # Step 5: Rename new enum to official name
    op.execute("ALTER TYPE resource_type_new RENAME TO resource_type")


def downgrade() -> None:
    """
    Restore old resource_type enum values.

    WARNING: This will lose data for resources that don't exist in the old enum!
    Only use for rollback immediately after migration, not on production data.
    """

    # Step 1: Create temporary enum with old values
    op.execute("""
        CREATE TYPE resource_type_old AS ENUM (
            'FUEL',
            'ORGANICS',
            'EQUIPMENT',
            'POPULATION',
            'ORE',
            'MINERALS',
            'LUXURY_GOODS',
            'TECHNOLOGY',
            'MEDICAL_SUPPLIES',
            'INDUSTRIAL_MATERIALS',
            'QUANTUM_COMPONENTS',
            'EXOTIC_MATTER'
        )
    """)

    # Step 2: Update resources table - map new values back to old where possible
    op.execute("""
        ALTER TABLE resources
        ALTER COLUMN type TYPE resource_type_old
        USING (
            CASE type::text
                WHEN 'BASIC_FOOD' THEN 'ORGANICS'::resource_type_old
                WHEN 'GOURMET_FOOD' THEN 'ORGANICS'::resource_type_old
                WHEN 'EXOTIC_TECHNOLOGY' THEN 'EXOTIC_MATTER'::resource_type_old
                WHEN 'QUANTUM_SHARDS' THEN 'QUANTUM_COMPONENTS'::resource_type_old
                WHEN 'QUANTUM_CRYSTALS' THEN 'QUANTUM_COMPONENTS'::resource_type_old
                WHEN 'COMBAT_DRONES' THEN 'EQUIPMENT'::resource_type_old
                WHEN 'PRISMATIC_ORE' THEN 'MINERALS'::resource_type_old
                WHEN 'PHOTONIC_CRYSTALS' THEN 'EXOTIC_MATTER'::resource_type_old
                ELSE type::text::resource_type_old
            END
        )
    """)

    # Step 3: Update market_transactions table
    op.execute("""
        ALTER TABLE market_transactions
        ALTER COLUMN resource_type TYPE resource_type_old
        USING (
            CASE resource_type::text
                WHEN 'BASIC_FOOD' THEN 'ORGANICS'::resource_type_old
                WHEN 'GOURMET_FOOD' THEN 'ORGANICS'::resource_type_old
                WHEN 'EXOTIC_TECHNOLOGY' THEN 'EXOTIC_MATTER'::resource_type_old
                WHEN 'QUANTUM_SHARDS' THEN 'QUANTUM_COMPONENTS'::resource_type_old
                WHEN 'QUANTUM_CRYSTALS' THEN 'QUANTUM_COMPONENTS'::resource_type_old
                WHEN 'COMBAT_DRONES' THEN 'EQUIPMENT'::resource_type_old
                WHEN 'PRISMATIC_ORE' THEN 'MINERALS'::resource_type_old
                WHEN 'PHOTONIC_CRYSTALS' THEN 'EXOTIC_MATTER'::resource_type_old
                ELSE resource_type::text::resource_type_old
            END
        )
    """)

    # Step 4: Drop new enum type
    op.execute("DROP TYPE resource_type")

    # Step 5: Rename old enum back to official name
    op.execute("ALTER TYPE resource_type_old RENAME TO resource_type")