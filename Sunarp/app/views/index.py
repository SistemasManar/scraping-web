# -*- coding: utf-8 -*-
from app import db
from flask import Blueprint, Flask, flash, render_template, request, url_for


index_blueprint = Blueprint('index', __name__)


@index_blueprint.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index/home.html')
