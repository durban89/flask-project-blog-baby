# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-12 17:53:08
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-13 09:41:59
import mongoengine as me


class Imdb(me.EmbeddedDocument):
    imdb_id = me.StringField()
    rating = me.DecimalField()
    votes = me.IntField()
