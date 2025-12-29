import os
import pytest
from app import app
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_readers(client):
    res = client.get('/readers')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)


def test_create_reader(client):
    res = client.post('/readers', json={'name': '测试用户', 'age': 30})
    assert res.status_code == 201
    assert res.get_json().get('msg') == 'reader created'


def test_create_book(client):
    res = client.post('/books', json={'title': '测试书籍', 'total_copies': 1, 'available_copies': 1})
    assert res.status_code == 201
    assert res.get_json().get('msg') == 'book created'
