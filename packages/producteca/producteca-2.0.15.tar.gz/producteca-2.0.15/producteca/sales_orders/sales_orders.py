from pydantic import BaseModel, Field
from typing import List, Optional
import requests
from producteca.abstract.abstract_dataclass import BaseService
from producteca.sales_orders.search_sale_orders import SearchSalesOrderParams, SearchSalesOrder
from producteca.payments.payments import Payment
from producteca.shipments.shipment import Shipment
from dataclasses import dataclass
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLocation(BaseModel):
    streetName: Optional[str] = None
    streetNumber: Optional[str] = None
    addressNotes: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    zipCode: Optional[str] = None


class SaleOrderBillingInfo(BaseModel):
    docType: Optional[str] = None
    docNumber: Optional[str] = None
    streetName: Optional[str] = None
    streetNumber: Optional[str] = None
    comment: Optional[str] = None
    zipCode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    stateRegistration: Optional[str] = None
    taxPayerType: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    businessName: Optional[str] = None


class SaleOrderProfile(BaseModel):
    app: int
    integrationId: str
    nickname: Optional[str] = None


class SaleOrderContact(BaseModel):
    id: int
    name: str
    contactPerson: Optional[str] = None
    mail: Optional[str] = None
    phoneNumber: Optional[str] = None
    taxId: Optional[str] = None
    location: Optional[SaleOrderLocation] = None
    notes: Optional[str] = None
    type: Optional[str] = None
    priceList: Optional[str] = None
    priceListId: Optional[str] = None
    profile: Optional[SaleOrderProfile] = None
    billingInfo: Optional[SaleOrderBillingInfo] = None


class SaleOrderIntegrationId(BaseModel):
    alternateId: Optional[str] = None
    integrationId: str
    app: int


class SaleOrderVariationPicture(BaseModel):
    url: str
    id: Optional[int] = None


class SaleOrderVariationStock(BaseModel):
    warehouseId: Optional[int] = None
    warehouse: str
    quantity: int
    reserved: int
    lastModified: Optional[str] = None
    available: int


class SaleOrderVariationAttribute(BaseModel):
    key: str
    value: str


class SaleOrderVariation(BaseModel):
    supplierCode: Optional[str] = None
    pictures: Optional[List[SaleOrderVariationPicture]] = None
    stocks: Optional[List[SaleOrderVariationStock]] = None
    integrationId: Optional[int] = None
    attributesHash: Optional[str] = None
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None
    size: Optional[str] = None
    thumbnail: Optional[str] = None
    attributes: Optional[List[SaleOrderVariationAttribute]] = None
    integrations: Optional[List[SaleOrderIntegrationId]] = None
    id: int
    sku: str
    barcode: Optional[str] = None


class SaleOrderProduct(BaseModel):
    name: str
    code: str
    brand: Optional[str] = None
    id: int


class SaleOrderConversation(BaseModel):
    questions: Optional[List[str]] = None


class SaleOrderLine(BaseModel):
    price: float
    originalPrice: Optional[float] = None
    transactionFee: Optional[float] = None
    product: SaleOrderProduct
    variation: SaleOrderVariation
    orderVariationIntegrationId: Optional[str] = None
    quantity: int
    conversation: Optional[SaleOrderConversation] = None
    reserved: Optional[int] = None
    id: int


class SaleOrderCard(BaseModel):
    paymentNetwork: Optional[str] = None
    firstSixDigits: Optional[int] = None
    lastFourDigits: Optional[int] = None
    cardholderIdentificationNumber: Optional[str] = None
    cardholderIdentificationType: Optional[str] = None
    cardholderName: Optional[str] = None


class SaleOrderPaymentIntegration(BaseModel):
    integrationId: str
    app: int


class SaleOrderPayment(BaseModel):
    date: Optional[str] = None
    amount: float
    couponAmount: Optional[float] = None
    status: Optional[str] = None
    method: Optional[str] = None
    integration: Optional[SaleOrderPaymentIntegration] = None
    transactionFee: Optional[float] = None
    installments: Optional[int] = None
    card: Optional[SaleOrderCard] = None
    notes: Optional[str] = None
    authorizationCode: Optional[str] = None
    hasCancelableStatus: Optional[bool] = None
    id: Optional[int] = None


class SaleOrderShipmentMethod(BaseModel):
    trackingNumber: Optional[str] = None
    trackingUrl: Optional[str] = None
    courier: Optional[str] = None
    mode: Optional[str] = None
    cost: Optional[float] = None
    type: Optional[str] = None
    eta: Optional[int] = None
    status: Optional[str] = None


class SaleOrderShipmentProduct(BaseModel):
    product: int
    variation: int
    quantity: int


class SaleOrderShipmentIntegration(BaseModel):
    app: int
    integrationId: str
    status: str
    id: int


class SaleOrderShipment(BaseModel):
    date: str
    products: List[SaleOrderShipmentProduct]
    method: Optional[SaleOrderShipmentMethod] = None
    integration: Optional[SaleOrderShipmentIntegration] = None
    receiver: Optional[dict] = None
    id: int


class SaleOrderInvoiceIntegration(BaseModel):
    id: Optional[int] = None
    integrationId: Optional[str] = None
    app: Optional[int] = None
    createdAt: Optional[str] = None
    documentUrl: Optional[str] = None
    xmlUrl: Optional[str] = None
    decreaseStock: Optional[bool] = None


class SaleOrder(BaseModel):
    tags: Optional[List[str]] = None
    integrations: Optional[List[SaleOrderIntegrationId]] = None
    invoiceIntegration: Optional[SaleOrderInvoiceIntegration] = None
    channel: Optional[str] = None
    piiExpired: Optional[bool] = None
    contact: Optional[SaleOrderContact] = None
    lines: Optional[List[SaleOrderLine]] = None
    warehouse: Optional[str] = None
    warehouseId: Optional[int] = None
    warehouseIntegration: Optional[str] = None
    pickUpStore: Optional[str] = None
    payments: Optional[List[SaleOrderPayment]] = None
    shipments: Optional[List[SaleOrderShipment]] = None
    amount: Optional[float] = None
    shippingCost: Optional[float] = None
    financialCost: Optional[float] = None
    paidApproved: Optional[float] = None
    paymentStatus: Optional[str] = None
    deliveryStatus: Optional[str] = None
    paymentFulfillmentStatus: Optional[str] = None
    deliveryFulfillmentStatus: Optional[str] = None
    deliveryMethod: Optional[str] = None
    paymentTerm: Optional[str] = None
    currency: Optional[str] = None
    customId: Optional[str] = None
    isOpen: Optional[bool] = None
    isCanceled: Optional[bool] = None
    cartId: Optional[str] = None
    draft: Optional[bool] = None
    promiseDeliveryDate: Optional[str] = None
    promiseDispatchDate: Optional[str] = None
    hasAnyShipments: Optional[bool] = None
    hasAnyPayments: Optional[bool] = None
    date: Optional[str] = None
    notes: Optional[str] = None
    id: int


@dataclass
class SaleOrderService(BaseService[SaleOrder]):
    endpoint: str = Field(default='salesorders', exclude=True)

    def __call__(self, **payload):
        self._record = SaleOrder(**payload)
        return self

    def get(self, sale_order_id: int) -> "SaleOrder":
        endpoint = f'{self.endpoint}/{sale_order_id}'
        url = self.config.get_endpoint(endpoint)
        response = requests.get(url, headers=self.config.headers)
        if not response.ok:
            raise Exception("Order could not be fetched")
        return SaleOrder(**response.json())

    def get_shipping_labels(self):
        if not self._record:
            raise Exception("You need to add a record id")
        endpoint = f'{self.endpoint}/{self._record.id}/labels'
        url = self.config.get_endpoint(endpoint)
        response = requests.get(url, headers=self.config.headers)
        if not response.ok:
            raise Exception("labels could not be gotten")
        return response.json()

    def close(self):
        if not self._record:
            raise Exception("You need to add a record id")
        endpoint = f'{self.endpoint}/{self._record.id}/close'
        url = self.config.get_endpoint(endpoint)
        response = requests.post(url, headers=self.config.headers)
        if not response.ok:
            raise Exception("Order could not be closed")

    def cancel(self):
        if not self._record:
            raise Exception("You need to add a record id")
        endpoint = f'{self.endpoint}/{self._record.id}/cancel'
        url = self.config.get_endpoint(endpoint)
        response = requests.post(url, headers=self.config.headers)
        if not response.ok:
            raise Exception("Order could not be closed")

    def synchronize(self, payload: "SaleOrder") -> "SaleOrder":
        endpoint = f'{self.endpoint}/synchronize'
        url = self.config.get_endpoint(endpoint)
        response = requests.post(url, data=payload.model_dump_json(exclude_none=True), headers=self.config.headers)
        if not response.ok:
            raise Exception(f"Synchronize error {response.text}")
        return SaleOrder(**response.json())

    def invoice_integration(self):
        if not self._record:
            raise Exception("You need to add a record id")
        endpoint = f'{self.endpoint}/{self._record.id}/invoiceIntegration'
        url = self.config.get_endpoint(endpoint)
        response = requests.put(url, headers=self.config.headers, data=self._record.model_dump_json(exclude_none=True))
        if not response.ok:
            raise Exception(f"Error on resposne {response.text}")
        return SaleOrder(**response.json())

    def search(self, params: SearchSalesOrderParams):
        endpoint: str = f"search/{self.endpoint}"
        headers = self.config.headers
        url = self.config.get_endpoint(endpoint)
        new_url = f"{url}?$filter={params.filter}&top={params.top}&skip={params.skip}"
        response = requests.get(
            new_url,
            headers=headers,
        )
        if not response.ok:
            raise Exception(f"Error on resposne {response.text}")
        return SearchSalesOrder(**response.json())

    def add_payment(self, payload: "Payment") -> "Payment":
        if not self._record:
            raise Exception("You need to add a record id")
        url = self.config.get_endpoint(f"{self.endpoint}/{self._record.id}/payments")
        res = requests.post(url, data=payload.model_dump_json(exclude_none=True), headers=self.config.headers)
        if not res.ok:
            raise Exception(f"Error on resposne {res.text}")
        return Payment(**res.json())

    def update_payment(self, payment_id: int, payload: "Payment") -> "Payment":
        if not self._record:
            raise Exception("You need to add a record id")
        url = self.config.get_endpoint(f"{self.endpoint}/{self._record.id}/payments/{payment_id}")
        res = requests.put(url, data=payload.model_dump_json(exclude_none=True), headers=self.config.headers)
        if not res.ok:
            raise Exception(f"Error on payment update {res.text}")
        return Payment(**res.json())

    def add_shipment(self, payload: "Shipment") -> "Shipment":
        if not self._record:
            raise Exception("You need to add a record id")
        url = self.config.get_endpoint(f"{self.endpoint}/{self._record.id}/shipments")
        res = requests.post(url, data=payload.model_dump_json(exclude_none=True), headers=self.config.headers)
        if not res.ok:
            raise Exception(f"Error on shipment add {res.text}")
        return Shipment(**res.json())

    def update_shipment(self, shipment_id: str, payload: "Shipment") -> "Shipment":
        if not self._record:
            raise Exception("You need to add a record id")
        url = self.config.get_endpoint(f"{self.endpoint}/{self._record.id}/shipments/{shipment_id}")
        res = requests.put(url, data=payload.model_dump_json(exclude_none=True), headers=self.config.headers)
        if not res.ok:
            raise Exception(f"Error on shipment update {res.text}")
        return Shipment(**res.json())
