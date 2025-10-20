from app import create_app

def test_create_app_basic():
    app = create_app()
    assert app is not None
    assert hasattr(app, "container_manager")
