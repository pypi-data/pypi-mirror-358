# @Time : 2023-06-14 10:48
# @Author  : Huang.XiaoGang
# @Desc : ==============================================
# Life is Short I Use Python!!!                      ===
# ======================================================
# @Project : GbopApiClient
# @FileName: event_push
# @Software: PyCharm
import uuid
import datetime
import requests
import json
from .common import ResultStruct


class CloudEventBasicAuth(object):
    PROTOCOL_TYPE = 'cloudevents'
    LANGUAGE = 'Python'
    CONTENT_TYPE = 'application/json;charset=utf-8'

    def __init__(self, producer_group: str, subject: str, secret_token: str):
        if not producer_group:
            raise Exception('请使用应用配置[ProducerGroup]')
        if not subject.startswith('persistent://'):
            raise Exception('请使用应用配置[Topic]参数值')
        if not secret_token:
            raise Exception('请使用密钥管理[密钥]参数值')
        self.producer_group = producer_group
        self.subject = subject
        self.secret_token = secret_token


class EventPushClient(object):
    def __init__(self, auth: object, base_url: str):
        if not isinstance(auth, CloudEventBasicAuth):
            raise Exception('当前只支持CloudEventBasicAuth验证方式')
        if not base_url.startswith('http'):
            raise Exception('推送地址不正确,请使用https,http开头的推送地址')
        self.auth = auth
        self.base_url = base_url + '/eventmesh/publish'

    def _get_headers(self):
        """
        生成header
        :return:
        """
        headers = {
            "producergroup": self.auth.producer_group,
            "protocoltype": self.auth.PROTOCOL_TYPE,
            "token": self.auth.secret_token,
            "content-type": self.auth.CONTENT_TYPE,
            "language": self.auth.LANGUAGE,
            "time": datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', '+08:00'),
        }
        return headers

    def push_message(self, data: dict, source: str, type_: str, id_: str = '', timeout: int = 30,
                     header: dict = {}) -> str:
        """
        消息推送
        :param timeout: 超时时间
        :param data: 数据体
        :param header: header
        :param source: 数据来源
        :param type_: 数据类型
        :param id_: 自定义数据编号(不传使用uuid)
        :return: response content
        """
        _data = {
            "id": id_ if id_ else str(uuid.uuid1()),
            "source": source,
            "type": type_,
            "specversion": "1.0",
            "subject": self.auth.subject,
            "data": data
        }
        headers = self._get_headers()
        if isinstance(header, dict):
            headers.update(header)
        response = requests.post(self.base_url, json=_data, headers=headers, timeout=timeout).content
        return response

    def push(self, data: dict, source: str, type_: str, id_: str = '', timeout: int = 30, header: dict = {}) -> str:
        """
        消息推送
        :param timeout: 超时时间
        :param data: 数据体
        :param source: 数据来源
        :param type_: 数据类型
        :param header: header
        :param id_: 自定义数据编号(不传使用uuid)
        :return: response content
        """
        _data = {
            "id": id_ if id_ else str(uuid.uuid1()),
            "source": source,
            "type": type_,
            "specversion": "1.0",
            "subject": self.auth.subject,
            "data": data
        }
        headers = self._get_headers()
        if isinstance(header, dict):
            headers.update(header)
        response = requests.post(self.base_url, json=_data, headers=headers, timeout=timeout).content
        res_json = json.loads(response.decode('utf-8'))
        code = res_json['retCode']
        msg = res_json['retMsg']
        if code == 0:
            result = True
            data = msg[msg.find('messageId=') + 10:-1]
            msg = ''
        else:
            result = False
            data = None
        return ResultStruct(result, code, msg, data)
