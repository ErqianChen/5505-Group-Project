import unittest
from app import app, db
from models import User, WorkoutRecord, SportsCategory
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-key'
        })
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()
            
        # Create standard categories and get timestamp for unique user
        timestamp = datetime.now().timestamp()
        categories = [
            SportsCategory(name='Running', met_value=9.8),
            SportsCategory(name='Cycling', met_value=7.5),
            SportsCategory(name='Swimming', met_value=8.0)
        ]
        db.session.add_all(categories)
        db.session.commit()

        # Create test user with unique email
        self.test_user = User(
            username=f'testuser_{timestamp}',
            email=f'test_{timestamp}@example.com',
            password_hash=generate_password_hash('password123'),
            nickname='Test User'
        )
        db.session.add(self.test_user)
        db.session.commit()
            
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_signup(self):
        """Test user signup functionality"""
        timestamp = datetime.now().timestamp()
        username = f'testuser_{timestamp}'
        email = f'test_{timestamp}@example.com'
        
        response = self.client.post('/api/signup', json={
            'username': username,
            'email': email,
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
                
        # Test duplicate signup
        response = self.client.post('/api/signup', json={
            'username': username,
            'email': email,
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 400)

    def test_login_logout(self):
        """Test login and logout functionality"""
        # Create test user with unique values
        timestamp = datetime.now().timestamp()
        username = f'testuser_{timestamp}'
        email = f'test_{timestamp}@example.com'
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash('password123'),
            nickname='Test User'
        )
        db.session.add(user)
        db.session.commit()
        
        # Test login
        response = self.client.post('/api/login', json={
            'username': username,
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
        # Create test user with unique values
        timestamp = datetime.now().timestamp()
        user = User(
            username=f'testuser_{timestamp}',
            email=f'test_{timestamp}@example.com',
            password_hash='hash'
        )
        db.session.add(user)
        db.session.commit()
        
        category = SportsCategory.query.filter_by(name='Running').first()
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
        timestamp = datetime.now().timestamp()
        user = User(
            username=f'testuser_{timestamp}',
            email=f'test_{timestamp}@example.com',
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

    def test_profile_update(self):
        """Test profile update functionality"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user.id
            
        from werkzeug.datastructures import MultiDict
        response = self.client.post('/api/account/edit', data=MultiDict([
            ('nickname', 'Updated Nick'),
            ('address', 'Updated Address')
        ]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        
        updated_user = User.query.get(self.test_user.id)
        self.assertEqual(updated_user.nickname, 'Updated Nick')
        self.assertEqual(updated_user.address, 'Updated Address')

    def test_workout_log(self):
        """Test workout logging functionality"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user.id
            
        from werkzeug.datastructures import MultiDict
        response = self.client.post('/api/log_cardio', data=MultiDict([
            ('activity', 'Running'),
            ('duration', '45'),
            ('calories', '450')
        ]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        
        records = WorkoutRecord.query.filter_by(user_id=self.test_user.id).all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].duration_min, 45)

    def test_invalid_login(self):
        """Test invalid login attempts"""
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json.get('success', False))

    def test_password_validation(self):
        """Test password validation rules"""
        # Test too short password
        timestamp = datetime.now().timestamp()
        response = self.client.post('/api/signup', json={
            'username': f'newuser_{timestamp}',
            'email': f'new_{timestamp}@test.com',
            'password': '123'  # too short
        })
        self.assertEqual(response.status_code, 400)
        
        # Test valid password
        timestamp = datetime.now().timestamp()
        response = self.client.post('/api/signup', json={
            'username': f'newuser_{timestamp}',
            'email': f'new_{timestamp}@test.com',
            'password': 'ValidPassword123'
        })
        self.assertEqual(response.status_code, 200)

    def test_record_validation(self):
        """Test workout record validation"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user.id
            
        # Test invalid duration
        from werkzeug.datastructures import MultiDict
        response = self.client.post('/api/log_cardio', data=MultiDict([
            ('activity', 'Running'),
            ('duration', '-5'),  # negative duration
            ('calories', '100')
        ]))
        self.assertEqual(response.status_code, 400)
        
        # Test too high duration
        response = self.client.post('/api/log_cardio', data=MultiDict([
            ('activity', 'Running'),
            ('duration', '1500'),  # too long
            ('calories', '100')
        ]))
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()