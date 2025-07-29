# @Time : 2022-07-08 11:18
# @Author  : Huang.XiaoGang
# @Desc : ==============================================
# Life is Short I Use Python!!!                      ===
# ======================================================
# @Project : python_test
# @FileName: PyGbop
# @Software: PyCharm
import base64
import datetime
import enum
import hmac
import time
from urllib.parse import quote_plus
from hashlib import sha256

import requests


class BasicAuth(object):
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key


class Method(enum.Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'


class GbopApiClient(object):
    LN = "\n"

    def __init__(self, auth: BasicAuth, base_url='', protocol='http://'):
        self.auth = auth
        self.base_url = base_url
        self.protocol = protocol

    def _generate_signature(self, path, method, headers, params):
        query_string = self._get_query_str(params, True, False)
        content_array = [method, path, query_string]
        if headers:
            if headers.__contains__("X-Gapi-Ca-Access-Key"):
                content_array.append(headers["X-Gapi-Ca-Access-Key"])
            if headers.__contains__("Date"):
                content_array.append(headers["Date"])
            if headers.__contains__("X-Gapi-Ca-Signed-Headers"):
                custom_headers = headers["X-Gapi-Ca-Signed-Headers"].split(";")
                for custom_header in custom_headers:
                    content_array.append(custom_header + ":" + headers[custom_header])
        content = self.LN.join(content_array) + self.LN
        content = content.encode("utf-8")
        secret_key = self.auth.secret_key.encode("utf-8")
        signature = base64.b64encode(hmac.new(secret_key, content, digestmod=sha256).digest())
        return signature

    def _get_header(self, path, method, params, is_beta_api):
        gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
        headers = {
            "X-Gapi-Ca-Timestamp": str(int(round(time.time() * 1000))),
            "X-Gapi-Ca-Algorithm": "hmac-sha256",
            "X-Gapi-Ca-Access-Key": self.auth.access_key,
            "X-Gapi-Ca-Signed-Headers": 'X-Gapi-Ca-Timestamp',
            "Date": datetime.datetime.utcnow().strftime(gmt_format),
            "Host": self.base_url,
        }
        if is_beta_api:
            headers["X-gapi-route-flag"] = "beta"
        headers["X-Gapi-Ca-Signature"] = self._generate_signature(path, method, headers, params)
        return headers

    def _get_query_str(self, params, is_signature, is_encode_params):  # noqa
        if not params:
            return ''
        queries_dic = sorted(params)
        queries = []
        for k in queries_dic:
            if isinstance(params[k], list):
                params[k].sort()
                for i in params[k]:
                    if not is_signature and is_encode_params:
                        params_value = quote_plus(str(i))
                        queries.append(f'{k}={params_value}')
                    else:
                        queries.append(f'{k}={i}')
            else:
                if not is_signature and is_encode_params:
                    params_value = quote_plus(str(params[k]))
                    queries.append(f'{k}={params_value}')
                else:
                    queries.append(f'{k}={params[k]}')
        return "&".join(queries)

    def _get_url_str(self, path, params, is_encode_params):
        query_str = self._get_query_str(params, False, is_encode_params)
        format_string = f"{self.base_url}{path}?{query_str}" if query_str else f"{self.base_url}{path}"
        url = self.protocol + format_string
        return url

    def execute(self, method=Method.GET, path='', params={}, data={}, files=[], header={}, is_beta_api=False,
                is_has_status=False, timeout=30, data_is_json=False, is_encode_params=False, verify=True):
        """
        接口调用
        :param method: 调用方法
        :param path: 调用路径
        :param params: GET参数
        :param data: POST参数
        :param header: header参数
        :param is_beta_api: 是否测试API
        :param is_has_status: 是否返回http code
        :param timeout: 超时时间
        :param data_is_json: 是否是json格式
        :param is_encode_params: GET参数值是否进行URL编号
        :param verify: 是否验证SSL证书
        :return:
        """
        url = self._get_url_str(path, params, is_encode_params)
        headers = self._get_header(path, method.value, params, is_beta_api)
        if isinstance(header, dict):
            headers.update(header)
        if data_is_json:
            res = requests.request(method.value, url, headers=headers, json=data, files=files, timeout=timeout,
                                   verify=verify)
        else:
            res = requests.request(method.value, url, headers=headers, data=data, files=files, timeout=timeout,
                                   verify=verify)
        if is_has_status:
            return res.status_code, res.content
        else:
            return res.content

    def execute_with_stream(self, method=Method.GET, path='', params={}, data={}, files=[], header={},
                            is_beta_api=False, timeout=30, data_is_json=False, chunk_size=1024, verify=True,
                            is_encode_params=False):
        """
        接口调用
        :param method: 调用方法
        :param path: 调用路径
        :param params: GET参数
        :param data: POST参数
        :param header: header参数
        :param is_beta_api: 是否测试API
        :param timeout: 超时时间
        :param data_is_json: 是否是json格式
        :param chunk_size: 返回数据分块大小
        :param verify: 是否验证SSL证书
        :param files: 文件上传参数
        :param is_encode_params: GET参数值是否进行URL编号
        :return:
        """
        url = self._get_url_str(path, params, is_encode_params)
        headers = self._get_header(path, method.value, params, is_beta_api)
        if isinstance(header, dict):
            headers.update(header)
        if data_is_json:
            res = requests.request(method.value, url, headers=headers, json=data, files=files, timeout=timeout,
                                   stream=True, verify=verify)
        else:
            res = requests.request(method.value, url, headers=headers, data=data, files=files, timeout=timeout,
                                   stream=True, verify=verify)
        if res.status_code == 200:
            for chunk in res.iter_content(chunk_size=chunk_size):
                yield chunk
        else:
            raise Exception(f"返回代码：{res.status_code} 返回数据：{res.content}")
