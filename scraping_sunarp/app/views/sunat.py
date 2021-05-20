from app import db
from datetime import datetime
from flask import Blueprint, Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from jobs.sunat import scrap_ruc_number
from models.ruc import RUC
from playhouse.flask_utils import object_list
from redis import Redis
from rq import Queue
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Optional
import csv
import io
import os
import peewee


sunat_blueprint = Blueprint('sunat', __name__)


# Redis queues
connection = Redis()
default_queue = Queue('default_sunat', connection=connection)
high_queue = Queue('high_sunat', connection=connection)


# Forms

class SearchForm(FlaskForm):
    term = StringField('', validators=[DataRequired('Este campo es requerido')])


class RucForm(FlaskForm):
    ruc_number = StringField('N° RUC', validators=[Optional()])
    ruc_name = StringField('RUC NAME', validators=[Optional()])
    tipo_contribuyente = StringField('Tipo Contribuyente', validators=[Optional()])
    tipo_docu = StringField('Tipo documento', validators=[Optional()])
    nombre_comercial = StringField('NOMBRE COMERCIAL', validators=[Optional()])
    fecha_inic = StringField('FECHA INICIO', validators=[Optional()])
    fecha_ins = StringField('FECHA INSCRIPCION', validators=[Optional()])
    estado_contribuyente = StringField('ESTADO CONTRIBUYENTE', validators=[Optional()])
    condicion_contribuyente = StringField('CONDICION CONTRIBUYENTE', validators=[Optional()])
    domicilio = StringField('DOMICILIO', validators=[Optional()])
    region = StringField('REGION', validators=[Optional()])
    distrito = StringField('DISTRITO', validators=[Optional()])
    sistema_emision_c = StringField('SISTEMA EMISION CONTRIBUYENTE', validators=[Optional()])
    actividad_comercio = StringField('ACTIVIDAD(ES) COMERCIALES', validators=[Optional()])
    sistema_contabilidad = StringField('SISTEMA CONTABILIDAD', validators=[Optional()])
    actividad_economica = StringField('ACTIVDAD(ES) ECONOMICA(S)', validators=[Optional()])
    comprobante_pago= StringField('COMPROBANTE DE PAGO', validators=[Optional()])
    sistema_emision_e= StringField('SISTEMA DE EMISION ELECTRONICA', validators=[Optional()])
    emisor_electronico= StringField('EMISOR ELECTRONICO DESDE', validators=[Optional()])
    comprobante_electronico= StringField('COMPROBANTE ELECTRONICO', validators=[Optional()])
    afiliado_ple= StringField('AFILIADO AL PLE', validators=[Optional()])
    padrones= StringField('PADRONES', validators=[Optional()])
    owners= StringField('CANTIDAD TRABAJADORES', validators=[Optional()])
    legalre= StringField('REPRESENTATES LEGALES(S)', validators=[Optional()])
    submit = SubmitField('Guardar')
    reprocess = SubmitField('Reprocesar')


class UploadForm(FlaskForm):
    file = FileField('Archivo', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Se requiere un archivo de tipo CSV')
    ])


class QueryForm(FlaskForm):
    ruc_number = StringField('Número de RUC', validators=[
        DataRequired('Este campo es requerido')
    ])

    def validate_ruc_number(form, field):
        parsed_data = field.data.upper().replace('-', '')
        if len(parsed_data) != 11:
            raise ValidationError('RUC INVALIDO')


# Routes

@sunat_blueprint.route('/', methods=['GET', 'POST'])
def home():
    connection = db.connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            r.id,
            r.ruc_number,
            r.ruc_name,
            r.tipo_contribuyente,
            r.tipo_docu,
            r.nombre_comercial,
            r.fecha_inic,
            r.fecha_ins,
            r.estado_contribuyente,
            r.condicion_contribuyente,
            r.domicilio,
            r.region,
            r.distrito,
            r.sistema_emision_c,
            r.actividad_comercio,
            r.sistema_contabilidad,
            r.actividad_economica,
            r.comprobante_pago,
            r.sistema_emision_e,
            r.emisor_electronico,
            r.comprobante_electronico,
            r.afiliado_ple,
            r.padrones,
            r.owners,
            r.legalre,
            r.status,
            r.created
        FROM ruc r
        ORDER BY r.created DESC
        LIMIT 10;
    ''')
    rucs = cursor.fetchall()
    return render_template('sunat/home.html',
        rucs=rucs,
    )


@sunat_blueprint.route('/ruc/<id>', methods=['GET', 'POST'])
def view_ruc(id):
    try:
        ruc = RUC.get(RUC.id == id)
    except RUC.DoesNotExist:
        return redirect(url_for('sunat.home'))
    form = RucForm(obj=ruc)
    if form.validate_on_submit():
        if form.submit.data:
            form.populate_obj(ruc)            
            if ruc.id == ruc.ruc_number:
                ruc.status = 1
            ruc.save()
            flash('Registro actualizado', 'success')
            return redirect(url_for('sunat.view_ruc', id=ruc.id))
        elif form.reprocess.data:
            high_queue.enqueue(scrap_ruc_number, ruc)
            flash('Registro enviado a la cola de proceso', 'info')
            return redirect(url_for('sunat.view_ruc', id=ruc.id))
    return render_template('sunat/view_ruc.html', ruc=ruc, form=form)


@sunat_blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            inserted, duplicated, invalid = process_from_csv(form.file.data)
            flash('Archivo procesado con éxito: {:,} encolados(s), {:,} duplicado(s), {:,} inválido(s)'.format(inserted, duplicated, invalid), 'success')
        except Exception as e:
            flash('Error al procesar el archivo: {}'.format(e), 'danger')

        return redirect(url_for('sunat.home'))

    return render_template('sunat/upload.html', form=form)


@sunat_blueprint.route('/query', methods=['GET', 'POST'])
def query():
    form = QueryForm()
    if form.validate_on_submit():
        ruc_num = form.ruc_number.data.strip()
        # Return ruc object if it already exists in database
        try:
            ruc = RUC.get(RUC.id == ruc_num)
        except RUC.DoesNotExist:
            ruc = RUC.create(id=ruc_num)
            high_queue.enqueue(scrap_ruc_number, ruc)
        return redirect(url_for('sunat.view_ruc', id=ruc.id))
    return render_template('sunat/query.html', form=form)


@sunat_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    rucs = []
    if form.validate_on_submit():
        term = form.term.data.strip()
        connection = db.connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                r.id,
                r.ruc_number,
                r.ruc_name,
                r.tipo_contribuyente,
                r.tipo_docu,
                r.nombre_comercial,
                r.fecha_inic,
                r.fecha_ins,
                r.estado_contribuyente,
                r.condicion_contribuyente,
                r.domicilio,
                r.region,
                r.distrito,
                r.sistema_emision_c,
                r.actividad_comercio,
                r.sistema_contabilidad,
                r.comprobante_pago,
                r.sistema_emision_e,
                r.emisor_electronico,
                r.comprobante_electronico,
                r.afiliado_ple,
                r.padrones,
                r.owners,
                r.legalre,
                r.status,
                r.created
            FROM ruc r
            WHERE
                r.id ILIKE %s OR
                r.ruc_number ILIKE %s OR
                r.ruc_name ILIKE %s OR
                r.tipo_contribuyente ILIKE %s OR
                r.tipo_docu ILIKE %s OR
                r.nombre_comercial ILIKE %s OR
                r.fecha_inic ILIKE %s OR
                r.fecha_ins ILIKE %s OR
                r.estado_contribuyente ILIKE %s OR
                r.condicion_contribuyente ILIKE %s OR
                r.domicilio ILIKE %s OR
                r.region ILIKE %s OR
                r.distrito ILIKE %s OR               
                r.sistema_emision_c ILIKE %s OR
                r.actividad_comercio ILIKE %s OR
                r.sistema_contabilidad ILIKE %s OR
                r.actividad_economica ILIKE %s OR
                r.comprobante_pago ILIKE %s OR
                r.sistema_emision_e ILIKE %s OR
                r.emisor_electronico ILIKE %s OR
                r.comprobante_electronico ILIKE %s OR
                r.afiliado_ple ILIKE %s OR
                r.padrones ILIKE %s OR
                r.owners ILIKE %s OR
                r.legalre ILIKE %s             
            ORDER BY r.id;
        ''', ['%{}%'.format(term)] * 25)
        rucs = cursor.fetchall()
    return render_template('sunat/search.html', form=form, rucs=rucs)


# Helpers

def process_from_csv(input_file):
    stream = io.StringIO(input_file.read().decode('utf-8'))
    csvfile = csv.reader(stream)
    inserted = 0
    invalid = 0
    duplicated = 0
    records = []

    for row in csvfile:
        try:
            ruc = row[0].strip().upper().replace('-', '')
            if len(ruc) == 11:
                with db.atomic():
                    ruc = RUC.create(id=ruc)
                # Add to process queue
                result = default_queue.enqueue(scrap_ruc_number, ruc)
                inserted += 1
            else:
                invalid += 1
        except peewee.IntegrityError:
            duplicated += 1
        except Exception as e:
            invalid += 1

    return inserted, duplicated, invalid
