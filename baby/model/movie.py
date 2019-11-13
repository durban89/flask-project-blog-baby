# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-12 17:48:55
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-13 10:12:48
from flask_mongoengine import Document
import mongoengine as me
from . import Imdb


class Movie(Document):
    title = me.StringField()
    year = me.IntField()
    rated = me.StringField()
    director = me.StringField()
    actors = me.ListField()
    imdb = me.EmbeddedDocumentField(Imdb)
