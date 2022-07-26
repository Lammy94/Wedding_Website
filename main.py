#!/usr/bin/env python3

from core.core import *
from datetime import datetime, timedelta
from flask import Flask, render_template, request, make_response, redirect, url_for
from json import dumps

from api.view import api
from information.view import info
from music.view import music
from rsvp.view import rsvp
from story.view import story

app = Flask(__name__, )
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.register_blueprint(api)
app.register_blueprint(info)
app.register_blueprint(music)
app.register_blueprint(rsvp)
app.register_blueprint(story)


@app.route("/", methods=['GET'])
def homepage():
    bundle = check_for_bundle_key(request)
    if not bundle:
        return render_template('enter_code.html')
    bundle = get_bundle_details(bundle)
    if not bundle:
        return render_template('error.html', Error_Message="Unique code not found in system")

    resp = make_response(render_template('index.html', config=dumps(get_config()), people=get_people_string(bundle)))
    resp.set_cookie('bundle', str(bundle['bundle_unique_id']), expires=datetime.now() + timedelta(days=365))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers["LADS"] = "No Hacking!" # for the boys at work
    return resp


@app.route("/login", methods=['POST'])
def login():
    given_id = request.form.to_dict()['code']
    bundle = get_bundle_details(given_id)

    if bundle:
        resp = make_response(redirect(url_for('homepage'), code=302))
        resp.set_cookie('bundle', str(given_id), expires=datetime.now() + timedelta(days=365))
        return resp
    else:
        return render_template('error.html', Error_Message="Unique code not found in system")


@app.route("/logout", methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('homepage'), code=302))
    resp.delete_cookie('bundle')
    return resp


@app.route("/error")
def error():
    return render_template('error.html')


@app.route("/robots.txt")
def robots():
    resp = make_response(render_template('robot.html'))
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
