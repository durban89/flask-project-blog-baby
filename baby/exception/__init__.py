# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-07 15:00:54
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-07 15:18:06


class InvalidUsage(Exception):
    """docstring for InvalidUsage"""

    status_code = 404

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv
