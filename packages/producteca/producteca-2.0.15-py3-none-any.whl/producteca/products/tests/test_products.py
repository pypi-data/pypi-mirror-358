import unittest
from unittest.mock import patch, Mock
from producteca.products.products import Product
from producteca.client import ProductecaClient


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.client = ProductecaClient(token="test_client_id", api_key="test_client_secret")
        self.test_product = Product(
            sku="TEST001",
            name="Test Product",
            code="TEST001",
            category="Test"
        )

    @patch('requests.post')
    def test_create_product_success(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_product.model_dump()
        mock_post.return_value = mock_response

        response = self.client.Product(**self.test_product.model_dump()).create()
        
        self.assertEqual(response.sku, "TEST001")

    @patch('requests.post')
    def test_create_product_not_exist(self, mock_post):
        # Mock product not found response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            self.client.Product.create()

    @patch('requests.post')
    def test_update_product_success(self, mock_post):
        # Mock successful update
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_product.model_dump()
        mock_post.return_value = mock_response

        response = self.client.Product(**self.test_product.model_dump()).update()
        
        self.assertEqual(response.name, "Test Product")

    @patch('requests.get')
    def test_get_product(self, mock_get):
        # Mock get product response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_product.model_dump()
        mock_get.return_value = mock_response

        response = self.client.Product.get(1)
        
        self.assertEqual(response.sku, "TEST001")

    @patch('requests.get')
    def test_get_bundle(self, mock_get):
        # Mock get bundle response
        mock_response = Mock()
        mock_response.status_code = 200
        test_prod = self.test_product.model_dump()
        test_prod.update({"sku": "TEST001", "bundles": []})
        mock_response.json.return_value = test_prod
        mock_get.return_value = mock_response

        product = self.client.Product.get_bundle(1)
        
        self.assertEqual(product.sku, "TEST001")

    @patch('requests.get')
    def test_get_ml_integration(self, mock_get):
        # Mock ML integration response
        mock_response = Mock()
        mock_response.status_code = 200
        test_prod = self.test_product.model_dump()
        test_prod.update({"sku": "TEST001", "integrations": []})
        mock_response.json.return_value = test_prod
        mock_get.return_value = mock_response

        product = self.client.Product.get_ml_integration(1)
        
        self.assertEqual(product.sku, "TEST001")


if __name__ == '__main__':
    unittest.main()
