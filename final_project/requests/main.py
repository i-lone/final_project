import datetime as dt
import json
import psycopg2
import requests
from flask import Flask, jsonify, request
from datetime import datetime

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = ""
# you can get API keys for free here - https://api-ninjas.com/api/jokes
RSA_KEY = ""

app = Flask(__name__)


def database_credentials():
    return psycopg2.connect(database="project",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def register_user(username, password):
    success = False
    conn = database_credentials()
    cursor = conn.cursor()
    cursor.execute("SELECT * from users WHERE username = '{0}'".format(username))
    if not cursor.rowcount:
        cursor.execute(f'INSERT INTO users (username, password) VALUES (%s, %s)',
                       (username, password))
        success = True
    conn.commit()
    cursor.close()
    conn.close()
    return success


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>We are reserving books.</h2></p>"


@app.route("/login", methods=["POST"])
def login():
    json_data = request.get_json()

    if json_data.get("username") is None:
        raise InvalidUsage("username is required", status_code=400)

    username = json_data.get("username")

    if json_data.get("password") is None:
        raise InvalidUsage("password is required", status_code=400)

    password = json_data.get("password")

    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("SELECT * from users WHERE username = '{0}'".format(username))
    if not cursor.rowcount:
        raise InvalidUsage("user not found", status_code=400)
    result = cursor.fetchall()[0]
    conn.commit()
    cursor.close()
    conn.close()
    if result is not None:
        if str(result[2]) == str(password):
            response_json = {
                "login": "true",
                "user_id": result[0],
                "username": result[1]
            }
        else:
            raise InvalidUsage("wrong password", status_code=400)
    else:
        raise InvalidUsage("user not found", status_code=400)
    return response_json


@app.route("/register", methods=["POST"])
def register():
    json_data = request.get_json()

    if json_data.get("username") is None:
        raise InvalidUsage("username is required", status_code=400)

    username = json_data.get("username")

    if json_data.get("password") is None:
        raise InvalidUsage("password is required", status_code=400)

    password = json_data.get("password")

    success = register_user(username, password)
    if success:
        conn = database_credentials()
        cursor = conn.cursor()
        cursor.execute("SELECT * from users WHERE username = '{0}'".format(username))
        if not cursor.rowcount:
            raise InvalidUsage("user not found", status_code=400)
        result = cursor.fetchall()[0]
        conn.commit()
        cursor.close()
        conn.close()
        if result is not None:
            if result[2] == password:
                response_json = {
                    "registration": "true",
                    "user_id": result[0],
                    "username": result[1]
                }
            else:
                raise InvalidUsage("registration failed", status_code=400)
        else:
            raise InvalidUsage("registration failed", status_code=400)
    else:
        raise InvalidUsage("user already exist", status_code=400)
    return response_json


@app.route("/search", methods=["GET"])
def search():
    json_data = request.get_json()

    if json_data.get("title") is None:
        raise InvalidUsage("username is required", status_code=400)

    title = json_data.get("title")

    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("SELECT * from books WHERE title = '{0}'".format(title))
    if not cursor.rowcount:
        raise InvalidUsage("books not found", status_code=400)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    response_json = {}
    if result is not None:
        for i in range(len(result)):
            response_json[i] = {
                "id": result[i][0],
                "title": result[i][1],
                "author": result[i][2],
                "year": result[i][3],
                "publisher": result[i][4],
                "city": result[i][5],
                "reserved_by": result[i][6]
            }
    else:
        raise InvalidUsage("books not found", status_code=400)
    return response_json


@app.route("/reserve", methods=["POST"])
def reserve_book():
    json_data = request.get_json()
    response_json = {}
    if json_data.get("book_id") is None:
        raise InvalidUsage("book id is required", status_code=400)

    book_id = json_data.get("book_id")

    if json_data.get("user_id") is None:
        raise InvalidUsage("user id is required", status_code=400)

    user_id = json_data.get("user_id")

    conn = database_credentials()
    cursor = conn.cursor()
    cursor.execute("SELECT * from books WHERE id = '{0}'".format(book_id))
    if cursor.rowcount:
        if cursor.fetchall()[0][6] is None:
            cursor.execute("SELECT * from users WHERE id = '{0}'".format(user_id))
            if cursor.rowcount:
                cursor.execute(
                    'UPDATE books SET reserved_by = %s WHERE id = %s',
                    (user_id, book_id))
                conn.commit()
                cursor.close()
                conn.close()
                response_json = {
                    "success": "true"
                }
            else:
                raise InvalidUsage("user not found", status_code=400)
        else:
            raise InvalidUsage("book is already reserved by someone", status_code=400)
    else:
        raise InvalidUsage("book not found", status_code=400)
    return response_json


@app.route("/return", methods=["POST"])
def return_book():
    json_data = request.get_json()
    response_json = {}
    if json_data.get("book_id") is None:
        raise InvalidUsage("book id is required", status_code=400)

    book_id = json_data.get("book_id")

    if json_data.get("user_id") is None:
        raise InvalidUsage("user id is required", status_code=400)

    user_id = json_data.get("user_id")
    conn = database_credentials()
    cursor = conn.cursor()
    cursor.execute("SELECT * from books WHERE id = '{0}'".format(book_id))

    if cursor.rowcount:
        result = cursor.fetchall()[0]
        if (result[6] is not None) and (str(result[6]) == str(user_id)):
            cursor.execute(
                'UPDATE books SET reserved_by = null WHERE id = {0}'.format(book_id))
            conn.commit()
            cursor.close()
            conn.close()
            response_json = {
                "success": "true"
            }
        elif result[6] is not None:
            raise InvalidUsage("book is reserved by someone else", status_code=400)
        else:
            raise InvalidUsage("book is already returned", status_code=400)
    else:
        raise InvalidUsage("book is not found", status_code=400)
    return response_json


@app.route("/user", methods=["GET"])
def get_reserved_books():
    json_data = request.get_json()
    response_json = {}

    if json_data.get("user_id") is None:
        raise InvalidUsage("user id is required", status_code=400)

    user_id = json_data.get("user_id")
    conn = database_credentials()
    cursor = conn.cursor()
    cursor.execute("SELECT * from users WHERE id = '{0}'".format(user_id))

    if cursor.rowcount:
        cursor.execute("SELECT * from books WHERE reserved_by = '{0}'".format(user_id))
        if not cursor.rowcount:
            raise InvalidUsage("books not found", status_code=400)
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        response_json = {}
        if result is not None:
            for i in range(len(result)):
                response_json[i] = {
                    "id": result[i][0],
                    "title": result[i][1],
                    "author": result[i][2],
                    "year": result[i][3],
                    "publisher": result[i][4],
                    "city": result[i][5],
                    "reserved_by": result[i][6]
                }
        else:
            raise InvalidUsage("books not found", status_code=400)
    else:
        raise InvalidUsage("user not found", status_code=400)
    return response_json
