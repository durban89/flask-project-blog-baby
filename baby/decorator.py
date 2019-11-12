# -*- coding: utf-8 -*-
# @Author: durban
# @Date:   2019-11-12 11:19:43
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-12 14:57:51

from functools import wraps
from flask import request, render_template
from baby.extensions import cache


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint.replace('.', '/') + '.j2'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx

            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


def cached(timeout=5 * 60, key='view/%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.path
            rv = cache.get(cache_key)
            if rv is None:
                rv = f(*args, **kwargs)

            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator
