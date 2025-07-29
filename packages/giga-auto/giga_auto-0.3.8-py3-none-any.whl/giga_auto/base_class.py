"""基础类，最好不要调用其它模块"""
import os
import inspect
import importlib

from giga_auto.conf.settings import settings
from giga_auto.request import RequestBase


class ApiBase(RequestBase):
    def __init__(self, **env):
        self.host = env.get('host', '')
        super().__init__(self.host, env.get('expect_code', 200))
        self.headers = env.get('headers', {})

    def set_headers(self, headers):
        self.headers = headers


class ConfigMeta(type):

    def __init__(cls, name, bases, attrs):
        cls.config={att:attrs[att] for att in attrs['__annotations__']}


class SingletonMeta(type):
    """
    单例元类：根据初始化参数区分不同实例
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        args_key = (cls, args, frozenset(kwargs.items()))
        if args_key not in SingletonMeta._instances:
            SingletonMeta._instances[args_key] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[args_key]


class Response:
    """针对新型写法需要针对response或者数据查询数据包一层"""

    def __init__(self, response):
        self.response = response

    def __getitem__(self, item):
        return self.response[item]

    def __repr__(self):
        if hasattr(self.response, 'text'):
            return self.response.text
        else:
            return self.response

    def __getattr__(self, attr):
        attr = attr.split('.')
        mid_value = self.response
        index = 0
        is_has_x = False
        while index < len(attr):
            att = attr[index]
            if att == 'content' and index==0:
                if isinstance(mid_value, dict):
                    mid_value = self.response
                else:
                    mid_value = self.response.json()
            elif is_has_x:
                mid_value = [k[att] for k in mid_value]
            elif att=='$': #返回全部
                mid_value=self.response
            elif isinstance(mid_value, dict):
                mid_value = mid_value[att]
            elif isinstance(mid_value, list):
                if att == '*':
                    is_has_x = True
                    mid_value = mid_value
                else:
                    mid_value = mid_value[int(att)]
            else:
                mid_value = getattr(mid_value, att)
            index += 1
        return mid_value


class OperationApi(metaclass=SingletonMeta):
    """针对新型api层写法统一放在这聚合分发类以及统计api数"""

    def __init__(self):
        self.api_path=settings.Constants.API_ROOT_DIR
        self.project_path=settings.Constants.BASE_DIR
        self._api_map=None

    def statistic_api(self):
        number_map={}
        for service in os.listdir(self.api_path):
            if service not in settings.ServiceKey.config.values():
                continue
            api_root_path=os.path.join(self.api_path, service)
            total=0
            module=self.dynamic_import_api(api_root_path)
            for m in module:
                class_objects=self.get_module_classes(m)
                total+=sum([len(self.get_api_method_name(class_object)) for class_object in class_objects])
            number_map[service]=total
        # todo 待提供接口，每周上传
        print(number_map)
        return number_map

    def dynamic_import_api(self,root_path:str):
        module_list=[]
        for root, dirs, files in os.walk(root_path):
            for filename in files:
                if filename.startswith('api') and filename.endswith('.py'):
                    m = os.path.relpath(os.path.join(root, filename), self.project_path).replace(os.sep, '.')[:-3]
                    m = importlib.import_module(m)
                    module_list.append(m)
        return module_list

    @staticmethod
    def get_module_classes(module):
        """获取模块中定义的所有类"""
        return [
            obj for name, obj in inspect.getmembers(module)
            if inspect.isclass(obj) and obj.__module__ == module.__name__
        ]

    @staticmethod
    def get_api_method_name(class_object):
        """获取类有多少个api函数"""
        return [name for name,obj in inspect.getmembers(class_object) if hasattr(obj,'api_url')]

    def check_repeat(self,class_list):
        """检查该service是否存在同名api方法"""
        name_list=[]
        for class_obj in class_list:
            name_list.extend(self.get_api_method_name(class_obj))
        repeat_set = set(filter(lambda x: name_list.count(x) > 1, name_list))
        if len(repeat_set) > 0:
            raise Exception(f"出现重复api方法名，请检查方法：{repeat_set}")

    @property
    def aggregate_api(self):
        """根据api_request目录聚合类，按照目录进行分发,已获取后就不会再获取，直接取self._api_map"""
        if self._api_map is None:
            self._api_map={}
            for filename in os.listdir(self.api_path):
                file_path=os.path.join(self.api_path, filename)
                api_obj_list=[]
                if os.path.isdir(file_path) and filename != '__pycache__':
                    modules=self.dynamic_import_api(file_path)
                    for module in modules:
                        api_obj_list.extend(self.get_module_classes(module))
                    self.check_repeat(api_obj_list)
                    api_request = type('ApiRequest', tuple(api_obj_list), {})
                    self._api_map[filename]=api_request
        return self._api_map
