import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pymysql
from datetime import date
from dotenv import load_dotenv
from utils import APIError, validate_json, json_response
import os

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'test')
DB_NAME = os.getenv('DB_NAME', 'library_db')
DB_PORT = int(os.getenv('DB_PORT', 3306))
print(DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT)
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


def get_conn(user=None, password=None):
    return pymysql.connect(host=DB_HOST, user=user or DB_USER, password=password or DB_PASS, db=DB_NAME, port=DB_PORT, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=False)


@app.errorhandler(APIError)
def handle_api_error(e):
    return jsonify({'error': e.message}), e.status_code


@app.route('/')
def index():
    return render_template('index.html')


# Readers CRUD
@app.route('/readers', methods=['GET', 'POST'])
def readers():
    if request.method == 'GET':
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM readers ORDER BY reader_id")
                return jsonify(cur.fetchall())
        finally:
            conn.close()

    data = request.json or {}
    validate_json({'name': str}, data)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO readers (name,address,gender,age,organization) VALUES (%s,%s,%s,%s,%s)",
                        (data['name'], data.get('address'), data.get('gender'), data.get('age'), data.get('organization')))
            conn.commit()
            return json_response({'msg': 'reader created'}, 201)
    except Exception as e:
        conn.rollback()
        raise APIError(str(e), 400)
    finally:
        conn.close()


@app.route('/readers/<int:reader_id>', methods=['GET', 'PUT', 'DELETE'])
def reader_detail(reader_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if request.method == 'GET':
                cur.execute("SELECT * FROM readers WHERE reader_id=%s", (reader_id,))
                r = cur.fetchone()
                if not r:
                    raise APIError('Reader not found', 404)
                return jsonify(r)

            if request.method == 'PUT':
                data = request.json or {}
                cur.execute("UPDATE readers SET name=%s,address=%s,gender=%s,age=%s,organization=%s WHERE reader_id=%s",
                            (data.get('name'), data.get('address'), data.get('gender'), data.get('age'), data.get('organization'), reader_id))
                conn.commit()
                return json_response({'msg': 'reader updated'})

            if request.method == 'DELETE':
                cur.execute("DELETE FROM readers WHERE reader_id=%s", (reader_id,))
                conn.commit()
                return json_response({'msg': 'reader deleted'})
    finally:
        conn.close()


# Books CRUD
@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'GET':
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM books ORDER BY book_id")
                return jsonify(cur.fetchall())
        finally:
            conn.close()

    data = request.json or {}
    validate_json({'title': str}, data)
    total = int(data.get('total_copies', 1))
    avail = int(data.get('available_copies', total))
    if avail > total:
        raise APIError('available_copies cannot exceed total_copies', 400)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO books (isbn,title,author,publisher,total_copies,available_copies) VALUES (%s,%s,%s,%s,%s,%s)",
                        (data.get('isbn'), data['title'], data.get('author'), data.get('publisher'), total, avail))
            conn.commit()
            return json_response({'msg': 'book created'}, 201)
    except Exception as e:
        conn.rollback()
        raise APIError(str(e), 400)
    finally:
        conn.close()


@app.route('/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
def book_detail(book_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if request.method == 'GET':
                cur.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
                b = cur.fetchone()
                if not b:
                    raise APIError('Book not found', 404)
                return jsonify(b)

            if request.method == 'PUT':
                data = request.json or {}
                cur.execute("UPDATE books SET isbn=%s,title=%s,author=%s,publisher=%s,total_copies=%s,available_copies=%s WHERE book_id=%s",
                            (data.get('isbn'), data.get('title'), data.get('author'), data.get('publisher'), data.get('total_copies'), data.get('available_copies'), book_id))
                conn.commit()
                return json_response({'msg': 'book updated'})

            if request.method == 'DELETE':
                cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
                conn.commit()
                return json_response({'msg': 'book deleted'})
    finally:
        conn.close()


# Borrow and Return
@app.route('/borrow', methods=['POST'])
def borrow():
    data = request.json or {}
    validate_json({'reader_id': int, 'book_id': int, 'due_date': str}, data)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("CALL BorrowBook(%s,%s,%s,%s)", (data['reader_id'], data['book_id'], data.get('borrow_date', date.today()), data['due_date']))
        conn.commit()
        return json_response({'msg': 'borrowed'})
    except Exception as e:
        conn.rollback()
        raise APIError(str(e), 400)
    finally:
        conn.close()


@app.route('/return', methods=['POST'])
def ret():
    data = request.json or {}
    validate_json({'loan_id': int, 'return_date': str}, data)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("CALL ReturnBook(%s,%s)", (data['loan_id'], data['return_date']))
        conn.commit()
        return json_response({'msg': 'returned'})
    except Exception as e:
        conn.rollback()
        raise APIError(str(e), 400)
    finally:
        conn.close()


@app.route('/loans', methods=['GET'])
def loans():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT l.*, b.title, r.name as reader_name FROM loans l JOIN books b ON l.book_id=b.book_id JOIN readers r ON l.reader_id=r.reader_id ORDER BY l.created_at DESC")
            return jsonify(cur.fetchall())
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
