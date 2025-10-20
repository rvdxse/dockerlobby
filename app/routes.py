from flask import Blueprint, render_template, jsonify, request, Response
import docker
from datetime import datetime
from functools import wraps

bp = Blueprint('main', __name__)
client = docker.from_env()

@bp.route("/")
def index():
    return render_template('index.html')

@bp.route("/data")
def data():
    containers = client.containers.list(all=True)
    out = []
    for c in containers:
        try:
            image = None
            try:
                if c.image and getattr(c.image, "tags", None):
                    image = c.image.tags[0] if c.image.tags else c.image.short_id
                else:
                    image = c.image.short_id
            except Exception:
                image = None
            created = None
            try:
                created = c.attrs.get('Created')
            except Exception:
                created = None

            out.append({
                'id': c.id,
                'short_id': c.short_id,
                'name': c.name,
                'status': c.status,
                'image': image,
                'created': created
            })
        except Exception:
            continue
    return jsonify(out)

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

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

@bp.route("/start/<cid>", methods=["POST"])
@requires_auth
def start_container(cid):
    try:
        client.containers.get(cid).start()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route("/stop/<cid>", methods=["POST"])
@requires_auth
def stop_container(cid):
    try:
        client.containers.get(cid).stop()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@bp.route("/inspect/<cid>")
def inspect_container(cid):
    try:
        c = client.containers.get(cid)
        attrs = {
            'id': c.id,
            'name': c.name,
            'status': c.status,
            'image': c.image.tags[0] if getattr(c.image, 'tags', None) and c.image.tags else getattr(c.image, 'short_id', None),
            'created': c.attrs.get('Created'),
            'labels': c.labels if hasattr(c, 'labels') else c.attrs.get('Config', {}).get('Labels', {})
        }
        return jsonify(attrs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/logs/<cid>")
def logs(cid):
    try:
        c = client.containers.get(cid)
        text = c.logs(tail=500).decode('utf-8', errors='replace')
        return text
    except Exception as e:
        return str(e), 500
