# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from jobs.claro_line import scrap_claro_lines
from jobs.movistar_line import scrap_movistar_lines
from models.graduate import Graduate, GraduateRecord
from models.osiptel import RRLL, TelephoneLine
from playhouse.flask_utils import object_list
from redis import Redis
from rq import Queue
from wtforms import DateField, StringField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired, Optional
import csv
import io
import os
import peewee


osiptel_blueprint = Blueprint('osiptel', __name__)

# Redis queues
connection = Redis()
default_queue = Queue('default_osiptel', connection=connection)
high_queue = Queue('high_osiptel', connection=connection)


# Forms

class SearchForm(FlaskForm):
    term = StringField('Buscar Por:', validators=[DataRequired('Este campo es requerido')])


class RRLLForm(FlaskForm):
    reprocess = SubmitField('Reprocesar')
    sel_provider = SelectField('Proveedor', choices=[('CLARO', 'CLARO'), ('MOVISTAR', 'MOVISTAR')])


class UploadForm(FlaskForm):
    file = FileField('Archivo', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Se requiere un archivo de tipo CSV')
    ])


class QueryForm(FlaskForm):
    document_ruc = StringField('Numero RUC', validators=[
        DataRequired('Este campo es requerido')
    ])
    document_dni = StringField('D.N.I.', validators=[
        DataRequired('Este campo es requerido')
    ])

    def validate_document_ruc(form, field):
        parsed_data = field.data.upper()
        if len(parsed_data) != 11:
            raise ValidationError('RUC inválido')

    def validate_document_dni(form, field):
        parsed_data = field.data.upper()
        print(parsed_data)
        if len(parsed_data) < 8 or len(parsed_data) > 9:
            raise ValidationError('DNI o Cta. Externa inválida')


# Routes

@osiptel_blueprint.route('/', methods=['GET', 'POST'])
def home():
    connection = db.connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            rl.status,
            rl.ruc,
            rl.dni,
            CASE WHEN rl.provider IS NULL THEN '---' ELSE rl.provider END AS provider,
            (CASE WHEN rl.status = 0 OR rl.status = 2 OR rl.status = 3 THEN '---' ELSE CAST(COUNT(tpl.rrll_id) as VARCHAR) END) AS nu_lineas,
            rl.created
        FROM rrll rl
        LEFT JOIN telephone_line tpl ON rl.id = tpl.rrll_id
        GROUP BY rl.status, rl.ruc, rl.dni, rl.provider, rl.created
        ORDER BY rl.created DESC
        LIMIT 1000;
    ''')
    records = cursor.fetchall()
    return render_template(
        'osiptel/home.html',
        records=records,
    )


'''*******************************************************************************************'''

@osiptel_blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            inserted, duplicated, invalid = process_from_csv(form.file.data)
            flash('Archivo procesado con éxito: {:,} encolados(s), {:,} duplicado(s), {:,} inválido(s)'.format(inserted, duplicated, invalid), 'success')
        except Exception as e:
            flash('Error al procesar el archivo: {}'.format(e), 'danger')

        return redirect(url_for('osiptel.home'))

    return render_template('osiptel/upload.html', form=form)


@osiptel_blueprint.route('/query', methods=['GET', 'POST'])
def query():
    form = QueryForm()
    if form.validate_on_submit():
        document_ruc = form.document_ruc.data.strip().upper()
        document_dni = form.document_dni.data.strip().upper()
        # Return rrll object if it already exists in database
        try:
            rrll_main = RRLL.get(RRLL.ruc == document_ruc, RRLL.dni == document_dni, provider = 'CLARO')
        except RRLL.DoesNotExist:
            #The rrll_main is the object which starts first in the pills and at the same time is some provider.
            rrll_main = RRLL.create(ruc = document_ruc, dni = document_dni, provider = 'CLARO')
            rrll_movistar = RRLL.create(ruc = document_ruc, dni = document_dni, provider = 'MOVISTAR')
            high_queue.enqueue(scrap_claro_lines, rrll_main)
            high_queue.enqueue(scrap_movistar_lines, rrll_movistar)
        return redirect(url_for('osiptel.view_rrll', ruc=rrll_main.ruc, dni=rrll_main.dni, provider = 'CLARO'))
    return render_template('osiptel/query.html', form=form)


#Aca se usa el jobs
@osiptel_blueprint.route('/rrll/<ruc>/<dni>/<provider>', methods=['GET', 'POST'])
def view_rrll(ruc, dni, provider):
    form = RRLLForm(sel_provider = provider)
    try:
        rrll = RRLL.get(RRLL.ruc == ruc, RRLL.dni == dni, RRLL.provider == provider)
        records = rrll.records.order_by(TelephoneLine.created.asc())
    except RRLL.DoesNotExist:
        return redirect(url_for('osiptel.home'))
        
    if form.reprocess.data:
        # Unset all fields
        rrll.status = 0
        rrll.save()
        # Delete existing
        for record in records:
            record.delete_instance()

        if rrll.provider == 'CLARO':
            high_queue.enqueue(scrap_claro_lines, rrll)
        elif rrll.provider == 'MOVISTAR':
            high_queue.enqueue(scrap_movistar_lines, rrll)

        flash('Registro enviado a la cola de proceso', 'info')
        return redirect(url_for('osiptel.view_rrll', ruc=rrll.ruc, dni=rrll.dni, provider=rrll.provider))
    return render_template(
        'osiptel/view_rrll.html',
        rrll=rrll,
        records=records,
        form=form
    )


@osiptel_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    records = []
    if form.validate_on_submit():
        term = form.term.data.strip()
        connection = db.connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT 
                rl.status,
                rl.ruc,
                rl.dni,
                CASE WHEN rl.provider IS NULL THEN '---' ELSE rl.provider END AS provider,
                (CASE WHEN rl.status = 0 OR rl.status = 2 OR rl.status = 3 THEN '---' ELSE CAST(COUNT(tpl.rrll_id) as VARCHAR) END) AS nu_lineas,
                rl.created
            FROM rrll rl
            LEFT JOIN telephone_line tpl
                ON rl.id = tpl.rrll_id
            WHERE
                rl.ruc ILIKE %s OR
                rl.dni ILIKE %s OR
                rl.provider ILIKE %s OR
                tpl.modality ILIKE %s OR
                tpl.telephone ILIKE %s
            GROUP BY rl.status, rl.ruc, rl.dni, rl.provider, rl.created;
        ''', ['%{}%'.format(term)] * 5)
        records = cursor.fetchall()
    return render_template('osiptel/search.html', form=form, records=records)


# Helpers

#Aca se usa el jobs
def process_from_csv(input_file):
    stream = io.StringIO(input_file.read().decode('utf-8'))
    csvfile = csv.reader(stream, delimiter=';')
    inserted = 0
    invalid = 0
    duplicated = 0
    records = []

    for row in csvfile:
        try:
            document_ruc = row[0].strip().upper()
            document_dni = row[1].strip().upper()

            if len(document_ruc) == 11 and (len(document_dni) > 7 and len(document_dni) < 10):
                with db.atomic():
                    rrll_claro = RRLL.create(ruc = document_ruc, dni = document_dni, provider = 'CLARO')
                    rrll_movistar = RRLL.create(ruc = document_ruc, dni = document_dni, provider = 'MOVISTAR')
                # Add to process queue
                result = default_queue.enqueue(scrap_claro_lines, rrll_claro)
                result = default_queue.enqueue(scrap_movistar_lines, rrll_movistar)
                inserted += 1
            else:
                invalid += 1
            
        except peewee.IntegrityError:
            duplicated += 1
        except Exception as e:
            print(e)
            invalid += 1

    return inserted, duplicated, invalid
