# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-13 16:30:07
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-14 22:54:57
from flask_mail import Message
from baby.extensions import mail
from baby import create_app
from baby.celery import create_celery
celery = create_celery(create_app())


@celery.task(name="tasks.add_together")
def add_together(a, b):
    return a + b


@celery.task(name="tasks.send_login_email")
def send_login_email(user, email):

    subject = 'Hello, %s' % user
    message = 'Login Success'
    html = '<p>Login Success</p>'
    msg = Message(
        subject=subject,
        body=message,
        html=html,
        recipients=[email]
    )

    mail.send(msg)
