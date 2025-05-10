import unittest
from main import app, db
from models import User, Sector, Ship, Cargo
from sectors import SHIP_TYPES

class TestTrading(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test user
        self.user = User(
            username='test_trader',
            email='test@trader.com',
            ship_type="Light Freighter",
            ship_name="SS Test Trader"
        )
        self.user.set_password('password123')
        self.user.credits = 1000
        self.user.location = 1
        db.session.add(self.user)
        db.session.commit() #Commit user to DB

        # Create test sector with port
        self.sector = Sector(
            id=1,
            name="Test Sector",
            has_planet=True,
            port_data={
                "buy": {"Food": 100},
                "sell": {"Food": 80},
                "inventory": {"Food": 1000},
                "ships": {}
            },
            links=[2, 3, 4]
        )
        db.session.add(self.sector)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_trading_flow(self):
        with self.client:
            # Login
            response = self.client.post('/login', data={
                'username': 'test_trader',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Dock at port
            response = self.client.post('/dock', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # Verify docked status
            user = User.query.filter_by(username='test_trader').first()
            self.assertTrue(user.docked, "User should be docked")

            # Buy food
            initial_credits = user.credits
            food_price = 80
            food_amount = 5

            response = self.client.post('/trade', data={
                'action': 'buy',
                'commodity': 'Food',
                'amount': food_amount
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Check credits were deducted
            user = User.query.refresh(user)
            expected_credits = initial_credits - (food_price * food_amount)
            self.assertEqual(user.credits, expected_credits, f"Expected {expected_credits} credits but got {user.credits}")

        # Check cargo was added
        cargo = Cargo.query.filter_by(user_id=user.id, commodity='Food').first()
        self.assertIsNotNone(cargo, "Cargo was not created")
        self.assertEqual(cargo.amount, food_amount, f"Expected {food_amount} food but got {cargo.amount}")

        # Sell food back to port
        response = self.client.post('/trade', data={
            'action': 'sell',
            'commodity': 'Food',
            'amount': food_amount
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check credits were added and cargo emptied
        user = User.query.filter_by(username='test_trader').first()
        expected_final_credits = initial_credits + ((100 - food_price) * food_amount)
        self.assertEqual(user.credits, expected_final_credits, 
                        f"Expected {expected_final_credits} credits but got {user.credits}")

        cargo = Cargo.query.filter_by(user_id=user.id, commodity='Food').first()
        self.assertIsNone(cargo, "Cargo should be deleted when empty")

if __name__ == '__main__':
    unittest.main()