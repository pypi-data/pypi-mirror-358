import os
import importlib


class LazySettings(object):

    def __init__(self):
        self._settings = None
        self._business=None

    def __getattr__(self, name):
        if self._settings is None:
            module_path=os.environ['GIGA_SETTINGS_MODULE']
            self._settings=importlib.import_module(module_path)
        if name == 'business':
            business_path=self._settings.business
            self._business=importlib.import_module(business_path)
            return self._business
        return getattr(self._settings, name)

settings = LazySettings()