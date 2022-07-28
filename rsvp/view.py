from core.core import *
from flask import Blueprint, render_template, request
from datetime import datetime
from json import dumps

rsvp = Blueprint('rsvp', __name__)

@rsvp.route('/rsvp', methods=['GET', 'POST'])
def rsvp_page():
    # make sure the user hasnt tried to navigate to the page without a
    # bundle id set
    if not request.cookies.get('bundle'):
        return render_template('error.html', Error_Message="No user data found")
    else:
        bundle = get_bundle_details(request.cookies.get('bundle'))


    # if the request was a submittion of the form
    if request.method == "POST":
        # Get the form data
        form_responses = request.form.to_dict()

        # Extract and remove the bundle_id from the hidden input element
        bundle_id, s_requirements = form_responses['bundle_id'], form_responses['special_requirements']
        form_responses.pop('bundle_id')
        form_responses.pop('special_requirements')

        # iterate over each response, update the database with individual responses
        for each in form_responses:
            day = 1 if form_responses[each] in ["both", "day"] else 0
            evening = 1 if form_responses[each] in ["both", "evening"] else 0
            current_datetime = datetime.now()
            update_table(f"UPDATE People SET attending_day = {day}, attending_evening = {evening}, response_datetime = '{current_datetime}' WHERE person_id = {each.split('_')[1]};")

        # Sanitize special requirements!
        # update the bundle
        update_table(f"UPDATE Bundle SET responded=1, special_requirements='{s_requirements}' WHERE bundle_id = '{bundle_id}';")
        return rsvp_thanks()

    # retun the content to the user 
    return render_template(
        'rsvp.html',
        config=dumps(get_config()),
        people=get_people(bundle),
        bundle=bundle
        )

@rsvp.route('/rsvp_thank_you')
def rsvp_thanks():
    """
    function to return the thank you page on form submittion (static content page)
    """
    return render_template('thank_you.html', response="Thank you for your response!")
