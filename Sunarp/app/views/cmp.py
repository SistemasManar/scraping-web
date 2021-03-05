# -*- coding: utf-8 -*-
from app import db
from flask import Blueprint, Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from jobs.cmp import scrap_cmp
from models.doctor import Doctor, DoctorSpecialty
from redis import Redis
from rq import Queue
from wtforms import DateField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Optional
import csv
import io


cmp_blueprint = Blueprint('cmp', __name__)

# Redis queues
connection = Redis()
default_queue = Queue('default_cmp', connection=connection)
high_queue = Queue('high_cmp', connection=connection)


# Forms

class DoctorForm(FlaskForm):
    cmp = StringField('C.M.P.', validators=[Optional()])
    name = StringField('NOMBRES', validators=[Optional()])
    surname = StringField('APELLIDOS', validators=[Optional()])
    state = StringField('ESTADO', validators=[Optional()])
    email = StringField('EMAIL', validators=[Optional()])
    region = StringField('REGIÓN', validators=[Optional()])
    notes = StringField('NOTAS', validators=[Optional()])
    submit = SubmitField('Guardar')
    reprocess = SubmitField('Reprocesar')


class QueryForm(FlaskForm):
    cmp = StringField('C.M.P.', validators=[
        DataRequired('Este campo es requerido')
    ])

    def validate_cmp(form, field):
        parsed_data = field.data.upper()
        if len(parsed_data) != 6:
            raise ValidationError('C.M.P. inválido')


class SearchForm(FlaskForm):
    term = StringField('', validators=[DataRequired('Este campo es requerido')])


class UploadForm(FlaskForm):
    file = FileField('Archivo', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Se requiere un archivo de tipo CSV')
    ])


# Routes

@cmp_blueprint.route('/', methods=['GET', 'POST'])
def home():
    connection = db.connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            d.id,
            d.name,
            d.surname,
            d.state,
            d.email,
            d.region,
            d.notes,
            d.status,
            d.created
        FROM doctor d
        ORDER BY d.created DESC
        LIMIT 10;
    ''')
    doctors = cursor.fetchall()
    return render_template('cmp/home.html',
        doctors=doctors,
    )


@cmp_blueprint.route('/query', methods=['GET', 'POST'])
def query():
    form = QueryForm()
    if form.validate_on_submit():
        cmp = form.cmp.data.strip().upper()
        # Return doctor object if it already exists in database
        try:
            doctor = Doctor.get(Doctor.id == cmp)
        except Doctor.DoesNotExist:
            doctor = Doctor.create(id=cmp)
            high_queue.enqueue(scrap_cmp, doctor)
        return redirect(url_for('cmp.view_doctor', id=doctor.id))
    return render_template('cmp/query.html', form=form)


@cmp_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    doctors = []
    if form.validate_on_submit():
        term = form.term.data.strip()
        connection = db.connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                d.id,
                d.name,
                d.surname,
                d.state,
                d.email,
                d.region,
                d.status,
                d.created
            FROM doctor d
            WHERE
                d.id ILIKE %s OR
                d.name ILIKE %s OR
                d.surname ILIKE %s OR
                d.state ILIKE %s OR
                d.email ILIKE %s OR
                d.region ILIKE %s
            ORDER BY d.id;
        ''', ['%{}%'.format(term)] * 6)
        doctors = cursor.fetchall()
    return render_template('cmp/search.html', form=form, doctors=doctors)


@cmp_blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            inserted, duplicated, invalid = process_from_csv(form.file.data)
            flash('Archivo procesado con éxito: {:,} encolados(s), {:,} duplicado(s), {:,} inválido(s)'.format(inserted, duplicated, invalid), 'success')
        except Exception as e:
            flash('Error al procesar el archivo: {}'.format(e), 'danger')
        return redirect(url_for('cmp.home'))
    return render_template('cmp/upload.html', form=form)


@cmp_blueprint.route('/doctor/<id>', methods=['GET', 'POST'])
def view_doctor(id):
    try:
        doctor = Doctor.get(Doctor.id == id)
        specialties = doctor.specialties.order_by(DoctorSpecialty.name)
    except Doctor.DoesNotExist:
        return redirect(url_for('cmp.home'))
    form = DoctorForm(obj=doctor)
    if form.validate_on_submit():
        if form.submit.data:
            form.populate_obj(doctor)
            doctor.status = 1
            doctor.save()
            flash('Registro actualizado', 'success')
            return redirect(url_for('cmp.view_doctor', id=doctor.id))
        elif form.reprocess.data:
            # Unset all fields
            doctor.name = None
            doctor.surname = None
            doctor.state = None
            doctor.email = None
            doctor.region = None
            doctor.notes = None
            doctor.status = 0
            doctor.save()
            # Delete existing specialties
            for specialty in specialties:
                specialty.delete_instance()
            high_queue.enqueue(scrap_cmp, doctor)
            flash('Registro enviado a la cola de proceso', 'info')
            return redirect(url_for('cmp.view_doctor', id=doctor.id))
    return render_template(
        'cmp/view_doctor.html',
        doctor=doctor,
        specialties=specialties,
        form=form
    )


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
            cmp = row[0].strip().upper()
            if len(cmp) == 6:
                with db.atomic():
                    doctor = Doctor.create(id=cmp)
                # Add to process queue
                result = default_queue.enqueue(scrap_cmp, doctor)
                inserted += 1
            else:
                invalid += 1
        except peewee.IntegrityError:
            duplicated += 1
        except Exception as e:
            invalid += 1

    return inserted, duplicated, invalid
