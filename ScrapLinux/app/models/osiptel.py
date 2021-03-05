# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
import peewee


class RRLL(peewee.Model):
    id = peewee.AutoField()
    ruc = peewee.CharField(null=False, max_length=25)
    dni = peewee.CharField(null=False, max_length=25)
    provider = peewee.CharField(null=True, max_length=999)
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
        db_table = 'rrll'
        indexes = (
            (('ruc', 'dni', 'provider'), True),
        )


class TelephoneLine(peewee.Model):
    rrll = peewee.ForeignKeyField(RRLL, backref='records')
    modality = peewee.CharField(null=True, max_length=999)
    telephone = peewee.CharField(null=True, max_length=999)
    created = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db
        db_table = 'telephone_line'
