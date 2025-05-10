
# Space Trader Admin UI Documentation

## Overview
The administrative interface provides a 2D visualization of the game universe and tools for managing sector information. The interface is built using D3.js for visualization and includes interactive features for real-time sector management.

## Layout Components

### Header Section
- Fixed position header with title "Space Trader Admin"
- Sticky positioning ensures visibility while scrolling

### Stats Panel
- Displays key universe statistics:
  - Total number of sectors
  - Number of planets
  - Number of active ports

### Search & Filter Panel
- Search by Sector ID or Name
- Filter by minimum fighters
- Filter by planet status (has planet/no planet)
- Real-time filtering updates visualization

### Action Buttons
- "Regenerate Universe" button - Recreates entire universe
- "Back to Game" button - Returns to main game interface

## Universe Visualization

### Map Display
- Interactive 2D visualization using D3.js
- Full-width display with responsive scaling
- Dark theme background for better visibility

### Sector Nodes
- Circular nodes representing sectors
- Color coding:
  - Green: Sectors with planets
  - Gray: Sectors without planets
- Node information displays sector ID

### Connections
- Lines between nodes showing sector connections
- Gray connection lines for visual clarity
- Interactive paths update with node movement

### Interactive Features
- Zoom functionality (0.1x to 4x scale)
- Pan navigation across the universe map
- Drag and drop sector repositioning
- Click sectors to edit properties

## Sector Editor

### Popup Interface
- Modal display with sector details
- Shows when clicking sector nodes
- Positioned relative to click location

### Editable Properties
- Basic Settings:
  - Has Planet toggle
  - Has Port toggle
  - Planet Name
- Defense Settings:
  - Planet Fighters (0-1000)
  - Sector Fighters (0-1000)
- Port Trading (if port exists):
  - Inventory levels
  - Buy prices
  - Sell prices

### Real-time Updates
- Changes apply immediately
- Visual feedback on updates
- Automatic universe refresh

## Mobile Responsiveness
- Adaptive layout for different screen sizes
- Touch-friendly controls
- Centered popup positioning on mobile
- Scalable visualization

## Technical Implementation
- D3.js for visualization
- Hammer.js for touch interactions
- Real-time AJAX updates
- Responsive CSS Grid layout
- Event-driven architecture

## Security
- Admin-only access
- Authorization checks on all operations
- Protected API endpoints
- Input validation and sanitization
