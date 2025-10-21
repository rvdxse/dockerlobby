import pytest
from unittest.mock import MagicMock, patch
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.testing = True

    mock_manager = MagicMock()
    mock_manager.list_containers.return_value = []
    mock_manager.get_container_details.return_value = {"id": "1", "name": "demo", "status": "running", "image": "ubuntu", "created": "today", "labels": {}}
    mock_manager.get_container_logs.return_value = "log output"
    app.container_manager = mock_manager
    app.config['BASIC_AUTH_USERNAME'] = 'admin'
    app.config['BASIC_AUTH_PASSWORD'] = 'password'
    return app.test_client()

def test_index_route(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"html" in resp.data or b"HTML" in resp.data

def test_data_route(client):
    resp = client.get('/data')
    assert resp.status_code == 200
    assert resp.is_json
    assert isinstance(resp.get_json(), list)

def test_start_stop_routes_auth(client):
    # Без авторизации
    resp = client.post('/start/123')
    assert resp.status_code == 401

    resp = client.post('/stop/123')
    assert resp.status_code == 401

    # С авторизацией
    headers = {"Authorization": "Basic YWRtaW46cGFzc3dvcmQ="}
    resp = client.post('/start/123', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True

    resp = client.post('/stop/123', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True

def test_inspect_route(client):
    resp = client.get('/inspect/123')
    assert resp.status_code == 200
    data = resp.get_json()
    assert "id" in data
    assert data["name"] == "demo"

def test_logs_route(client):
    resp = client.get('/logs/123')
    assert resp.status_code == 200
    assert b"log output" in resp.data

def test_events_route(client):
    import json

    app = client.application
    app.TEST_MODE_MAX_ITER = 3
    resp = client.get('/events', buffered=True)
    assert resp.status_code == 200
    assert resp.headers['Content-Type'].startswith('text/event-stream')

    first_chunk = resp.response[0] 
    if isinstance(first_chunk, bytes):
        first_chunk = first_chunk.decode()
    data_json = json.loads(first_chunk.replace("data: ", ""))
    assert isinstance(data_json, list)

