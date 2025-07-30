from dg_sdk.core.request_tools import request_post
from dg_sdk.request.request_api_urls import V2_HYC_INVOICE_APPLY



class V2HycInvoiceApplyRequest(object):
    """
    申请开票
    """

    # 请求流水号
    req_seq_id = ""
    # 请求日期
    req_date = ""
    # 商户汇付id
    huifu_id = ""
    # 交易流水列表
    batch_list = ""
    # 接收人手机号
    receive_mobile = ""
    # 接收人姓名
    receive_name = ""
    # 快递地址
    courier_address = ""
    # 开票类目
    invoice_category = ""

    def post(self, extend_infos):
        """
        申请开票

        :param extend_infos: 扩展字段字典
        :return:
        """

        required_params = {
            "req_seq_id":self.req_seq_id,
            "req_date":self.req_date,
            "huifu_id":self.huifu_id,
            "batch_list":self.batch_list,
            "receive_mobile":self.receive_mobile,
            "receive_name":self.receive_name,
            "courier_address":self.courier_address,
            "invoice_category":self.invoice_category
        }
        required_params.update(extend_infos)
        return request_post(V2_HYC_INVOICE_APPLY, required_params)
