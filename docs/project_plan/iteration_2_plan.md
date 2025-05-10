# Sector Wars 2102 - Project Plan: Iteration 2

**Date:** May 10, 2025 (Simulated - Day 2)
**Iteration Lead:** Project Planner (Simulated)

## Goals for Iteration 2:

1.  **Deepen Core Game Design:** Elaborate on existing game design documents with more specific details, examples, and initial balancing considerations.
2.  **Initiate Feature Documentation:** Begin drafting the first set of detailed feature documents for core gameplay systems.
3.  **Formalize Technical Specifications:** Refine the database schema with specific data types and constraints, and start outlining API endpoints.
4.  **Implement and Test Basic Docker Environment:** Ensure the defined Docker setup is functional and can run a placeholder PHP application.
5.  **Refine All Documentation:** Update all existing documents and AI Specs based on Iteration 2 developments.

## Key Deliverables for Iteration 2:

*   **Game Design Document (Updates & New):**
    *   `lore_premise.md` (v1.1): Add details on one key historical event post-Collapse and a brief description of a notable starting region.
    *   `core_mechanics.md` (v1.1): Further detail the "Exploration" and "Basic Combat" (conceptual) loops.
    *   `ship_concepts.md` (v1.1): Provide more specific example stats (e.g., cargo range, base speed, typical weapon hardpoints) for the "Pathfinder" and "Guardian" classes.
    *   `faction_concepts.md` (v1.1): Flesh out the "Terran Remnant Compact" (TRC) and "Orion Syndicate" with more details on their typical ship types, territories, and disposition towards new captains.
    *   **New:** `feature_galaxy_map_navigation.md` (v1.0): Detailed design for galaxy map UI, sector-to-sector navigation mechanics, and initial points of interest.
    *   **New:** `feature_basic_combat_loop.md` (v1.0): Conceptual outline of ship-to-ship combat (turn-based or real-time decision points, core stats involved, win/loss conditions for early game encounters).
*   **Developer Requirements (Updates & New):**
    *   `database_schema_v1.md` to be evolved into `database_schema_v2.md`: Add specific PostgreSQL data types, NOT NULL constraints, basic indexes, and foreign key relationships. Introduce tables for `ship_modules` (conceptual) and `player_inventory` (linking players to resources).
    *   `initial_requirements.md` to be evolved into `detailed_requirements_v1.md`: Outline key API endpoints for user authentication, galaxy map data retrieval, and ship movement actions.
    *   **New:** `api_design_v1.md`: Document the general structure of API requests/responses, authentication method, and versioning strategy.
*   **DevOps Setup (Updates & Testing):**
    *   `docker_setup.md` (v1.1): Add a section on common Docker commands (build, up, down, logs) and confirm PHP/PostgreSQL connectivity.
    *   `Dockerfile` (v1.1): Minor refinements if needed after testing.
    *   `docker-compose.yml` (v1.1): Add a service for Adminer (or similar DB management tool). Test basic PHP application connectivity with PostgreSQL within Docker.
*   **AI Specs (Updates & New):**
    *   Update all existing AI spec files to reflect changes in their source documents.
    *   Create new AI spec files for `feature_galaxy_map_navigation.md`, `feature_basic_combat_loop.md`, and `api_design_v1.md`.
*   **Project Plan:**
    *   `iteration_2_plan.md` (this document).

## Team Responsibilities (Simulated - Iteration 2 Focus):

*   **Project Planner:** Oversee Iteration 2, ensure deliverables are met, update this plan as needed.
*   **Game Designer:** Lead updates to `core_mechanics.md`, `ship_concepts.md`, `faction_concepts.md`, and create `feature_galaxy_map_navigation.md`, `feature_basic_combat_loop.md`.
*   **Lore and Wording Writer:** Lead updates to `lore_premise.md`, contribute to descriptive text in feature docs.
*   **Developer:** Lead evolution of `database_schema_v2.md`, `detailed_requirements_v1.md`, and create `api_design_v1.md`. Assist DevOps with application-specific aspects of Docker testing.
*   **DevOps:** Lead updates to `docker_setup.md`, `Dockerfile`, `docker-compose.yml`. Perform Docker environment testing and PHP-DB connectivity tests.

## Next Steps (Post Iteration 2):

1.  **Review & Refine:** Team review of all Iteration 2 deliverables.
2.  **Plan Iteration 3:** Define goals for Iteration 3, likely focusing on implementing a basic vertical slice of the core loop (e.g., login, view map, move ship, basic resource interaction) and further detailing more game features and systems.
