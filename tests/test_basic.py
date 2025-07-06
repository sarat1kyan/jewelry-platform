import unittest
import sys
sys.path.append('..')
from app import app, JewelryPlatform

class TestBasicFunctionality(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
    
    def test_parameters_endpoint(self):
        response = self.app.get('/api/parameters')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('parameters', data)

if __name__ == '__main__':
    unittest.main()
