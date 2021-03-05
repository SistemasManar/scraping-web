# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
import peewee


class Graduate(peewee.Model):
    id = peewee.CharField(primary_key=True, max_length=8)
    status = peewee.SmallIntegerField(default=0)
    created = peewee.DateTimeField(default=datetime.now)

    @property
    def status_class(self):
        if self.status == 0:
            return 'info'
        elif self.status == 1:
            return 'success'
        elif self.status == 2:
            return 'warning'
        elif self.status == 3:
            return 'danger'

    @property
    def status_text(self):
        if self.status == 0:
            return 'PENDIENTE'
        elif self.status == 1:
            return 'PROCESADO'
        elif self.status == 2:
            return 'INVÁLIDO'
        elif self.status == 3:
            return 'ERROR'

    class Meta:
        database = db
        db_table = 'graduate'


class GraduateRecord(peewee.Model):
    graduate = peewee.ForeignKeyField(Graduate, backref='records')
    name = peewee.CharField(null=True, max_length=999)
    grade = peewee.CharField(null=True, max_length=999)
    institution = peewee.CharField(null=True, max_length=999)
    created = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db
        db_table = 'graduate_record'
