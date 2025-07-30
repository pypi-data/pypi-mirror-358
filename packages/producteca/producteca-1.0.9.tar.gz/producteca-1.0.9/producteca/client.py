from producteca.config.config import ConfigProducteca
from producteca.products.products import Product
from producteca.sales_orders.sales_orders import SalesOrder
from producteca.search.search import Search
from producteca.shipments.shipment import Shipment
from producteca.payments.payments import Payment
import os


class ProductecaClient:

    def __init__(self, token: str = os.environ['PRODUCTECA_TOKEN'], api_key: str = os.environ['PRODUCTECA_API_KEY']):
        if not token:
            raise ValueError('PRODUCTECA_TOKEN environment variable not set')
        if not api_key:
            raise ValueError('PRODUCTECA_API_KEY environment variable not set')
        self.config = ConfigProducteca(token=token, api_key=api_key)
        
    @property
    def Product(self):
        return lambda *args: Product(config=self.config, *args)

    @property 
    def SalesOrder(self):
        return lambda *args: SalesOrder(config=self.config, *args)

    @property
    def Search(self):
        return lambda *args: Search(config=self.config, *args)

    @property
    def Shipment(self):
        return lambda *args: Shipment(config=self.config, *args)

    @property
    def Payment(self):
        return lambda *args: Payment(config=self.config, *args)
