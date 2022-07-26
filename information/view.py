from core.core import *
from flask import Blueprint, render_template
from json import dumps

info = Blueprint('info', __name__)

@info.route('/info', methods=['GET'])
def information():
    return render_template('information.html', config=dumps(get_config()))
