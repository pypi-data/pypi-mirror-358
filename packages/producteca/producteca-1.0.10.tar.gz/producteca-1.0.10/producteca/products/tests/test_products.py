import unittest
from unittest.mock import patch, Mock
from producteca.config.config import ConfigProducteca
from producteca.products.products import Product, MeliProduct


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.config = ConfigProducteca(token="test_id", api_key="test_secret")
        self.test_product = Product(
            config=self.config,
            sku="TEST001",
            name="Test Product",
            code="TEST001"
        )

    @patch('requests.post')
    def test_create_product_success(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "sku": "TEST001"}
        mock_post.return_value = mock_response

        response, status_code = self.test_product.create()
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["sku"], "TEST001")

    @patch('requests.post')
    def test_create_product_not_exist(self, mock_post):
        # Mock product not found response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        response, status_code = self.test_product.create()
        
        self.assertEqual(status_code, 204)
        self.assertEqual(response["Message"], "Product does not exist and the request cant create if it does not exist")

    @patch('requests.post')
    def test_update_product_success(self, mock_post):
        # Mock successful update
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "sku": "TEST001", "name": "Updated Product"}
        mock_post.return_value = mock_response

        response, status_code = self.test_product.update()
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["name"], "Updated Product")

    @patch('requests.get')
    def test_get_product(self, mock_get):
        # Mock get product response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "sku": "TEST001"}
        mock_get.return_value = mock_response

        response, status_code = Product.get(self.config, 1)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["sku"], "TEST001")

    @patch('requests.get')
    def test_get_bundle(self, mock_get):
        # Mock get bundle response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sku": "TEST001", "bundles": []}
        mock_get.return_value = mock_response

        product, status_code = Product.get_bundle(self.config, 1)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(product.sku, "TEST001")

    @patch('requests.get')
    def test_get_ml_integration(self, mock_get):
        # Mock ML integration response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sku": "TEST001", "integrations": []}
        mock_get.return_value = mock_response

        product, status_code = Product.get_ml_integration(self.config, 1)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(product.sku, "TEST001")

if __name__ == '__main__':
    unittest.main()
