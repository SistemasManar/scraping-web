# -*- coding: utf-8 -*-
"""
CREATE TABLE public.vehicle
(
  id character varying(6) NOT NULL,
  plate_number character varying(255),
  serial_number character varying(255),
  vin_number character varying(255),
  engine_number character varying(255),
  color character varying(255),
  make character varying(255),
  model character varying(255),
  valid_plate_number character varying(255),
  previous_plate_number character varying(255),
  state character varying(255),
  notes character varying(255),
  branch character varying(255),
  owners character varying(255),
  status smallint NOT NULL,
  created timestamp without time zone NOT NULL,
  CONSTRAINT vehicle_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
"""
from app import db
from datetime import datetime
import peewee


class Vehicle(peewee.Model):
    id = peewee.CharField(primary_key=True, max_length=6)
    plate_number = peewee.CharField(null=True)
    serial_number = peewee.CharField(null=True)
    vin_number = peewee.CharField(null=True)
    engine_number = peewee.CharField(null=True)
    color = peewee.CharField(null=True)
    make = peewee.CharField(null=True)
    model = peewee.CharField(null=True)
    valid_plate_number = peewee.CharField(null=True)
    previous_plate_number = peewee.CharField(null=True)
    state = peewee.CharField(null=True)
    notes = peewee.CharField(null=True)
    branch = peewee.CharField(null=True)
    owners = peewee.CharField(null=True)
    image_path = peewee.CharField(null=True)
    status = peewee.SmallIntegerField(default=0)
    created = peewee.DateTimeField(default=datetime.now)

    @property
    def show_owners(self):
        return self.owners.replace('|', '<br>')

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
        db_table = 'vehicle'
