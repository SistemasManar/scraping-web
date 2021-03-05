# -*- coding: utf-8 -*-
from app import app, db
from models import *
from jobs import *
from views import *


# Blueprints

app.register_blueprint(index_blueprint, url_prefix='/')
app.register_blueprint(cmp_blueprint, url_prefix='/cmp')
app.register_blueprint(sunarp_blueprint, url_prefix='/sunarp')
app.register_blueprint(sunedu_blueprint, url_prefix='/sunedu')
app.register_blueprint(osiptel_blueprint, url_prefix='/osiptel')


def create_tables():
    # Create table for each model if it does not exist.
    # Use the underlying peewee database object instead of the
    # flask-peewee database wrapper:
    tables = [
        Doctor,
        DoctorSpecialty,
        Graduate,
        GraduateRecord,
        Proxy,
        Vehicle,
        RRLL,
        TelephoneLine,
    ]
    db.create_tables(tables, safe=True)


if __name__ == "__main__":
    create_tables()
    app.run(host='0.0.0.0', debug=True, port=8080)
