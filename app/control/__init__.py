# Blueprint Constructor for control module
from flask import Blueprint

control = Blueprint('control', __name__)

from . import views


