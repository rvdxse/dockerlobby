from flask import Blueprint, render_template, jsonify, request, Response, current_app, stream_with_context
from functools import wraps
import json
import time

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

@bp.route('/events')
def events():
    app = current_app._get_current_object()
    max_iter = getattr(app, 'TEST_MODE_MAX_ITER', None)

    @stream_with_context
    def generate():
        count = 0
        while True:
            try:
                containers = app.container_manager.list_containers()
                yield f"data: {json.dumps(containers)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            count += 1
            if max_iter is not None and count >= max_iter:
                break

            time.sleep(3)

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

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
