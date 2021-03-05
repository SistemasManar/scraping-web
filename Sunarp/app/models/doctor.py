# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
import peewee


class Doctor(peewee.Model):
    id = peewee.CharField(primary_key=True, max_length=6)
    name = peewee.CharField(null=True, max_length=100)
    surname = peewee.CharField(null=True, max_length=100)
    state = peewee.CharField(null=True, max_length=50)
    email = peewee.CharField(null=True, max_length=100)
    region = peewee.CharField(null=True, max_length=200)
    notes = peewee.CharField(null=True, max_length=250)
    image_path = peewee.CharField(null=True, max_length=999)
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
        db_table = 'doctor'


class DoctorSpecialty(peewee.Model):
    doctor = peewee.ForeignKeyField(Doctor, backref='specialties')
    name = peewee.CharField(null=True, max_length=500)
    type = peewee.CharField(null=True, max_length=100)
    code = peewee.CharField(null=True, max_length=10)
    end_date = peewee.DateField(null=True)

    class Meta:
        database = db
        db_table = 'doctor_specialty'
