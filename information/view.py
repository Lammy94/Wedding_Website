from core.core import *
from flask import Blueprint, render_template
from json import dumps

info = Blueprint('info', __name__)

@info.route('/info', methods=['GET'])
def information():
    """
    simply returns the 'information' page (static content page)
    '"""
    return render_template('information.html', config=dumps(get_config()))
