from core.core import *
from flask import Blueprint, jsonify, render_template, request
from json import dumps
import requests
import threading
import urllib

music = Blueprint('music', __name__)

class getArtwork(threading.Thread):
    """
    Class to call to MusicBrainz and get the link to album artwork
    runs as its own thread so as not to hold up the ux
    """
    def __init__(self, songName, artist, songID):
        threading.Thread.__init__(self)
        self.songName = songName
        self.artist = artist
        self.songID = songID
        
        # these are placeholders, get overwriten when discovered
        self.release_id = 000
        self.artwork_url = "https://via.placeholder.com/150x150.png?text=No+Album+Cover"

    def run(self):
        self.get_artwork_url()
        self.update_db()

    def get_artwork_url(self):
        url = f"http://musicbrainz.org/ws/2/release/?query=artistname:{urllib.parse.quote_plus(self.songName)}ANDrelease:{urllib.parse.quote_plus(self.artist)}"
        track_data = requests.get(url, headers={'Accept': 'application/json'})
        for release in track_data.json()['releases']:
            release_id = release['id']
            url = "https://coverartarchive.org/release/{}".format(release['id'])
            image_data = requests.get(url, headers={'Accept': 'application/json'})
            if image_data.status_code == 200:
                self.release_id = release_id
                self.artwork_url = image_data.json()['images'][0]['image']
                break

    def update_db(self):
        with db_connect().cursor() as cursor:
            try:
                cursor.execute(f"UPDATE MusicRequests SET musicbrainz_id = '{self.release_id}', artwork = '{self.artwork_url}' WHERE request_id = '{self.songID}';")
                return True
            except Exception as err:
                logging.debug(f"[*] Error: {err}")
                return False

def add_song(form_data):
    with db_connect().cursor() as cursor:
        try:
            cursor.execute(f"SELECT request_id FROM MusicRequests WHERE title = '{form_data['title']}' AND artist = '{form_data['artist']}';")
            data = cursor.fetchone()
        except Exception as err:
            logging.debug(f"[*] Error: {err}")
            return False

        if not data:
            try:
                cursor.execute(f"INSERT INTO MusicRequests (title, artist, requester_id) VALUES ('{form_data['title']}','{form_data['artist']}','{form_data['bundle']}');")
                getArtwork(form_data['title'], form_data['artist'], cursor.lastrowid).start()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
                return False
        else:
            logging.debug(f"[*] Duplicate Found!", flush=True)
    return True
    
def get_all_requested_music():
    with db_connect().cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM MusicRequests ORDER BY title;")
            data = cursor.fetchall()
        except Exception as err:
            data = None
            logging.debug(f"[*] Could not connect to the database: {err}", flush=True)

    return data if data else None


@music.route('/music_api', methods=['GET'])
def music_api():
    return jsonify(get_all_requested_music())

@music.route('/music', methods=['GET', 'POST'])
def music_request():
    if request.method == "POST":
        add_song(request.form.to_dict())
    bundle = get_bundle_details(request.cookies.get('bundle'))
    return render_template('music.html', config=dumps(get_config()), bundle=bundle)
