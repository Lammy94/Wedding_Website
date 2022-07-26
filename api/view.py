from core.core import *
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, send_from_directory, redirect, url_for, make_response
import imgkit
import pdfkit
import pymysql
import pyqrcode
import threading
from PyPDF2 import PdfFileMerger
import os

api = Blueprint('api', __name__)


class MakeQRCode:
    def __init__(self, base_url, id):
        self.database = self.db_connect()
        self.base_url = base_url
        self.bundle_id = id
        self.bundle_data = self.get_data()
        self.url = self.make_url()
        self.code = self.make_code()

    def get_data(self):
        with self.database.cursor() as cursor:
            try:
                cursor.execute(f"SELECT * FROM Bundle WHERE bundle_id = '{self.bundle_id}';")
                data = cursor.fetchone()
            except Exception as err:
                logging.info(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else False

    def make_url(self):
        return f"{self.base_url}?bundle={self.bundle_data['bundle_unique_id']}"

    def make_code(self):
        return pyqrcode.create(self.url)

    @staticmethod
    def db_connect():
        return pymysql.connect(
            host='localhost',
            user=getenv('db_user'),
            password=getenv('db_pass'),
            db='wedding',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            charset='utf8'
        )


class MakeInvite(threading.Thread):
    def __init__(self, base_url, id, as_image=False, save_html=False):
        threading.Thread.__init__(self)

        self.database = self.db_connect()
        self.config = self.get_config()
        self.bundle_details = self.get_bundle_details(id)
        self.QR = MakeQRCode(base_url, id)

        location = {"1": "The Speech House", "2": "Speech House Rd", "3": "Coleford", "4": "GL16 7EL"}

        dt = datetime.strptime(self.config['Wedding_date'], '%Y-%m-%d')
        dates = {"day": dt.strftime('%A'),
                 "date": dt.strftime("%B %d %Y"),
                 "rsvp": datetime.strptime(self.config['RSVP_Date'], '%Y-%m-%d').strftime("%d %B")}
        times = {
            "ceremony": datetime.strptime(self.config['Ceremony_Start'], '%H:%M:%S').strftime('%H:%M %p'),
            "evening": datetime.strptime(self.config['Evening_Start'], '%H:%M:%S').strftime('%H:%M %p')
        }

        # Render the template with details
        self.template = render_template(
            'invite.html',
            dates=dates,
            times=times,
            location=location,
            link=self.QR.url,
            attend_day=self.bundle_details['bundle_invited_day'],
            qr=self.QR.code.png_as_base64_str(scale=3),
            bundle_name=self.bundle_details['bundle_name'],
            config=self.config
        )

        # Output the html as an image
        self.file = self.html_to_img() if as_image else self.html_to_pdf()

        if save_html:
            self.write_to_file()

        print(f"[*] Invite generated for {self.bundle_details['bundle_name']}")

        self.outcome = "success"

    def write_to_file(self):
        with open(f"invites/{self.bundle_details['bundle_name']}.html", "w") as file:
            file.write(self.template)

    def get_people(self):
        with self.database.cursor() as cursor:
            try:
                cursor.execute(
                    f"SELECT person_first FROM People WHERE bundle_id = '{self.bundle_details['bundle_id']}'")
                data = cursor.fetchall()
            except Exception as err:
                logging.info(f"[*] Could not connect to the database: {err}", flush=True)

        people = [each['person_first'] for each in data]

        return ', '.join(people)

    def html_to_img(self):
        file_name = f"invites/{self.bundle_details['bundle_name']}.png"
        imgkit.from_string(self.template, file_name)
        return file_name

    def html_to_pdf(self):
        file_name = f"invites/{self.bundle_details['bundle_name']}.pdf"
        pdfkit.from_string(self.template, file_name, options={
            'page-size': 'A5',
            'margin-top': '0',
            'margin-right': '0',
            'margin-bottom': '0',
            'margin-left': '0',
        })
        return file_name

    def get_bundle_details(self, id):
        with self.database.cursor() as cursor:
            try:
                cursor.execute(f"SELECT * FROM Bundle WHERE bundle_id = '{id}';")
                data = cursor.fetchone()
            except Exception as err:
                logging.info(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else False

    def get_config(self):
        with self.database.cursor() as cursor:
            try:
                cursor.execute(f"SELECT * FROM Configuration;")
                data = cursor.fetchall()
            except Exception as err:
                logging.info(f"[*] Could not connect to the database: {err}", flush=True)
        return {each['Key']: each['Value'] for each in data} if data else False

    @staticmethod
    def db_connect():
        return pymysql.connect(
            host='localhost',
            user=getenv('db_user'),
            password=getenv('db_pass'),
            db='wedding',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            charset='utf8'
        )

class MakePlaceCard(threading.Thread):
    def __init__(self, as_image=False, save_html=False):
        threading.Thread.__init__(self)

        self.database = self.db_connect()
        self.people = self.get_people()

        # Render the template with details
        self.template = render_template(
            'placecard.html',
            person=self.people
        )

        # Output the html as an image
        # self.file = self.html_to_img() if as_image else self.html_to_pdf()

        if save_html:
            self.write_to_file()

        self.outcome = "success"

    def write_to_file(self):
        with open(f"placecard/all.html", "w") as file:
            file.write(self.template)

    def html_to_img(self):
        file_name = f"placecard/all.png"
        imgkit.from_string(self.template, file_name)
        return file_name

    def html_to_pdf(self):
        file_name = f"placecard/all.pdf"
        pdfkit.from_string(self.template, file_name, options={
            'page-size': 'A6',
            'margin-top': '0',
            'margin-right': '0',
            'margin-bottom': '0',
            'margin-left': '0',
        })
        return file_name

    def get_people(self):
        with self.database.cursor() as cursor:
            try:
                cursor.execute(f"SELECT * FROM People WHERE attending_day = 1;")
                data = cursor.fetchall()
            except Exception as err:
                logging.info(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else False

    @staticmethod
    def db_connect():
        return pymysql.connect(
            host='localhost',
            user=getenv('db_user'),
            password=getenv('db_pass'),
            db='wedding',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            charset='utf8'
        )


@api.route('/api/guestlist', methods=['GET'])
def guestlist():
    def stat_last_response():
        with db_connect().cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM Entire_Guestlist;")
                data = cursor.fetchall()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else []
    def stat_responses():
        with db_connect().cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM Response_Counts;")
                data = cursor.fetchone()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else []

    bundle = check_for_bundle_key(request)
    if bundle not in ['370960', "351254", "543391"]:
        return redirect(url_for('homepage'))

    return render_template('guestlist.html', data=stat_last_response(), stats=stat_responses())

@api.route('/api/music_list', methods=['GET'])
def musiclist():
    def get_all():
        with db_connect().cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM wedding.Music_Report;")
                data = cursor.fetchall()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
                data = None
        return data if data else []

    bundle = check_for_bundle_key(request)
    display_requesters = True if bundle and bundle == '370960' else False

    return render_template('musiclist.html', data=get_all(), requesters=display_requesters)

@api.route('/api/gen_invite', methods=['GET'])
def generate_invite():
    bundle_id = request.args.get('id')
    logging.info(f"invited generation requested for {bundle_id}")
    if bundle_id:
        invite = MakeInvite(request.url_root, bundle_id)
        return send_from_directory('', invite.file, as_attachment=False)
    else:
        response = jsonify({"error": f"no bundle id provided"})
    return response

@api.route('/api/gen_placecard', methods=['GET'])
def generate_placecard():
    placecard = MakePlaceCard()
    return placecard.template

@api.route('/api/dev_placecard', methods=['GET'])
def dev_placecard():
    return render_template(
            'placecard.html',
            person = [{'person_first':'ryan', 'person_last':'lambert'},{'person_first':'india', 'person_last':'lambert'}]
        )


@api.route('/api/gen_all_invites', methods=['GET'])
def generate_all_invite():
    bundles = get_all_bundle_ids()

    creator_threads = []
    for each in bundles:
        creator_thread = MakeInvite(request.url_root, each)
        creator_thread.start()
        creator_threads.append(creator_thread)

    for x in creator_threads:
        x.join()

    return download_all_invite()

@api.route('/api/download_all_invites', methods=['GET'])
def download_all_invite():
    folder = "invites"
    file_name = "all_invites.pdf"

    if os.path.exists(f"{folder}/{file_name}"):
        os.remove(f"{folder}/{file_name}")

    pdfs = [f for f in os.listdir(folder)]
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(f"{folder}/{pdf}")
    merger.write(f"{folder}/{file_name}")
    merger.close()
    return send_from_directory('', f"{folder}/{file_name}", as_attachment=False)

@api.route('/api/stats', methods=['GET'])
def stats():
    def stat_counts():
        with db_connect().cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM wedding.Response_Counts;")
                data = cursor.fetchone()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else {'Total': 0}

    def stat_responses():
        with db_connect().cursor() as cursor:
            try:
                cursor.execute("SELECT Responded, Not_Responded, Total_Invites FROM wedding.Responses;")
                data = cursor.fetchone()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else {'Total_Invites': 0}

    def stat_today():
        with db_connect().cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM Today_Responses;")
                data = cursor.fetchone()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else {"Today": 0}
    counts = stat_counts()
    counts.update(stat_responses())
    counts.update(stat_today())

    return jsonify(counts)


@api.route('/api/last', methods=['GET'])
def last():
    def stat_last_response():
        with db_connect().cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM wedding.Recent_Responses LIMIT 1;")
                data = cursor.fetchone()
            except Exception as err:
                logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return data if data else {"Last_Name": "Aaron A. Aaronson", "Last_Bundle": "The Greater Good"}
    return jsonify(stat_last_response())

