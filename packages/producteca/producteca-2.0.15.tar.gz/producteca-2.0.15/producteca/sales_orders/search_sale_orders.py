from typing import List, Optional
from pydantic import BaseModel, Field
import logging

_logger = logging.getLogger(__name__)


class SalesOrderProduct(BaseModel):
    id: int
    name: str
    code: str
    brand: str


class SalesOrderVariationAttribute(BaseModel):
    key: str
    value: str


class SalesOrderVariation(BaseModel):
    id: int
    attributes: List[SalesOrderVariationAttribute]
    sku: str
    thumbnail: str


class SalesOrderLine(BaseModel):
    product: SalesOrderProduct
    variation: SalesOrderVariation
    quantity: int
    price: float


class SalesOrderCard(BaseModel):
    payment_network: str = Field(alias="paymentNetwork")
    first_six_digits: int = Field(alias="firstSixDigits")
    last_four_digits: int = Field(alias="lastFourDigits")
    cardholder_identification_number: str = Field(alias="cardholderIdentificationNumber")
    cardholder_identification_type: str = Field(alias="cardholderIdentificationType")
    cardholder_name: str = Field(alias="cardholderName")


class SalesOrderPaymentIntegration(BaseModel):
    integration_id: str = Field(alias="integrationId")
    app: int


class SalesOrderPayment(BaseModel):
    date: str
    amount: float
    coupon_amount: float = Field(alias="couponAmount")
    status: str
    method: str
    integration: SalesOrderPaymentIntegration
    transaction_fee: float = Field(alias="transactionFee")
    installments: int
    card: SalesOrderCard
    notes: str
    has_cancelable_status: bool = Field(alias="hasCancelableStatus")
    id: int


class SalesOrderIntegration(BaseModel):
    alternate_id: str = Field(alias="alternateId")
    integration_id: int = Field(alias="integrationId")
    app: int


class SalesOrderShipmentProduct(BaseModel):
    product: int
    variation: int
    quantity: int


class SalesOrderShipmentMethod(BaseModel):
    tracking_number: str = Field(alias="trackingNumber")
    tracking_url: str = Field(alias="trackingUrl")
    courier: str
    mode: str
    cost: float
    type: str
    eta: str
    status: str


class SalesOrderShipmentIntegration(BaseModel):
    id: int
    integration_id: str = Field(alias="integrationId")
    app: int
    status: str


class SalesOrderShipment(BaseModel):
    date: str
    products: List[SalesOrderShipmentProduct]
    method: SalesOrderShipmentMethod
    integration: SalesOrderShipmentIntegration


class SalesOrderResultItem(BaseModel):
    codes: List[str]
    contact_id: int = Field(alias="contactId")
    currency: str
    date: str
    delivery_method: str = Field(alias="deliveryMethod")
    delivery_status: str = Field(alias="deliveryStatus")
    id: str
    integration_ids: List[str] = Field(alias="integrationIds")
    integrations: List[SalesOrderIntegration]
    invoice_integration_app: int = Field(alias="invoiceIntegrationApp")
    invoice_integration_id: str = Field(alias="invoiceIntegrationId")
    lines: List[SalesOrderLine]
    payments: List[SalesOrderPayment]
    payment_status: str = Field(alias="paymentStatus")
    payment_term: str = Field(alias="paymentTerm")
    product_names: List[str] = Field(alias="productNames")
    reserving_product_ids: str = Field(alias="reservingProductIds")
    sales_channel: int = Field(alias="salesChannel")
    shipments: List[SalesOrderShipment]
    tracking_number: str = Field(alias="trackingNumber")
    skus: List[str]
    status: str
    tags: List[str]
    warehouse: str
    company_id: int = Field(alias="companyId")
    shipping_cost: float = Field(alias="shippingCost")
    contact_phone: str = Field(alias="contactPhone")
    brands: List[str]
    courier: str
    order_id: int = Field(alias="orderId")
    updated_at: str = Field(alias="updatedAt")
    invoice_integration_created_at: str = Field(alias="invoiceIntegrationCreatedAt")
    invoice_integration_document_url: str = Field(alias="invoiceIntegrationDocumentUrl")
    has_document_url: bool = Field(alias="hasDocumentUrl")
    integration_alternate_ids: str = Field(alias="integrationAlternateIds")
    cart_id: str = Field(alias="cartId")
    amount: float
    has_any_shipments: bool = Field(alias="hasAnyShipments")


class SearchSalesOrder(BaseModel):
    count: int
    results: List[SalesOrderResultItem]


class SearchSalesOrderParams(BaseModel):
    top: Optional[int]
    skip: Optional[int]
    filter: Optional[str] = Field(default=None, alias="$filter")

    class Config:
        validate_by_name = True
