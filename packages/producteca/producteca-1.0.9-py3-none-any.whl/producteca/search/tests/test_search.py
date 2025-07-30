import unittest
from unittest.mock import patch, Mock
from producteca.config.config import ConfigProducteca
from producteca.search.search_sale_orders import SearchSalesOrder, SearchSalesOrderParams, SearchSalesOrderResponse
from producteca.search.search import SearchProduct, SearchProductParams

class TestSearchSalesOrder(unittest.TestCase):
    def setUp(self):
        self.config = ConfigProducteca(
            token="test_client_id",
            api_key="test_client_secret",
        )
        self.params = SearchSalesOrderParams(
            top=10,
            skip=0,
            filter="status eq 'confirmed'"
        )

    @patch('requests.get')
    def test_search_saleorder_success(self, mock_get):
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 1,
            "results": [{
                "id": "123",
                "status": "confirmed",
                "lines": [],
                "payments": [],
                "shipments": [],
                "integrations": [],
                "codes": [],
                "integration_ids": [],
                "product_names": [],
                "skus": [],
                "tags": [],
                "brands": []
            }]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response, status_code = SearchSalesOrder.search_saleorder(self.config, self.params)
        
        # Validate response
        self.assertEqual(status_code, 200)
        self.assertEqual(response["count"], 1)
        self.assertEqual(len(response["results"]), 1)
        self.assertEqual(response["results"][0]["id"], "123")

        # Verify the request was made with correct parameters
        expected_url = f"{self.config.get_endpoint(SearchSalesOrder.endpoint)}?$filter={self.params.filter}&top={self.params.top}&skip={self.params.skip}"
        mock_get.assert_called_once_with(
            expected_url,
            headers=self.config.headers
        )

    @patch('requests.get')
    def test_search_saleorder_error(self, mock_get):
        # Mock error response
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        response, status_code = SearchSalesOrder.search_saleorder(self.config, self.params)
        
        # Validate error response
        self.assertEqual(status_code, 400)
        self.assertEqual(response["error"], "Invalid request")


class TestSearchProduct(unittest.TestCase):
    def setUp(self):
        self.config = ConfigProducteca(
            token="test_client_id",
            api_key="test_client_secret",
        )
        self.params = SearchProductParams(
            top=10,
            skip=0,
            filter="status eq 'active'",
            search="test product",
            sales_channel="2"
        )

    @patch('requests.get')
    def test_search_product_success(self, mock_get):
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 1,
            "facets": [{
                "key": "brand",
                "value": [{
                    "count": 1,
                    "value": "test_brand",
                    "label": "Test Brand"
                }],
                "is_collection": False,
                "translate": True
            }],
            "results": [{
                "@search.score": 1.0,
                "id": 123,
                "product_id": 456,
                "company_id": 789,
                "name": "Test Product",
                "code": "TEST-001",
                "skus": ["SKU001"],
                "brand": "Test Brand",
                "category": "Test Category",
                "thumbnail": "http://test.com/image.jpg",
                "stocks": [{
                    "warehouse": "Main",
                    "quantity": 10,
                    "reserved": 0
                }],
                "warehouses_with_stock": ["Main"],
                "total_stock": 10,
                "has_pictures": True,
                "buying_price": 100.0,
                "prices": [{
                    "price_list_id": 1,
                    "price_list": "Default",
                    "amount": 200.0,
                    "currency": "USD"
                }],
                "integration_ids": ["INT001"],
                "integration_apps": ["APP1"],
                "integrations": [],
                "campaigns": [],
                "app": None,
                "status": None,
                "synchronize_stock": None,
                "listing_type": None,
                "price_amount": None,
                "price_currency": None,
                "category_id": None,
                "category_base_id": None,
                "category_l1": None,
                "category_l2": None,
                "category_l3": None,
                "category_l4": None,
                "category_l5": None,
                "category_l6": None,
                "has_category": None,
                "category_fixed": None,
                "accepts_mercadoenvios": None,
                "shipping_mode": None,
                "local_pickup": None,
                "mandatory_free_shipping": None,
                "free_shipping": None,
                "free_shipping_cost": None,
                "template": None,
                "youtube_id": None,
                "warranty": None,
                "permalink": None,
                "domain": None,
                "attribute_completion_status": None,
                "attribute_completion_count": None,
                "attribute_completion_total": None,
                "deals": None,
                "campaign_status": None,
                "size_chart": None,
                "channel_status": None,
                "channel_category_l1": None,
                "channel_category_l2": None,
                "channel_category_l3": None,
                "channel_category_id": None,
                "channel_synchronizes_stock": None,
                "channel_has_category": None,
                "catalog_products_status": None,
                "metadata": None,
                "integration_tags": None,
                "variations_integration_ids": None,
                "channel_pictures_templates": None,
                "channel_pictures_templates_apps": None
            }]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = SearchProduct.search_product(self.config, self.params)
        
        # Validate response
        self.assertEqual(response.count, 1)
        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].id, 123)
        self.assertEqual(response.results[0].name, "Test Product")
        
        

    @patch('requests.get')
    def test_search_product_error(self, mock_get):
        # Mock error response
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        # TODO: Fix this
        # with self.assertRaises(Exception):
        #     SearchProduct.search_product(self.config, self.params)


if __name__ == '__main__':
    unittest.main()

