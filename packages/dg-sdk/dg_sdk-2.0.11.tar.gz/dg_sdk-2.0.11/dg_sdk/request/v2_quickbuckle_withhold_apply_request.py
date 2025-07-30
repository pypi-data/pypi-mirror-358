from dg_sdk.core.request_tools import request_post
from dg_sdk.request.request_api_urls import V2_QUICKBUCKLE_WITHHOLD_APPLY



class V2QuickbuckleWithholdApplyRequest(object):
    """
    代扣绑卡申请
    """

    # 请求流水号
    req_seq_id = ""
    # 请求时间
    req_date = ""
    # 汇付Id
    huifu_id = ""
    # 返回地址
    return_url = ""
    # 用户id
    out_cust_id = ""
    # 绑卡订单号
    order_id = ""
    # 绑卡订单日期
    order_date = ""
    # 银行卡号
    card_id = ""
    # 银行卡开户姓名 
    card_name = ""
    # 银行卡绑定证件类型 
    cert_type = ""
    # 银行卡绑定身份证
    cert_id = ""
    # 银行卡绑定手机号 
    card_mp = ""
    # CVV2信用卡代扣专用 需要密文传输，需要密文传输，使用汇付RSA公钥加密(加密前64位，加密后最长2048位），参见[参考文档](https://paas.huifu.com/open/doc/guide/#/api_jiami_jiemi)；
    vip_code = ""
    # 卡有效期 信用卡代扣专用，格式：MMYY 需要密文传输，使用汇付RSA公钥加密(加密前64位，加密后最长2048位），参见[参考文档](https://paas.huifu.com/open/doc/guide/#/api_jiami_jiemi)；
    expiration = ""
    # 个人证件有效期类型
    cert_validity_type = ""
    # 个人证件有效期起始日
    cert_begin_date = ""
    # 个人证件有效期到期日长期有效不填.格式：YYYYMMDD；&lt;font color&#x3D;&quot;green&quot;&gt;示例值：20450112&lt;/font&gt;
    cert_end_date = ""
    # 卡的借贷类型
    dc_type = ""

    def post(self, extend_infos):
        """
        代扣绑卡申请

        :param extend_infos: 扩展字段字典
        :return:
        """

        required_params = {
            "req_seq_id":self.req_seq_id,
            "req_date":self.req_date,
            "huifu_id":self.huifu_id,
            "return_url":self.return_url,
            "out_cust_id":self.out_cust_id,
            "order_id":self.order_id,
            "order_date":self.order_date,
            "card_id":self.card_id,
            "card_name":self.card_name,
            "cert_type":self.cert_type,
            "cert_id":self.cert_id,
            "card_mp":self.card_mp,
            "vip_code":self.vip_code,
            "expiration":self.expiration,
            "cert_validity_type":self.cert_validity_type,
            "cert_begin_date":self.cert_begin_date,
            "cert_end_date":self.cert_end_date,
            "dc_type":self.dc_type
        }
        required_params.update(extend_infos)
        return request_post(V2_QUICKBUCKLE_WITHHOLD_APPLY, required_params)
