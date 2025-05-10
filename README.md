
# Space Trader Game

A web-based space trading simulation game built with Flask and PostgreSQL.

## Overview

Space Trader is a turn-based trading game where players navigate through different sectors, trade commodities, manage ships, and colonize planets.

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Web Server**: Gunicorn
- **Frontend**: HTML/CSS with vanilla JavaScript

## Database Schema 222

The game uses PostgreSQL with the following main tables:

### User Table
- Stores player information
- Tracks credits, location, ship details
- Manages authentication and admin status

### Cargo Table
- Tracks player inventory
- Links to users through foreign key relationships
- Manages commodity quantities

### Sector Table
- Stores universe structure
- Tracks planet ownership
- Contains port and trading data

## Game Features

- Multiple ship types with different capacities
- Dynamic trading system with fluctuating prices
- Planet colonization system
- Turn-based movement between sectors
- Admin panel for universe management

## Development Setup

1. The project uses PostgreSQL 16 (automatically configured in Replit)
2. Database initializes automatically on first run
3. Default admin credentials:
   - Username: admin
   - Password: admin

## Running the Game

The game runs on port 81 in development and port 5000 in production. Gunicorn is configured to handle the web server duties.

## Database Migrations

The project uses Flask-Migrate for database schema changes. Migrations are handled automatically through the SQLAlchemy ORM.

## Game Rules

See GAME_RULES.md for detailed gameplay mechanics and rules.
