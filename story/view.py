from flask import Blueprint, render_template

story = Blueprint('story', __name__)

@story.route('/story', methods=['GET'])
def our_story():
    """
    simply returns the 'our story page (static content page)
    '"""
    return render_template('story.html')
