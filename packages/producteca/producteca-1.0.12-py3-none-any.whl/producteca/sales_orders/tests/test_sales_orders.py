import unittest
from unittest.mock import patch, Mock
from producteca.config.config import ConfigProducteca
from producteca.sales_orders.sales_orders import SaleOrder, SaleOrderInvoiceIntegration


class TestSaleOrder(unittest.TestCase):
    def setUp(self):
        self.config = ConfigProducteca(token="test_client", api_key="test_secret")
        self.sale_order_id = 123
        self.mock_response = {
            "id": self.sale_order_id,
            "contact": {"id": 1, "name": "Test Contact"},
            "lines": []
        }

    @patch('requests.get')
    def test_get_sale_order(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: self.mock_response
        )

        sale_order = SaleOrder.get(self.config, self.sale_order_id)
        self.assertEqual(sale_order.id, self.sale_order_id)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_get_shipping_labels(self, mock_get):
        mock_labels = ["label1", "label2"]
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: mock_labels
        )

        labels = SaleOrder.get_shipping_labels(self.config, self.sale_order_id)
        self.assertEqual(labels, mock_labels)
        mock_get.assert_called_once()

    @patch('requests.post')
    def test_close_sale_order(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"status": "closed"}
        )

        status_code, response = SaleOrder.close(self.config, self.sale_order_id)
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"status": "closed"})
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_cancel_sale_order(self, mock_post):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"status": "cancelled"}
        )

        status_code, response = SaleOrder.cancel(self.config, self.sale_order_id)
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"status": "cancelled"})
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_synchronize_sale_order(self, mock_post):
        sale_order = SaleOrder(**self.mock_response)
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: self.mock_response
        )

        status_code, response = SaleOrder.synchronize(self.config, sale_order)
        self.assertEqual(status_code, 200)
        self.assertEqual(response.id, self.sale_order_id)
        mock_post.assert_called_once()

    @patch('requests.put')
    def test_invoice_integration(self, mock_put):
        invoice_data = {
            "id": 1,
            "integrationId": "test123",
            "app": 1
        }
        invoice_integration = SaleOrderInvoiceIntegration(**invoice_data)
        sale_order = SaleOrder(id=self.sale_order_id, invoiceIntegration=invoice_integration)

        mock_put.return_value = Mock(
            status_code=200,
            json=lambda: {}
        )

        status_code, response = SaleOrder.invoice_integration(self.config, self.sale_order_id, sale_order)
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {})
        mock_put.assert_called_once()

if __name__ == '__main__':
    unittest.main()
