from flask import Blueprint, session

main = Blueprint('main', __name__)

from . import views, errors

""""@main.app_context_processor
def inject_user_id():
    user_id = session['user_id']
    return {'user_id': user_id}"""
