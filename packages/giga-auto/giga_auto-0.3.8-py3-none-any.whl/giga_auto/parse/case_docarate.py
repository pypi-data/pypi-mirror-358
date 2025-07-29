from functools import wraps

import allure

from giga_auto.assert_utils import AssertUtils
from giga_auto.base_class import OperationApi
from giga_auto.parse.parse_case import ParseCase
from giga_auto.parse.parse_step import ParseStep
from giga_auto.conf.settings import settings


def case_decorate():
    def _wrapper(func):
        @wraps(func)
        def wrapper(self, case_data, variables, db, service):
            allure.dynamic.feature(variables['feature_variables']['name'])
            allure.dynamic.story(variables['case_variables']['name'])
            allure.dynamic.title(case_data['desc'])
            parse = ParseCase(case_data, variables, settings.business, db)
            parse.parse_prepare()  # 处理setup，失败不进入用例执行
            try:
                steps = case_data['steps']
                for step in steps:  # 处理步骤，适配依赖其它接口请求的接口测试
                    parse_step = ParseStep(step, variables, settings.business, db)
                    if 'params' in step:  # 根据params判断是否走接口请求
                        account_key = step.pop('account_key', 'admin')
                        service = step.pop('service', service)
                        api_request = OperationApi().aggregate_api[service](service=service,
                                                               account_key=account_key,
                                                               reload_login=step.pop('reload_login', False))
                        parse_step.parse_params()
                        params = step['params']
                        api_method = params.pop('api_method', None) or variables['api_method']
                        resp = getattr(api_request, api_method)(**params)
                        parse_step.parse_extract(resp)
                        parse_step.parse_validate(resp)
                        AssertUtils().validate(step['validate'])
                    else:
                        resp = parse_step.parse_function()
                        parse_step.parse_extract(resp)
            finally:
                parse.parse_teardown()  # 处理teardown,无论如何都执行teardown操作

        return wrapper

    return _wrapper
