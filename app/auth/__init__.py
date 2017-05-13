# Blueprint Constructor for authentication module
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
