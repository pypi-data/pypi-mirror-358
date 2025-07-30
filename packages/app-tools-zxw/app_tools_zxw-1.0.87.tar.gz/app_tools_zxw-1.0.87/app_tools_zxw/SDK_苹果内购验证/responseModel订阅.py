from pydantic import BaseModel
from typing import List


class _receipt_in_app(BaseModel):
    quantity: str  # = '1'
    product_id: str  # = '...'
    transaction_id: str  # = '1000000567124099'
    original_transaction_id: str  # = '1000000567124099'
    purchase_date: str  # = '2019-09-11 10:06:34 Etc/GMT'
    purchase_date_ms: str  # = '1568196394000'
    purchase_date_pst: str  # = '2019-09-11 03:06:34 America/Los_Angeles'
    original_purchase_date: str  # = '2019-09-11 10:06:35 Etc/GMT'
    original_purchase_date_ms: str  # = '1568196395000'
    original_purchase_date_pst: str  # = '2019-09-11 03:06:35 America/Los_Angeles'
    expires_date: str  # = '2019-09-11 11:06:34 Etc/GMT'
    expires_date_ms: int  # = '1568199994000'
    expires_date_pst: str  # = '2019-09-11 04:06:34 America/Los_Angeles'
    web_order_line_item_id: str  # = '1000000046836911'
    is_trial_period: str  # = 'false'
    is_in_intro_offer_period: str  # = 'false'


class _receipt(BaseModel):
    receipt_type: str  # = 'ProductionSandbox'
    adam_id: int  # = 0
    app_item_id: int  # = 0
    bundle_id: str  # = '...'
    application_version: str  # = '1'
    download_id: int  # = 0
    version_external_identifier: int  # = 0
    receipt_creation_date: str  # = '2019-09-11 10:12:57 Etc/GMT'
    receipt_creation_date_ms: str  # = '1568196777000'
    receipt_creation_date_pst: str  # = '2019-09-11 03:12:57 America/Los_Angeles'
    request_date: str  # = '2019-09-11 11:38:36 Etc/GMT'
    request_date_ms: str  # = '1568201916879'
    request_date_pst: str  # = '2019-09-11 04:38:36 America/Los_Angeles'
    original_purchase_date: str  # = '2013-08-01 07:00:00 Etc/GMT'
    original_purchase_date_ms: str  # = '1375340400000'
    original_purchase_date_pst: str  # = '2013-08-01 00:00:00 America/Los_Angeles'
    original_application_version: str  # = '1.0'
    in_app: List[_receipt_in_app]


class _latest_receipt_info(BaseModel):
    quantity: str  # = '1'
    product_id: str  # = '...'
    transaction_id: str  # = '1000000567124099'
    original_transaction_id: str  # = '1000000567124099'
    purchase_date: str  # = '2019-09-11 10:06:34 Etc/GMT'
    purchase_date_ms: int  # = '1568196394000'
    purchase_date_pst: str  # = '2019-09-11 03:06:34 America/Los_Angeles'
    original_purchase_date: str  # = '2019-09-11 10:06:35 Etc/GMT'
    original_purchase_date_ms: str  # = '1568196395000'
    original_purchase_date_pst: str  # = '2019-09-11 03:06:35 America/Los_Angeles'
    expires_date: str  # = '2019-09-11 11:06:34 Etc/GMT'
    expires_date_ms: int  # = '1568199994000'
    expires_date_pst: str  # = '2019-09-11 04:06:34 America/Los_Angeles'
    web_order_line_item_id: str  # = '1000000046836911'
    is_trial_period: str  # = 'false'
    is_in_intro_offer_period: str  # = 'false'


class _pending_renewal_info(BaseModel):
    auto_renew_product_id: str  # = '...'
    original_transaction_id: str  # = '1000000567124099'
    product_id: str  # = '...'
    auto_renew_status: str  # = '1'


class response_data(BaseModel):
    status: int
    environment: str
    receipt: _receipt
    latest_receipt_info: List[_latest_receipt_info]
    latest_receipt: str
    pending_renewal_info: List[_pending_renewal_info]
