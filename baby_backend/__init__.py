# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-06 17:18:31
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-06 17:41:43

import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'baby.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return 'baby backend'

    return app


application = create_app()

if __name__ == '__main__':
    application.run()
