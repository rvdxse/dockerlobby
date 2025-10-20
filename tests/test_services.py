import pytest
from unittest.mock import MagicMock
from app.services import DockerManager

@pytest.fixture
def mock_client():
    client = MagicMock()
    return client

def test_get_image_name_with_tags(mock_client):
    container = MagicMock()
    container.image.tags = ["ubuntu:latest"]
    manager = DockerManager(mock_client)
    assert manager._get_image_name(container) == "ubuntu:latest"

def test_get_image_name_no_tags(mock_client):
    container = MagicMock()
    container.image.tags = []
    container.image.short_id = "abc123"
    manager = DockerManager(mock_client)
    assert manager._get_image_name(container) == "abc123"

def test_list_containers_basic(mock_client):
    c = MagicMock()
    c.id = "123"
    c.short_id = "abc"
    c.name = "test"
    c.status = "running"
    c.attrs = {"Created": "now"}
    c.image.tags = ["ubuntu:latest"]
    mock_client.containers.list.return_value = [c]

    manager = DockerManager(mock_client)
    result = manager.list_containers()
    assert isinstance(result, list)
    assert result[0]["name"] == "test"

def test_start_stop(mock_client):
    c = MagicMock()
    mock_client.containers.get.return_value = c
    manager = DockerManager(mock_client)

    manager.start_container("123")
    c.start.assert_called_once()

    manager.stop_container("123")
    c.stop.assert_called_once()

def test_get_container_details(mock_client):
    c = MagicMock()
    del c.labels  
    c.id = "1"
    c.name = "demo"
    c.status = "running"
    c.image.tags = ["ubuntu"]
    c.attrs = {"Created": "yesterday", "Config": {"Labels": {"env": "prod"}}}
    mock_client.containers.get.return_value = c

    manager = DockerManager(mock_client)
    details = manager.get_container_details("1")
    assert details["name"] == "demo"
    assert "env" in details["labels"]


    manager = DockerManager(mock_client)
    details = manager.get_container_details("1")
    assert details["name"] == "demo"
    assert "env" in details["labels"]

def test_get_container_logs(mock_client):
    c = MagicMock()
    c.logs.return_value = b"hello world"
    mock_client.containers.get.return_value = c

    manager = DockerManager(mock_client)
    logs = manager.get_container_logs("1")
    assert "hello" in logs
