
import random
from models import db, Sector
from collections import deque

COMMODITIES = {
    "Food": {"base_price": 100},
    "Tech": {"base_price": 250},
    "Ore": {"base_price": 80},
    "Fuel": {"base_price": 150},
    "Population": {"base_price": 50}
}

SHIP_TYPES = {
    "Light Freighter": {"price": 1000, "cargo_capacity": 50, "fighter_capacity": 2},
    "Medium Hauler": {"price": 5000, "cargo_capacity": 100, "fighter_capacity": 4},
    "Heavy Transport": {"price": 10000, "cargo_capacity": 200, "fighter_capacity": 6},
    "Luxury Yacht": {"price": 15000, "cargo_capacity": 150, "fighter_capacity": 3}
}

def generate_port():
    if random.random() < 0.4:  # 40% chance of having a port
        return {
            "buy": {k: v["base_price"] + random.randint(-20, 20) for k, v in COMMODITIES.items()},
            "sell": {k: v["base_price"] + random.randint(-20, 20) for k, v in COMMODITIES.items()},
            "inventory": {k: random.randint(100, 1000) for k in COMMODITIES.keys()},
            "ships": SHIP_TYPES if random.random() < 0.2 else {}  # 20% chance of selling ships
        }
    return None

def generate_universe():
    # Clear existing universe
    Sector.query.delete()
    
    # Create Earth (Sector 1)
    earth = Sector(
        id=1,
        name="Terra Prime",
        has_planet=True,
        port_data={
            "buy": {k: v["base_price"] for k, v in COMMODITIES.items()},
            "sell": {k: v["base_price"] for k, v in COMMODITIES.items()},
            "inventory": {k: 1000 for k in COMMODITIES.keys()},
            "ships": SHIP_TYPES
        },
        links=[],
        is_earth=True
    )
    db.session.add(earth)

    # Generate other sectors (2-100)
    sectors = []
    for i in range(2, 101):
        sector = Sector(
            id=i,
            name=f"Sector {i}",
            has_planet=random.random() < 0.3,  # 30% chance of planet
            port_data=generate_port(),
            links=[],
            planet_fighters=random.randint(5, 20) if random.random() < 0.2 else 0,  # 20% chance of planet fighters
            sector_fighters=random.randint(3, 15) if random.random() < 0.15 else 0  # 15% chance of sector fighters
        )
        sectors.append(sector)
        db.session.add(sector)

    # Generate connections using a modified DFS to ensure connectivity
    def connect_sectors(start, remaining):
        visited = set()
        stack = deque([(start, [])])
        
        while stack and remaining:
            current, path = stack.popleft()
            if current in visited:
                continue
                
            visited.add(current)
            
            # Add 2-4 random connections
            possible_connections = [s for s in remaining if s != current]
            num_connections = min(random.randint(2, 4), len(possible_connections))
            connections = random.sample(possible_connections, num_connections)
            
            for conn in connections:
                if current == 1:
                    earth.links.append(conn)
                else:
                    sectors[current-2].links.append(conn)
                if conn == 1:
                    earth.links.append(current)
                else:
                    sectors[conn-2].links.append(current)
                    
                stack.append((conn, path + [current]))
            
            remaining.remove(current)
    
    # Start from Earth (sector 1) and ensure all sectors are connected
    sectors_to_connect = set(range(1, 101))
    connect_sectors(1, sectors_to_connect)
    
    db.session.commit()

