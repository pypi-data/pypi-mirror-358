DG Python SDK
===================================

 dougong sdk 工具类

安装
-----
远程下载并安装：

`pip install dg-sdk`


简介
------

为了提高客户接入的便捷性，本系统提供 SDK 方式介入，使用本 SDK 将极大的简化开发者的工作，开发者将无需考虑通信、签名、验签等，只需要关注业务参数的输入。



使用方法
--------

* 初始化SDK

未入网前，可使用以下测试商户参数进行开发测试

.. code:: Python

    import dg_sdk

    huifu_id = "6666000108854952"
    sys_id = "6666000108854952"
    product_id = "YYZY"
    private_key= "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCxtfk3rjwdpBV81WBy5jIMcDLFdvHckhjGXkmWfaBn7euPRyetEhS4inpr7EvQ5KDUXNBPljI2NVhG/LEGZKvau1MW8j3t7dJ3gWafuVGsCiLJHU79sIRHf11nKOTykX5WxB/7MMwRnZsECuaZyCk7WPuSAlznqbDJdrZTzHhjQzMhjto1qD6+vc0OxyaBFlOY9piBtEfecsvD+6GfQ8exFqwzblJm9iZPYw02DaeUDLFO9Umn7i7gShlj/1Hh8nEM7YitpF/p26o+MC9LHWbIjgzjvNVhSRVmbvWys+3S11Zm/vux6Yzfk0H3fqrksAKSEkLEtEoYKS4wKjHdecztAgMBAAECggEACy1g4WmqCks5tsJM8K0d1L5x0w2qJK9js4ZWpop8Pk0ulbJqAm6ysvCyxnr0Qc0/eFvmFjtiKRqt1LksATTvwjAqB7Vww7hDlpSi+cTUKDfy/CdFwpsJlt2h6E0gKUmRYq+vO0NUcn8xMs3ktyNpxHvSRtqzMTbxEZrP2PFxWPzUKGNyk53FTlJ64YCoGQqWeGhA5LO6QLPHlAxIrvRf9B5dtXQr5XZXVqS9MwjtsRPvQPWiFXxlzvhJRcL/wXehcNextHzpMMgX/idB3HIpIl6XXLKiFUR4rBDJIMiQjQvS6zz2l1zpiJ0vWujVa3IY+PNefRA2ttg1DeC19GYa2QKBgQDh7AkJ7wut7p4qYAdcFEDVhFgP5mnSRyOBGWmClHYE4RIFplPiv4yO0fttAjFuCg4Zaxq49BuV3zshWOEIr72VK6wMa6Z+QbfXNr/1DT6nW+ktgXTw2G9Ts/nZiMrpcsbl7qvwChfJAPvEwnyP7Ckmd9t2WbQisuYZc+Vu8znO7wKBgQDJXskTiExEipQSOcVH5cX/ExVyj9MoLjmJhy3WTTDzGafgEoOPOfej2ZCgF6gCwugXJr+rtgdOpASk8WPACaCePdjdgQ2NVhSfV3op3TtvhgAPf3iI/zCVkZM4I1iZs6KjdHstLCKyAzCFBsowkPbfZBlFX4eO7Bk6XcIZ6x2h4wKBgQDcH64C5s4bb2beZOhm2Dj/kU54V4l93+CBFjCOkXaYdG+p35DWWspqEcCHSt68l8F7FLdZxEbodTPY3w+L9iejI4UkKPN1CzVD1U2dR4VnbY85zmwRiuCVzsM/KCCE61dOi4ktfbgFGhc1dEYHuROzLo8/tlFkiajW3eyLeSM3MwKBgATL3iw57d8gEeDRQXKx9WJa+QLOjDAD0dkFwEC/e+/+Z3I93qZVsiFT+E7n4VeXfuG2SZB0eH4WCApJuZ+EWzAJtxWnkkQQjdMxyTYgD99bKLs1xRA2S9j0K7aFmQGoNrJ//sMXrwfgbZJtk/lOKqMthjCR0u/DjeJHA22MnRsTAoGADXzJs/of0JExvQWwfdIUnSEPs/PgTrrJpo+CAdXnagYHF+InrmvIcNwx6ZzIs+9aGwUt0d/YsSpJkHMfAtTwZjB7sSw8Cg5DZ179Jy3YkKhFPvZv2ZCANa5J74HZNQUrUUL6O4FouZUiLwFlq8YuUPRtkAjYwyS/jwUbhJzqZhQ="
    public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkMX8p3GyMw3gk6x72h20NOk3L9+Nn9mOVP6+YoBwCe7Zs4QmYrA/etFRZw2TQrSc51wgtCkJi1/x8Wl7maPL1uH2+77JFlPv7H/F4Lr2I2LXgnllg6PtwOSw/qvGYInVVB4kL85VQl0/8ObyxBUdJ43I0z/u8hJb2gwujSudOGizbeqQXAYrwcNy+e+cjodpPy9unpJjBfa4Wz2eVLLvUYYKZKdRn6pZR2cQsMBvL30K4cFlZqlJ9iP2hTG3gaiZJ9JrjTigwki0g9pbTDXiPACfuF1nOeObvLD22zBbgn1kwgfsqoG67z7g84u2jvfUFCzX1JRgd0xfNorTRkS2RQIDAQAB"

    dg_sdk.DGClient.mer_config = dg_sdk.MerConfig(private_key, public_key, sys_id, product_id, huifu_id)

参数说明：

    +-------------+----------+
    | 参数        | 中文名   |
    +-------------+----------+
    | public_key  | 汇付公钥 |
    +-------------+----------+
    | private_key | 商户私钥 |
    +-------------+----------+
    | sys_id      | 系统号   |
    +-------------+----------+
    | product_id  | 产品号   |
    +-------------+----------+
    | huifu_id    | 商户号   |
    +-------------+----------+

* 接口调用

    * 以支付宝支付为例，根据接口文档说明，构建请求参数体

    .. code:: Python

        required_params = {
            "trade_type": "A_NATIVE",
            "trans_amt": "1.00",
            "goods_desc": "goods_desc",
        }

    * 调用接口

    .. code:: Python

        url = "https://api.huifu.com/v2/trade/payment/jspay"
        result = dg_sdk.request_post(url, required_params)



* 其他调用方式

除了通用的调用接口之外，SDK 还针对部分重要交易接口提供了一种更便捷的方法，

将一些默认、非必须、无需特别关注的参数传递，以及数据脱敏、加密处理进行了封装。

* SDK 会自动生成必传参数：req_date 以及 req_seq_id，如不想使用SDK内部生成的值，直接传入即可。

* 针对 huifu_id 以及 product_id，如不传，SDK会使用初始化时传入的值。

使用方法如下所示：

    .. code:: Python

        response = dg_sdk.ScanPayment.create(trade_type=trade_type,
                                             trans_amt=amount,
                                             goods_desc="goods_desc",
                                             **extra_info)
        print(response)

现支持模块功能列表如下


* 聚合扫码 ScanPayment
    * 聚合正扫 - create
    * 订单查询 - query
    * 退款创建 - refund
    * 退款查询 - refund_query
    * 反扫 - micro_create
    * 关单 - close
    * 关单查询 - close_query
    * 支付托管预下单 - preorder_create

* 线上交易 OnlinePayment
    * 线上交易查询 - query
    * 线上交易退款 - refund
    * 线上退款查询 - refund_query
    * 银联APP支付 - union_app_create
    * 网银支付页面版 - web_page
    * 手机网页支付 - wap_page
    * 网银付款银行账户查询 - payer_query
    * 网银支付银行列表查询 - bank_list

* 快捷代扣对象 QuickAndHoldPay
    * 支付申请 - apply
    * 快捷支付确认 - confirm
    * 快捷/代扣绑卡申请 - bind_card
    * 快捷/代扣绑卡确认 - bind_card_confirm
    * 快捷代扣解绑 - un_bind
    * 快捷代扣短信重发(v1) - sms_code
    * 快捷页面版 - page
    * 代扣 - with_hold_pay
    * 线上交易查询 - query
    * 退款 - refund
    * 退款查询 - refund_query
    * 快捷支付用户注册 - customer_reg

* 余额支付 AcctPayment
    * 余额支付 - create
    * 余额支付交易查询 - query
    * 余额支付退款 - refund
    * 余额支付退款查询 - refund_query
    * 余额查询 - balance_query

* 代发 Surrogate
    * 代发 - create
    * 出金交易查询 - query

* 取现对象 Settlement
    * 取现 - create
    * 取现查询 - query

* 延时交易对象 Delaytrans
    * 延时交易确认 - confirm
    * 延时交易确认查询 - confirm_query
    * 延时交易退款 - confirm_refund
    * 交易确认批量信息查询(v1) - query_confirm_list
    * 查询交易分账明细 - split_list

* 银行卡分期 Installment
    * 银行卡分期支付签约 - sign
    * 二段式分期支付申请 - payment_apply
    * 二段式分期支付确认 - payment_confirm
    * 银行卡分期退款 - refund
    * 银行卡分期查询 - query

* 商户对象 Merchant
    * 企业类型商户进件 - create_enterprise
    * 个体户类型商户进件 - create_individual
    * 商户基本信息修改 - modify
    * 商户详细信息查询 - query_merch_info
    * 新增总部 - add_headquarters
    * 修改总部 - modify_headquarters
    * 总部商户绑定&解除 - bind_headquarters
    * 查询账户信息 - query_acct_info
    * 商户业务开通 - reg_busi_info
    * 商户业务开通修改 - modify_busi_info
    * 申请单状态查询 - query_apply_status
    * 商户图片资料上传(v1) - upload
    * 商户分账配置 - add_split_config
    * 商户分账配置查询 - query_split_config
    * 商户分期配置 - installment_config
    * 商户分期配置详情查询 - query_fenqi_config
    * 活动报名，支持微信 - reg_activity
    * 机构下属商户查询 - branch_mercust_query
    * 商户关系绑定 - branch_config
    * 机构列表查询 - branch_query

* 分账用户对象 Member
    * 企业用户基本信息注册 - create_enterprise
    * 个人用户基本信息注册 - create_individual
    * 查询账户信息 - query_acct_info
    * 企业用户基本信息修改 - modify_enter_base_info
    * 个人用户基本信息修改 - modify_individual_base_info
    * 用户业务入驻 - reg_busi_info
    * 用户详情查询 - query_user_detail

* 微信商户 WxMerchant
    * 微信商户配置 - config
    * 微信商户配置查询 - query_config
    * 微信实名认证 - realname
    * 微信实名认证状态查询 - query_realname_state
    * 证书登记 - add_cert_info
    * 微信特约商户进件申请 - apply_register_mer
    * 查询微信申请状态 - query_apply_reg
    * 修改微信结算帐号 - modify_settlement_info
    * 查询微信结算账户 - query_settlement_info
    * 微信关注配置 - subscribe_config
    * 微信关注配置查询 - query_subscribe_config

* 支付宝商户 AliMerchant
    * 证书登记 - add_cert_info
    * 签约版-换取应用授权令牌 - exchange_app_auth_token
    * 签约版-申请当面付代签约 - apply_face2face_sign
    * 签约版-查询申请状态 - query_apply_order_status
    * 直付通-商户进件申请 - zft_apply_register_mer
    * 直付通-分账关系绑定&解绑 - zft_split_config
    * 直付通-分账关系查询 - query_zft_split_config

* 云闪付商户 UniPayMerchant
    * 云闪付活动商户入驻 - apply_register_mer
    * 云闪付活动商户入驻状态查询 - query_apply_reg
    * 云闪付活动商户详细信息查询 - query_mer_base_info
    * 云闪付活动列表查询 - query_activity_list
    * 云闪付活动报名 - enlist_activity
    * 云闪付活动报名进度查询 - query_enlish_activity_status

* 花呗分期配置对象 Huabei
    * 支付宝间连证书上传 - add_ali_cert_info
    * 创建花呗分期商家贴息方案 - create_pcredit_solution
    * 上架/下架花呗分期贴息 - modify_solution_status
    * 更新花呗分期商家贴息方案 - modify_pcredit_solution
    * 查询花呗分期贴息 - query_hb_solution
    * 花呗活动详情查询 - query_hb_activity

* 终端设备 Terminal
    * 新增终端设备 - add
    * 注销终端设备 - cancel
    * 绑定终端查询 - query_list

* 智能终端mis接入 Cloudmis
    * 智能终端接入 - device_info

* POS 机交易 POS
    * 银行卡交易查询 - query

* 工具类 DGTools
    * 校验签名 - verify_sign
    * 校验 webhook 返回报文签名 - verify_webhook_sign
    * 使用公钥加密敏感信息 - encrypt_with_public_key



详情参考SDK 接入说明_

.. _接入说明: https://paas.huifu.com/docs/partners/devtools/#/sdk_python
