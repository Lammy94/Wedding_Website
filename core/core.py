import pymysql.cursors
import logging
from os import getenv

def check_for_bundle_key(request):
    # Check for a user details
    if request.args.get('bundle'):
        bundle = request.args.get('bundle')
    elif request.cookies.get('bundle'):
        bundle = request.cookies.get('bundle')
    else:
        bundle = None

    return bundle
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
def get_all_bundle_ids():
    with db_connect().cursor() as cursor:
        try:
            cursor.execute("SELECT bundle_id FROM wedding.Bundle;")
            data = cursor.fetchall()
        except Exception as err:
            logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
            return False
    return [x['bundle_id'] for x in data]
def get_bundle_details(bundle_code):
    data=None
    with db_connect().cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM Bundle WHERE bundle_unique_id = '{bundle_code}';")
            data = cursor.fetchone()
        except Exception as err:
            logging.info(f"[*] Could not connect to the database: {err}", flush=True)
    return data if data else False
def get_bundle_from_person(person_id):
    with db_connect().cursor() as cursor:
        try:
            cursor.execute(f"SELECT bundle_id FROM People WHERE person_id = '{person_id}';")
            return cursor.fetchone()
        except Exception as err:
            logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return False
def get_config():
    with db_connect().cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM Configuration")
            data = cursor.fetchall()
        except Exception as err:
            logging.info(f"[*] Could not connect to the database: {err}", flush=True)

    return {item['Key']:item['Value'] for item in data} if data else False
def get_people(bundle):
    with db_connect().cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM People WHERE bundle_id = '{bundle['bundle_id']}'")
            data = cursor.fetchall()
        except Exception as err:
            data = None
            logging.debug(f"[*] Could not connect to the database: {err}", flush=True)

    return data if data else None
def get_people_string(bundle):
    data = get_people(bundle)
    string = ''
    flag = 0
    for person in data:
        flag=flag+1
        if flag == len(data):
            string = string + " & " + person['person_first']
        elif flag == 1:
            string=person['person_first']
        else:
            string = string + ", " + person['person_first']
    return string
def update_table(sql):
    with db_connect().cursor() as cursor:
        try:
            cursor.execute(sql)
            success = True
        except Exception as err:
            success = False
            logging.DEBUG(f"[*] Could not connect to the database: {err}", flush=True)

    return success