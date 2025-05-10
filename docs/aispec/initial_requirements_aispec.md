# AI Spec: Sector Wars 2102 - Initial Developer Requirements (Iteration 1)

**Source Document:** `docs/developer_requirements/initial_requirements.md`
**Date:** May 10, 2025

## Core Technical Goals:
- Web-based application.
- Persistent universe.
- Design for future multiplayer.
- Scalable architecture.
- Modular game systems.

## Key Systems & Features (Initial Focus):
1.  **User Auth & Account Management:** Register, login/logout, session.
2.  **Basic Game State:** Player profile (name, ship, credits, location), ship instances, basic universe representation.
3.  **Galaxy Map & Navigation (Simplified):** 2D map, select destination, abstract travel.
4.  **Resource Representation:** Basic types (Fuel, Ore), player inventory.
5.  **Basic Actions (PoC):** Movement, abstract mining, abstract trading.
6.  **Database Backend:** PostgreSQL.
7.  **API Layer:** PHP-based (logic, data access, client-server communication).

## Technology Stack:
- Backend: PHP (framework TBD).
- Database: PostgreSQL.
- Containerization: Docker.
- Frontend: HTML, CSS, JavaScript (framework TBD).

## Non-Functional (Initial):
- Basic security (SQLi, XSS).
- Data integrity.
