# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-13 17:19:11
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-13 17:19:25
from celery import Celery


def create_celery(app=None):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
