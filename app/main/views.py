from flask import render_template, current_app, session
from flask_login import current_user
from . import main


@main.route('/')
def index():
    return render_template('index.html')

