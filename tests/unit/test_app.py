import unittest
from app import app, db
from models import User, WorkoutRecord, SportsCategory
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()
            
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_signup(self):
        """Test user signup functionality"""
        response = self.client.post('/api/signup', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
                
        # Test duplicate signup
        response = self.client.post('/api/signup', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 400)

    def test_login_logout(self):
        """Test login and logout functionality"""
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()
        
        # Test login
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        
        # Test logout
        response = self.client.post('/api/logout')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])

    def test_workout_metrics(self):
        """Test workout metrics calculation"""
        # Create test user and workout records
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hash'
        )
        category = SportsCategory(name='Running', met_value=9.8)
        db.session.add_all([user, category])
        db.session.commit()
        
        record = WorkoutRecord(
            user_id=user.id,
            category_id=category.id,
            date=date.today(),
            duration_min=60,
            difficulty=3,
            calories_burn=500
        )
        db.session.add(record)
        db.session.commit()
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = user.id
            
        response = self.client.get('/api/record/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['current_streak'], 1)
        self.assertEqual(response.json['total_calories'], 500.0)
        self.assertEqual(response.json['total_hours'], 1.0)

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        response = self.client.get('/api/record/metrics')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Unauthorized')

    def test_workout_trend(self):
        """Test workout trend data calculation"""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hash'
        )
        db.session.add(user)
        db.session.commit()
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = user.id
            
        response = self.client.get('/api/record/trend')
        self.assertEqual(response.status_code, 200)
        self.assertIn('labels', response.json)
        self.assertIn('you', response.json)
        self.assertIn('average', response.json)

if __name__ == '__main__':
    unittest.main()