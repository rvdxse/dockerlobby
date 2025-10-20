from flask import Blueprint, render_template, jsonify, request, Response, current_app
from functools import wraps

bp = Blueprint('main', __name__)

def check_auth(username, password):
    config = current_app.config
    return (username == config.get('BASIC_AUTH_USERNAME') and 
            password == config.get('BASIC_AUTH_PASSWORD'))

def authenticate():
    return Response('Please provide valid credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated



@bp.route("/")
def index():
    return render_template('index.html')

@bp.route("/data")
def data():
    try:
        out = current_app.container_manager.list_containers()
        return jsonify(out)
    except Exception as e:
        return jsonify({'ok': False, 'error': "Docker service error: " + str(e)}), 500

@bp.route("/start/<cid>", methods=["POST"])
@requires_auth
def start_container(cid):
    try:
        current_app.container_manager.start_container(cid)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route("/stop/<cid>", methods=["POST"])
@requires_auth
def stop_container(cid):
    try:
        current_app.container_manager.stop_container(cid)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route("/inspect/<cid>")
def inspect_container(cid):
    try:
        attrs = current_app.container_manager.get_container_details(cid)
        return jsonify(attrs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/logs/<cid>")
def logs(cid):
    try:
        text = current_app.container_manager.get_container_logs(cid)
        return Response(text, mimetype='text/plain')
    except Exception as e:
        return str(e), 500
