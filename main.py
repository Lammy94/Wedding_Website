#!/usr/bin/env python3

from core.core import *
from datetime import datetime, timedelta
from flask import Flask, render_template, request, make_response, redirect, url_for
from json import dumps

# import views (areas of site)
from api.view import api
from information.view import info
from music.view import music
from rsvp.view import rsvp
from story.view import story

app = Flask(__name__, )
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# register the 
app.register_blueprint(api)
app.register_blueprint(info)
app.register_blueprint(music)
app.register_blueprint(rsvp)
app.register_blueprint(story)

# Note - throughout project a group of users is refered to as a 'bundle'

@app.route("/", methods=['GET'])
def homepage():
    """
    main homepage for the site
    """
    # check that a bundle key is either present in the request arguments or session details
    bundle = check_for_bundle_key(request)

    # if no bundle key is found, serve the "enter code" page
    if not bundle:
        return render_template('enter_code.html')
    
    # Get details from the database around the bundle
    # if valid id not found, let the user know 
    bundle = get_bundle_details(bundle)
    if not bundle:
        return render_template('error.html', Error_Message="Unique code not found in system")

    # Generate a response to be sent
    resp = make_response(render_template(
        'index.html',
        config=dumps(get_config()),
        people=get_people_string(bundle)
    ))

    # Set the bundle cookie so that the user is logged in if they come back
    resp.set_cookie('bundle', str(bundle['bundle_unique_id']), expires=datetime.now() + timedelta(days=365))
    
    # Standard "dont cache" headers
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"

    # some recipients may need a gentle reminder
    resp.headers["LADS"] = "No Hacking!" 

    # return the response to the user
    return resp


@app.route("/login", methods=['POST'])
def login():
    """
    if the user has gone through the login page, 
    the request will go here before they get redirected
    """

    # get the id from the request
    given_id = request.form.to_dict()['code']
    bundle = get_bundle_details(given_id)

    # if the bundle is valid, redirect them to the homepage and log them in.
    # setting the cookie with their bundle id
    # else return the error page
    if bundle:
        resp = make_response(redirect(url_for('homepage'), code=302))
        resp.set_cookie('bundle', str(given_id), expires=datetime.now() + timedelta(days=365))
        return resp
    else:
        return render_template('error.html', Error_Message="Unique code not found in system")


@app.route("/logout", methods=['GET'])
def logout():
    """
    if the user has clicked the logout button:
        - wipes the cookie tracking their bundle id
        - redirects to the homepage
    """
    resp = make_response(redirect(url_for('homepage'), code=302))
    resp.delete_cookie('bundle')
    return resp


@app.route("/error")
def error():
    """
    return a generic error template
    """
    return render_template('error.html')


@app.route("/robots.txt")
def robots():
    """
    specific for google robots. stops google from scanning in and indexing the site
    """
    resp = make_response(render_template('robot.html'))
    return resp

# if the program ran directly - load in debug mode
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

# if the program run indirectly. will be through gunicorn 
# so setup logging
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
