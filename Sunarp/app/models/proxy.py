# -*- coding: utf-8 -*-
from app import db
from datetime import date
import peewee


class Proxy(peewee.Model):
    service = peewee.CharField()
    ip = peewee.CharField()
    created = peewee.DateField(default=date.today)

    class Meta:
        database = db
        db_table = 'proxy'
