import unittest
from app import create_app, db
from app.models import User, Organisation

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user_successfully(self):
        response = self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('accessToken', response.get_json()['data'])

    def test_login_user_successfully(self):
        user = User(
            firstName='Jane',
            lastName='Doe',
            email='jane@example.com',
            password=hash_password('password'),
            phone='1234567890'
        )
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/auth/login', json={
            'email': 'jane@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('accessToken', response.get_json()['data'])

    def test_register_user_validation_errors(self):
        response = self.client.post('/auth/register', json={
            'firstName': '',
            'lastName': '',
            'email': 'invalid',
            'password': '',
            'phone': ''
        })
        self.assertEqual(response.status_code, 422)

    def test_register_user_duplicate_email(self):
        user = User(
            firstName='John',
            lastName='Doe',
            email='john@example.com',
            password=hash_password('password'),
            phone='1234567890'
        )
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/auth/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password',
            'phone': '0987654321'
        })
        self.assertEqual(response.status_code, 422)
