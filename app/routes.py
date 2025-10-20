from flask import Blueprint, render_template, jsonify, request, Response
import docker
from datetime import datetime
from functools import wraps

def format_bytes(b):
    if b is None or b < 0:
        return "N/A"
    for unit in ['B', 'KiB', 'MiB', 'GiB']:
        if b < 1024.0:
            return f"{b:3.2f} {unit}"
        b /= 1024.0
    return f"{b:3.2f} TiB"

def calculate_cpu_percent(stats):
    cpu_percent = 0.0
    cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
    system_cpu_usage = stats['cpu_stats']['system_cpu_usage']
    online_cpus = stats['cpu_stats'].get('online_cpus', 0)
    
    precpu_usage = stats['precpu_stats']['cpu_usage']['total_usage']
    psystem_cpu_usage = stats['precpu_stats']['system_cpu_usage']

    cpu_delta = cpu_usage - precpu_usage
    system_delta = system_cpu_usage - psystem_cpu_usage

    if system_delta > 0.0 and cpu_delta > 0.0:
        cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0
        
    return f"{cpu_percent:3.2f}%"

def calculate_mem_usage(stats):
    mem_usage = stats['memory_stats']['usage']
    mem_cache = stats['memory_stats'].get('stats', {}).get('cache', 0)
    
    real_mem_usage = mem_usage - mem_cache
    mem_limit = stats['memory_stats']['limit']

    if mem_limit == 0:
        mem_limit = None
    
    return {
        'usage': format_bytes(real_mem_usage),
        'limit': format_bytes(mem_limit),
    }

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
            cpu_percent = "N/A"
            mem_usage = "N/A / N/A"
            if c.status == 'running':
                try:
                    stats = c.stats(stream=False)
                    cpu_percent = calculate_cpu_percent(stats)
                    mem_data = calculate_mem_usage(stats)
                    mem_info = f"{mem_data['usage']} / {mem_data['limit']}"
                except Exception as e:
                    pass

            out.append({
                'id': c.id,
                'short_id': c.short_id,
                'name': c.name,
                'status': c.status,
                'image': image,
                'created': created,
                'cpu_percent': cpu_percent,
                'mem_usage': mem_info
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
