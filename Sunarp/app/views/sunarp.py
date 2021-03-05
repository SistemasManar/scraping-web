# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
from flask import Blueprint, Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from jobs.sunarp import scrap_plate_number
from models.vehicle import Vehicle
from playhouse.flask_utils import object_list
from redis import Redis
from rq import Queue
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Optional
import csv
import io
import os
import peewee


sunarp_blueprint = Blueprint('sunarp', __name__)


# Redis queues
connection = Redis()
default_queue = Queue('default_sunarp', connection=connection)
high_queue = Queue('high_sunarp', connection=connection)


# Forms

class SearchForm(FlaskForm):
    term = StringField('', validators=[DataRequired('Este campo es requerido')])


class VehicleForm(FlaskForm):
    plate_number = StringField('N° PLACA', validators=[Optional()])
    serial_number = StringField('N° SERIE', validators=[Optional()])
    vin_number = StringField('N° VIN', validators=[Optional()])
    engine_number = StringField('N° MOTOR', validators=[Optional()])
    color = StringField('COLOR', validators=[Optional()])
    make = StringField('MARCA', validators=[Optional()])
    model = StringField('MODELO', validators=[Optional()])
    valid_plate_number = StringField('PLACA VIGENTE', validators=[Optional()])
    previous_plate_number = StringField('PLACA ANTERIOR', validators=[Optional()])
    state = StringField('ESTADO', validators=[Optional()])
    notes = StringField('ANOTACIONES', validators=[Optional()])
    branch = StringField('SEDE', validators=[Optional()])
    owners = StringField('PROPIETARIO(S)', validators=[Optional()])
    submit = SubmitField('Guardar')
    reprocess = SubmitField('Reprocesar')


class UploadForm(FlaskForm):
    file = FileField('Archivo', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Se requiere un archivo de tipo CSV')
    ])


class QueryForm(FlaskForm):
    plate_number = StringField('Número de placa', validators=[
        DataRequired('Este campo es requerido')
    ])

    def validate_plate_number(form, field):
        parsed_data = field.data.upper().replace('-', '')
        if len(parsed_data) != 6:
            raise ValidationError('Placa inválida')


# Routes

@sunarp_blueprint.route('/', methods=['GET', 'POST'])
def home():
    connection = db.connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            v.id,
            v.plate_number,
            v.serial_number,
            v.vin_number,
            v.engine_number,
            v.color,
            v.make,
            v.model,
            v.valid_plate_number,
            v.previous_plate_number,
            v.state,
            v.notes,
            v.branch,
            v.owners,
            v.status,
            v.created
        FROM vehicle v
        ORDER BY v.created DESC
        LIMIT 10;
    ''')
    vehicles = cursor.fetchall()
    return render_template('sunarp/home.html',
        vehicles=vehicles,
    )


@sunarp_blueprint.route('/vehicle/<id>', methods=['GET', 'POST'])
def view_vehicle(id):
    try:
        vehicle = Vehicle.get(Vehicle.id == id)
    except Vehicle.DoesNotExist:
        return redirect(url_for('sunarp.home'))
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        if form.submit.data:
            form.populate_obj(vehicle)
            if vehicle.id == vehicle.plate_number:
                vehicle.status = 1
            vehicle.save()
            flash('Registro actualizado', 'success')
            return redirect(url_for('sunarp.view_vehicle', id=vehicle.id))
        elif form.reprocess.data:
            high_queue.enqueue(scrap_plate_number, vehicle)
            flash('Registro enviado a la cola de proceso', 'info')
            return redirect(url_for('sunarp.view_vehicle', id=vehicle.id))
    return render_template('sunarp/view_vehicle.html', vehicle=vehicle, form=form)


@sunarp_blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            inserted, duplicated, invalid = process_from_csv(form.file.data)
            flash('Archivo procesado con éxito: {:,} encolados(s), {:,} duplicado(s), {:,} inválido(s)'.format(inserted, duplicated, invalid), 'success')
        except Exception as e:
            flash('Error al procesar el archivo: {}'.format(e), 'danger')

        return redirect(url_for('sunarp.home'))

    return render_template('sunarp/upload.html', form=form)


@sunarp_blueprint.route('/query', methods=['GET', 'POST'])
def query():
    form = QueryForm()
    if form.validate_on_submit():
        plate_number = form.plate_number.data.strip().upper().replace('-', '')
        # Return vehicle object if it already exists in database
        try:
            vehicle = Vehicle.get(Vehicle.id == plate_number)
        except Vehicle.DoesNotExist:
            vehicle = Vehicle.create(id=plate_number)
            high_queue.enqueue(scrap_plate_number, vehicle)
        return redirect(url_for('sunarp.view_vehicle', id=vehicle.id))
    return render_template('sunarp/query.html', form=form)


@sunarp_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    vehicles = []
    if form.validate_on_submit():
        term = form.term.data.strip()
        connection = db.connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                v.id,
                v.plate_number,
                v.serial_number,
                v.vin_number,
                v.engine_number,
                v.color,
                v.make,
                v.model,
                v.valid_plate_number,
                v.previous_plate_number,
                v.state,
                v.notes,
                v.branch,
                v.owners,
                v.status,
                v.created
            FROM vehicle v
            WHERE
                v.id ILIKE %s OR
                v.plate_number ILIKE %s OR
                v.serial_number ILIKE %s OR
                v.vin_number ILIKE %s OR
                v.engine_number ILIKE %s OR
                v.color ILIKE %s OR
                v.make ILIKE %s OR
                v.model ILIKE %s OR
                v.valid_plate_number ILIKE %s OR
                v.previous_plate_number ILIKE %s OR
                v.state ILIKE %s OR
                v.notes ILIKE %s OR
                v.branch ILIKE %s OR
                v.owners ILIKE %s
            ORDER BY v.id;
        ''', ['%{}%'.format(term)] * 14)
        vehicles = cursor.fetchall()
    return render_template('sunarp/search.html', form=form, vehicles=vehicles)


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
            plate_number = row[0].strip().upper().replace('-', '')
            if len(plate_number) == 6:
                with db.atomic():
                    vehicle = Vehicle.create(id=plate_number)
                # Add to process queue
                result = default_queue.enqueue(scrap_plate_number, vehicle)
                inserted += 1
            else:
                invalid += 1
        except peewee.IntegrityError:
            duplicated += 1
        except Exception as e:
            invalid += 1

    return inserted, duplicated, invalid
