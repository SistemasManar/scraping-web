# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from jobs.sunedu import scrap_document_number
from models.graduate import Graduate, GraduateRecord
from playhouse.flask_utils import object_list
from redis import Redis
from rq import Queue
from wtforms import DateField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Optional
import csv
import io
import os
import peewee


sunedu_blueprint = Blueprint('sunedu', __name__)

# Redis queues
connection = Redis()
default_queue = Queue('default_sunedu', connection=connection)
high_queue = Queue('high_sunedu', connection=connection)


# Forms

class SearchForm(FlaskForm):
    term = StringField('', validators=[DataRequired('Este campo es requerido')])


class GraduateForm(FlaskForm):
    submit = SubmitField('Guardar')
    reprocess = SubmitField('Reprocesar')


class UploadForm(FlaskForm):
    file = FileField('Archivo', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Se requiere un archivo de tipo CSV')
    ])


class QueryForm(FlaskForm):
    document_number = StringField('D.N.I.', validators=[
        DataRequired('Este campo es requerido')
    ])

    def validate_document_number(form, field):
        parsed_data = field.data.upper()
        if len(parsed_data) != 8:
            raise ValidationError('D.N.I. inválido')


# Routes

@sunedu_blueprint.route('/', methods=['GET', 'POST'])
def home():
    connection = db.connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            g.status,
            g.id,
            gr.name,
            gr.grade,
            gr.institution,
            gr.created
        FROM graduate_record gr
        RIGHT JOIN graduate g
            ON g.id = gr.graduate_id
        ORDER BY gr.created
        LIMIT 10;
    ''')
    records = cursor.fetchall()
    return render_template(
        'sunedu/home.html',
        records=records,
    )


@sunedu_blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            inserted, duplicated, invalid = process_from_csv(form.file.data)
            flash('Archivo procesado con éxito: {:,} encolados(s), {:,} duplicado(s), {:,} inválido(s)'.format(inserted, duplicated, invalid), 'success')
        except Exception as e:
            flash('Error al procesar el archivo: {}'.format(e), 'danger')

        return redirect(url_for('sunedu.home'))

    return render_template('sunedu/upload.html', form=form)


@sunedu_blueprint.route('/query', methods=['GET', 'POST'])
def query():
    form = QueryForm()
    if form.validate_on_submit():
        document_number = form.document_number.data.strip().upper()
        # Return graduate object if it already exists in database
        try:
            graduate = Graduate.get(Graduate.id == document_number)
        except Graduate.DoesNotExist:
            graduate = Graduate.create(id=document_number)
            high_queue.enqueue(scrap_document_number, graduate)
        return redirect(url_for('sunedu.view_graduate', id=graduate.id))
    return render_template('sunedu/query.html', form=form)


@sunedu_blueprint.route('/graduate/<id>', methods=['GET', 'POST'])
def view_graduate(id):
    try:
        graduate = Graduate.get(Graduate.id == id)
        records = graduate.records.order_by(GraduateRecord.created.asc())
    except Graduate.DoesNotExist:
        return redirect(url_for('sunedu.home'))
    form = GraduateForm(obj=graduate)
    if form.validate_on_submit():
        if form.submit.data:
            form.populate_obj(graduate)
            graduate.status = 1
            graduate.save()
            flash('Registro actualizado', 'success')
            return redirect(url_for('sunedu.view_graduate', id=graduate.id))
        elif form.reprocess.data:
            # Unset all fields
            graduate.status = 0
            graduate.save()
            # Delete existing specialties
            for record in records:
                record.delete_instance()
            high_queue.enqueue(scrap_document_number, graduate)
            flash('Registro enviado a la cola de proceso', 'info')
            return redirect(url_for('sunedu.view_graduate', id=graduate.id))
    return render_template(
        'sunedu/view_graduate.html',
        graduate=graduate,
        records=records,
        form=form
    )


@sunedu_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    records = []
    if form.validate_on_submit():
        term = form.term.data.strip()
        connection = db.connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                g.status,
                g.id,
                gr.name,
                gr.grade,
                gr.institution,
                gr.created
            FROM graduate_record gr
            RIGHT JOIN graduate g
                ON g.id = gr.graduate_id
            WHERE
                g.id ILIKE %s OR
                gr.name ILIKE %s OR
                gr.grade ILIKE %s OR
                gr.institution ILIKE %s
            ORDER BY gr.created;
        ''', ['%{}%'.format(term)] * 4)
        records = cursor.fetchall()
    return render_template('sunedu/search.html', form=form, records=records)


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
            document_number = row[0].strip().upper()
            if len(document_number) == 8:
                with db.atomic():
                    graduate = Graduate.create(id=document_number)
                # Add to process queue
                result = default_queue.enqueue(scrap_document_number, graduate)
                inserted += 1
            else:
                invalid += 1
        except peewee.IntegrityError:
            duplicated += 1
        except Exception as e:
            invalid += 1

    return inserted, duplicated, invalid
