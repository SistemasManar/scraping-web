"""
CREATE TABLE public.ruc
(
  id character varying(6) NOT NULL,
  RUC_number character varying(255),
  tipo_contribuyente character varying(255),
  nombre_comercial character varying(255),
  fecha_ins character varying(255),
  fecha_ini character varying(255),
  estado_contribuyente character varying(255),
  condicion_contribuyente character varying(255),
  domicilio character varying(255),
  region character varying(255),
  distrito character varying(255),
  sistema_emision_C character varying(255),
  actividad_comercio character varying(255),
  comprobante_pago character varying(255),
  sistema_emision_E character varying(255),
  emisor_electronico character varying(255),
  comprobante_electronico character varying(255),
  afiliado_ple character varying(255),
  padrones character varying(255),
  cantidad_trabajadores character varying(255),
  status smallint NOT NULL,
  created timestamp without time zone NOT NULL,
  CONSTRAINT ruc_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
"""
from app import db
from datetime import datetime
import peewee


class RUC(peewee.Model):
    id = peewee.CharField(primary_key=True, max_length=11)
    ruc_number = peewee.CharField(null=True)
    ruc_name = peewee.CharField(null=True)
    tipo_contribuyente = peewee.CharField(null=True)
    tipo_docu = peewee.CharField(null=True)
    nombre_comercial = peewee.CharField(null=True)
    fecha_inic = peewee.CharField(null=True)
    fecha_ins = peewee.CharField(null=True)
    estado_contribuyente = peewee.CharField(null=True)
    condicion_contribuyente = peewee.CharField(null=True)
    domicilio = peewee.CharField(null=True)
    region = peewee.CharField(null=True)
    distrito = peewee.CharField(null=True)
    sistema_emision_c = peewee.CharField(null=True)
    actividad_comercio = peewee.CharField(null=True)
    sistema_contabilidad = peewee.CharField(null=True)
    actividad_economica = peewee.CharField(null=True)
    comprobante_pago = peewee.CharField(null=True)
    sistema_emision_e = peewee.CharField(null=True)
    emisor_electronico = peewee.CharField(null=True)    
    comprobante_electronico = peewee.CharField(null=True)
    afiliado_ple = peewee.CharField(null=True)
    padrones = peewee.CharField(null=True)
    owners = peewee.CharField(null=True)
    legalre = peewee.CharField(null=True)    
    status = peewee.SmallIntegerField(default=0)
    created = peewee.DateTimeField(default=datetime.now)

    @property
    def show_owners(self):
       return self.owners.replace('|', '<br>')
    
    @property
    def show_legalre(self):
       return self.legalre.replace('|', '<br>')

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
        db_table = 'ruc'
