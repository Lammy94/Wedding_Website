import pymysql.cursors
import logging
from os import getenv

def check_for_bundle_key(request):
    """
    function to check for a bundle id
    """
    # Check for a bundle id in the request arguments
    if request.args.get('bundle'):
        bundle = request.args.get('bundle')
    # if that does not exist, check in the browser cookies
    elif request.cookies.get('bundle'):
        bundle = request.cookies.get('bundle')
    # else, the user hasnt yet set a bundle id
    else:
        bundle = None

    # return the result
    return bundle
def db_connect():
    # base function to connect to the database
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
    """
    function to get a list of bundle_ids from the database
    """

    # with a db connection open
    with db_connect().cursor() as cursor:
        try:
            # execute the sql query, fetch all records
            cursor.execute("SELECT bundle_id FROM wedding.Bundle;")
            data = cursor.fetchall()
        except Exception as err:
            logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
            return False

    # return a list of just the bundle_ids
    return [x['bundle_id'] for x in data]

def get_bundle_details(bundle_code):
    """
    function to get information surrounding a bundle. 
    """
    # default to no data
    data=None

    # with a db connection open
    with db_connect().cursor() as cursor:
        try:
            # execute the sql query, fetch only the first available record
            cursor.execute(f"SELECT * FROM Bundle WHERE bundle_unique_id = '{bundle_code}';")
            data = cursor.fetchone()
        except Exception as err:
            logging.info(f"[*] Could not connect to the database: {err}", flush=True)

    # return the data if it was found, else return false
    return data if data else False
def get_bundle_from_person(person_id):
    """
    function to match a person to their bundle
    """
        # with a db connection open
    with db_connect().cursor() as cursor:
        try:
            # execute the sql query, fetch one record 
            # (each person can only be a member of one bundle)
            cursor.execute(f"SELECT bundle_id FROM People WHERE person_id = '{person_id}';")
            return cursor.fetchone()
        except Exception as err:
            logging.debug(f"[*] Could not connect to the database: {err}", flush=True)
        return False
def get_config():
    """
    Function to get the configuration table
    """
    with db_connect().cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM Configuration")
            data = cursor.fetchall()
        except Exception as err:
            logging.info(f"[*] Could not connect to the database: {err}", flush=True)

    # turn the returned data into a key:value dictionary instead of a list of key:values.

    return {item['Key']:item['Value'] for item in data} if data else False
def get_people(bundle):
    """
    Function to get all people from a bundle based on the bundle id
    """
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
    """
    Function to update tables in the database,
    query passed in from function call for higher flexibility 
    """
    with db_connect().cursor() as cursor:
        try:
            cursor.execute(sql)
            success = True
        except Exception as err:
            success = False
            logging.DEBUG(f"[*] Could not connect to the database: {err}", flush=True)

    return success