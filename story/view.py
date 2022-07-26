from flask import Blueprint, render_template

story = Blueprint('story', __name__)

@story.route('/story', methods=['GET'])
def our_story():
    return render_template('story.html')
