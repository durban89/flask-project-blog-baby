# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-06 11:04:15
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-13 13:40:29

from . import (
    home,
    auth,
    food,
    chat,
    blog,
    langcode,
    stream,
    api_food,
    api_food_type,
    api_food_week,
    api_auth,
)
from baby.helper import LazyView


def init_app(app):
    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(food.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(langcode.bp)
    app.register_blueprint(stream.bp)
    app.register_blueprint(api_food.bp)
    app.register_blueprint(api_food_type.bp)
    app.register_blueprint(api_food_week.bp)
    app.register_blueprint(api_auth.bp)

    app.add_url_rule(
        '/langcode/me',
        view_func=LazyView('baby.views.langcode.me')
    )
