# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-13 16:30:07
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-14 18:35:17
from baby import create_app
from baby.celery import create_celery
celery = create_celery(create_app())


@celery.task(name="tasks.add_together")
def add_together(a, b):
    return a + b


@celery.task(name="tasks.send_email")
def send_email(email):
    pass
