import functools
from functools import wraps

from giga_auto.base_class import ApiResponse
from giga_auto.conf.settings import settings


def api_decorate(url, method='get', assert_resp=False):
    """
    装饰api数据，组装配置的路径与api函数里的数据，请求接口
    """

    def _decorate(func):
        func.api_url = url

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            data = func(self, *args, **kwargs) or {}
            data['url'] = url
            data['method'] = method
            if assert_resp:
                resp = self.request(**data)
            else:
                resp = self._request(**data)
            return ApiResponse(resp)
        return wrapper

    return _decorate

get_api = functools.partial(api_decorate, method='GET')
post_api = functools.partial(api_decorate, method='POST')
delete_api = functools.partial(api_decorate, method='DELETE')
put_api = functools.partial(api_decorate, method='PUT')

get_api_ast = functools.partial(api_decorate, method='GET', assert_resp=True)
post_api_ast = functools.partial(api_decorate, method='POST', assert_resp=True)
delete_api_ast = functools.partial(api_decorate, method='DELETE', assert_resp=True)
put_api_ast = functools.partial(api_decorate, method='PUT', assert_resp=True)


def retry_login(times=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for i in range(times):
                try:
                    result = func(self, *args, **kwargs)
                except Exception as e:
                    self.kwargs['retry_login'] = False
                    raise e
                if result == settings.UNAUTHORIZED:  # 认证失败重登一次
                    self.kwargs['retry_login'] = True
                else:
                    self.kwargs['retry_login'] = False
                    return result
            return None

        return wrapper

    return decorator
