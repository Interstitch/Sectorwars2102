from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sectors import SHIP_TYPES
from models import db, User, Cargo, Sector
import os
import json
from datetime import datetime, timedelta

app = Flask('app')
app.secret_key = os.urandom(24)
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()

LAST_TURN_REFRESH = datetime.now()

def should_refresh_turns():
    global LAST_TURN_REFRESH
    now = datetime.now()
    if now - LAST_TURN_REFRESH > timedelta(days=1):
        LAST_TURN_REFRESH = now
        return True
    return False

def init_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()

        # Check if admin exists, if not create one
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@spacetrader.com',
                is_admin=True,
                ship_name='SS Admin',
                credits=1000000
            )
            admin.set_password('admin')
            db.session.add(admin)
            try:
                db.session.commit()
                print("Admin user created successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin: {e}")

        # Generate universe if it doesn't exist
        if Sector.query.count() == 0:
            try:
                from sectors import generate_universe
                generate_universe()
                print("Universe generated successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error generating universe: {e}")

# Initialize database and create admin user on startup
init_db()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            return render_template('register.html', error='Username already exists')

        user = User(
            username=request.form['username'],
            email=request.form['email'],
            ship_name=f"SS {request.form['username']}"
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
    if should_refresh_turns():
        current_user.turns = 100
        db.session.commit()

    loc = Sector.query.get(current_user.location)
    cargo_dict = {item.commodity: item.amount for item in current_user.cargo_items}

    return render_template('index.html',
        location=f"{current_user.location} - {loc.name}",
        port=loc.port_data if loc.port_data else "No port here",
        connected_sectors=loc.links,
        has_planet=loc.has_planet,
        status={
            "credits": current_user.credits,
            "cargo": cargo_dict,
            "cargo_space_used": sum(item.amount for item in current_user.cargo_items),
            "turns": current_user.turns,
            "ship_name": current_user.ship_name,
            "ship_type": current_user.ship_type,
            "docked": current_user.docked,
            "landed": current_user.landed,
            "fighters": current_user.fighters
        },
        ship_types=SHIP_TYPES
    )

@app.route("/land", methods=["POST"])
@login_required
def land():
    sector = SECTORS[current_user.location]
    if sector.get("has_planet"):
        current_user.landed = True
        db.session.commit()
    return redirect(url_for('home'))

@app.route("/takeoff", methods=["POST"])
@login_required
def takeoff():
    current_user.landed = False
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/buy_fighters", methods=["POST"])
@login_required
def buy_fighters():
    if current_user.location != 1 or not current_user.landed:
        return redirect(url_for('home'))

    try:
        amount = int(request.form.get("amount", 1))
    except:
        return redirect(url_for('home'))

    ship_data = SHIP_TYPES[current_user.ship_type]
    total_cost = amount * 1000

    if (current_user.fighters + amount <= ship_data["fighter_capacity"] and
        current_user.credits >= total_cost):
        current_user.credits -= total_cost
        current_user.fighters += amount
        db.session.commit()

    return redirect(url_for('home'))

@app.route("/buy_ship", methods=["POST"])
@login_required
def buy_ship():
    if current_user.location != 1 or not current_user.landed:
        return redirect(url_for('home'))

    ship_type = request.form.get("ship_type")
    if ship_type in SHIP_TYPES:
        cost = SHIP_TYPES[ship_type]["price"]
        if current_user.credits >= cost:
            current_user.credits -= cost
            current_user.ship_type = ship_type
            current_user.ship_name = f"SS {ship_type}"
            db.session.commit()
    return redirect(url_for('home'))

@app.route("/move/<int:sector_id>", methods=["POST"])
@login_required
def move(sector_id):
    current = current_user.location
    current_sector = Sector.query.get(current)
    if sector_id in current_sector.links:
        current_user.location = sector_id
        current_user.turns -= 1
        db.session.commit()

        # Check if player has population and wants to claim planet
        if (SECTORS[sector_id].get("has_planet") and
            not SECTORS[sector_id].get("planet_owner") and
            any(item.commodity == "Population" and item.amount >= 10000 for item in current_user.cargo_items) and
            current_user.credits >= 10000):
            SECTORS[sector_id]["planet_owner"] = current_user.ship_name
            for item in current_user.cargo_items:
                if item.commodity == "Population":
                    item.amount -= 10000
                    if item.amount <= 0:
                        db.session.delete(item)
                    break
            current_user.credits -= 10000
            db.session.commit()

        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route("/dock", methods=["POST"])
@login_required
def dock():
    sector = Sector.query.get(current_user.location)
    if not sector or not sector.port_data:
        return jsonify({"error": "No port in this sector"}), 400
    current_user.docked = True
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/undock", methods=["POST"])
@login_required
def undock():
    current_user.docked = False
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/trade", methods=["POST"])
@login_required
def trade():
    if not current_user.docked:
        return redirect(url_for('home'))
    action = request.form.get("action")
    commodity = request.form.get("commodity")
    try:
        amount = int(request.form.get("amount", 0))
    except:
        return redirect(url_for('home'))
    sector = SECTORS[current_user.location]
    port = sector.get("port")

    if not port:
        return jsonify({"error": "No port in this sector"}), 400

    if action == "buy":
        commodity_price = port["sell"].get(commodity)
        if commodity_price:
            total = commodity_price * amount
            ship_data = SHIP_TYPES[current_user.ship_type]
            current_cargo = sum(item.amount for item in current_user.cargo_items)

            if (current_user.credits >= total and
                port["inventory"][commodity] >= amount and
                current_cargo + amount <= ship_data["cargo_capacity"]):

                current_user.credits -= total
                port["inventory"][commodity] -= amount
                cargo_item = next((item for item in current_user.cargo_items if item.commodity == commodity), None)
                if cargo_item:
                    cargo_item.amount += amount
                else:
                    cargo_item = Cargo(user_id=current_user.id, commodity=commodity, amount=amount)
                    db.session.add(cargo_item)
                db.session.commit()
            return redirect(url_for('home'))
        return redirect(url_for('home'))

    if action == "sell":
        commodity_price = port["buy"].get(commodity)
        if commodity_price and commodity in [item.commodity for item in current_user.cargo_items]:
            cargo_item = next((item for item in current_user.cargo_items if item.commodity == commodity))
            if cargo_item.amount >= amount and amount > 0:
                total = commodity_price * amount
                cargo_item.amount -= amount
                if cargo_item.amount <= 0:
                    db.session.delete(cargo_item)
                port["inventory"][commodity] = port["inventory"].get(commodity, 0) + amount
                current_user.credits += total
                db.session.commit()
        return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.route("/admin")
@login_required
def admin_panel():
    if not current_user.is_admin:
        return redirect(url_for('home'))
        
    sector_search = request.args.get('sector_search', '')
    min_fighters = request.args.get('min_fighters', type=int)
    has_planet = request.args.get('has_planet', type=int)
    
    query = Sector.query
    
    if sector_search:
        query = query.filter(db.or_(
            Sector.id == sector_search if sector_search.isdigit() else False,
            Sector.name.ilike(f'%{sector_search}%')
        ))
    
    if min_fighters is not None:
        query = query.filter(db.or_(
            Sector.planet_fighters >= min_fighters,
            Sector.sector_fighters >= min_fighters
        ))
        
    if has_planet is not None:
        query = query.filter(Sector.has_planet == bool(has_planet))
        
    sectors = {sector.id: {
        'id': sector.id,
        'name': sector.name,
        'has_planet': sector.has_planet,
        'planet_owner': sector.planet_owner,
        'port': sector.port_data,
        'links': sector.links,
        'planet_fighters': sector.planet_fighters,
        'sector_fighters': sector.sector_fighters,
        'is_earth': sector.is_earth,
        'x': None,  # Will be set by D3
        'y': None   # Will be set by D3
    } for sector in Sector.query.all()}
    return render_template('admin.html', sectors=sectors)

@app.route("/admin/update_sector", methods=["POST"])
@login_required
def update_sector():
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    sector = Sector.query.get(data['sector_id'])
    if not sector:
        return jsonify({"error": "Sector not found"}), 404
        
    field = data['field']
    value = data['value']
    
    if hasattr(sector, field):
        if field == 'has_planet':
            setattr(sector, field, value == 'true' or value == True)
        elif field in ['planet_fighters', 'sector_fighters']:
            setattr(sector, field, int(value))
        else:
            setattr(sector, field, value)
            
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"error": "Invalid field"}), 400

@app.route("/admin/regenerate_universe", methods=["POST"])
@login_required
def regenerate_universe():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    try:
        from sectors import generate_universe
        generate_universe()
        flash('Universe has been regenerated!')
        return redirect(url_for('admin_panel'))
    except Exception as e:
        flash(f'Error regenerating universe: {str(e)}', 'error')
        return redirect(url_for('admin_panel'))
    for i in range(2, 17):
        SECTORS[i] = {
            "name": f"Sector {i}",
            "has_planet": random.random() < 0.4,
            "planet_owner": None,
            "port": generate_port(),
            "links": random.sample([j for j in range(1, 17) if j != i], random.randint(2, 4))
        }
    flash('Universe has been regenerated!')
    return redirect(url_for('admin_panel'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)
@app.route('/test/reset', methods=['POST'])
def test_reset():
    if not app.config['TESTING']:
        return jsonify({'error': 'Not allowed in production'}), 403
    db.drop_all()
    db.create_all()
    return jsonify({'status': 'ok'})

@app.route('/test/setup', methods=['POST'])
def test_setup():
    if not app.config['TESTING']:
        return jsonify({'error': 'Not allowed in production'}), 403
    data = request.json
    
    # Create test user
    user = User(
        username=data['user']['username'],
        email=data['user']['email'],
        ship_type=data['user']['ship_type'],
        ship_name=data['user']['ship_name']
    )
    user.set_password(data['user']['password'])
    user.credits = data['user']['credits']
    user.location = data['user']['location']
    db.session.add(user)
    
    # Create test sector
    sector = Sector(**data['sector'])
    db.session.add(sector)
    
    db.session.commit()
    return jsonify({'status': 'ok'})
