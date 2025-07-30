import unittest
from unittest.mock import patch, MagicMock
from producteca.shipments.shipment import Shipment, ShipmentProduct, ShipmentMethod, ShipmentIntegration, ConfigProducteca


class TestShipment(unittest.TestCase):

    @patch('requests.post')
    def test_create_shipment(self, mock_post):
        # Arrange
        config = ConfigProducteca(token="test_token", api_key="as")
        sale_order_id = 123
        products = [ShipmentProduct(product=1, variation=2, quantity=3)]
        method = ShipmentMethod(trackingNumber="TN123", trackingUrl="http://track.url", courier="DHL", mode="air", cost=10.5, type="express", eta=5, status="shipped")
        integration = ShipmentIntegration(id=1, integrationId="int123", app=10, status="active")
        payload = Shipment(date="2023-01-01", products=products, method=method, integration=integration)

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        # Act
        status_code, response_json = Shipment.create(config, sale_order_id, payload)

        # Assert
        self.assertEqual(status_code, 201)
        self.assertEqual(response_json, {'success': True})
        mock_post.assert_called_once()

    @patch('requests.put')
    def test_update_shipment(self, mock_put):
        # Arrange
        config = ConfigProducteca(token="test_token", api_key="as")
        sale_order_id = 123
        shipment_id = 'abc'
        products = [ShipmentProduct(product=4, quantity=7)]
        method = ShipmentMethod(courier="FedEx", cost=15.0)
        integration = ShipmentIntegration(status="pending")
        payload = Shipment(date="2023-02-02", products=products, method=method, integration=integration)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'updated': True}
        mock_put.return_value = mock_response

        # Act
        status_code, response_json = Shipment.update(config, sale_order_id, shipment_id, payload)

        # Assert
        self.assertEqual(status_code, 200)
        self.assertEqual(response_json, {'updated': True})
        mock_put.assert_called_once()


if __name__ == '__main__':
    unittest.main()