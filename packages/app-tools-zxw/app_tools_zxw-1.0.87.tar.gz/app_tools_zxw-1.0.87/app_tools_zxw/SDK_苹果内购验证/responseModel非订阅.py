from pydantic import BaseModel
from typing import List


# 非订阅 - 成功响应结构
class _receipt_in_app_item(BaseModel):
    is_trial_period: str = 'false'
    original_purchase_date_ms: str = '1562908866000'
    quantity: str = '1'
    purchase_date_ms: str = '1562908866000'
    purchase_date_pst: str = '2019-07-11 22:21:06 America/Los_Angeles'
    product_id: str = 'xxxxxx'
    original_purchase_date: str = '2019-07-12 05:21:06 Etc/GMT'
    transaction_id: str = '100000xxxxx826'
    original_transaction_id: str = '10000005xxxx826'
    original_purchase_date_pst: str = '2019-07-11 22:21:06 America/Los_Angeles'
    purchase_date: str = '2019-07-12 05:21:06 Etc/GMT'


class _receipt(BaseModel):
    receipt_creation_date_ms: str = '1562909318000'
    adam_id: str = 0
    receipt_creation_date: str = '2019-07-12 05:28:38 Etc/GMT'
    version_external_identifier: str = 0
    original_purchase_date_pst: str = '2013-08-01 00:00:00  America/Los_Angeles'
    original_purchase_date_ms: str = '1375340400000'
    bundle_id: str = 'xxxxxxx'
    receipt_creation_date_pst: str = '2019-07-11 22:28:38 America/Los_Angeles'
    request_datea_ms: str = '1562909325495'
    app_item_id: int = 0
    original_purchase_date: str = '2013-08-01 07:00:00 Etc/GMT'
    request_date_pst: str = '2019-07-11 22:28:45 America/Los_Angeles'
    original_application_version: str = '1.0'
    application_version: str = '1'
    receipt_type: str = 'ProductionSandbox'
    download_id: int = 0
    request_date: str = '2019-07-12 05:28:45 Etc/GMT'
    """
    收据在 receipt 中的 in_app 字段里，这是数组包对象的形式，里面的每一个对象都是一次交易
    先获取 in_app 这个字段中的数据
    遍历其中的每一个对象，将其中的 transaction_id 与 iOS 端传来的 transactionId 进行匹配,匹配成功的话，就说明这单交易是存在的，
    但是为了进一步校验交易的准确性，我们再将 product_id 与 iOS 端传来的 productId 做比较，如果相等则校验成功，若不相等，则有可能是伪造的虚假数据。
    还有值得注意的一个字段是 original_transaction_id ，这个字段是自动订阅式购买时，当前用户在你的App内首次购买的交易单号，可以利用这个字段在某些情况下进行用户关联。
    而在本例中可以看到，在 in_app 的两个对象中，original_transaction_id 是不一样的，因为本次操作的是非自动订阅式购买。
    """
    in_app: List[_receipt_in_app_item]


class response_data(BaseModel):
    receipt: _receipt
    status: int = 0
    environment: str = "Sandbox"
