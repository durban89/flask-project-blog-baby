# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-12 17:04:22
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-12 17:13:42
from werkzeug.utils import import_string, cached_property


class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)
