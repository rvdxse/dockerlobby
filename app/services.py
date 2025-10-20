import docker
from datetime import datetime
from .utils import calculate_cpu_percent, calculate_mem_usage

class DockerManager:
    def __init__(self, client):
        self.client = client

    def _get_image_name(self, container):
        try:
            if container.image and getattr(container.image, "tags", None) and container.image.tags:
                return container.image.tags[0]
            else:
                return container.image.short_id
        except Exception:
            return None
    
    def list_containers(self):
        containers = self.client.containers.list(all=True)
        out = []
        for c in containers:
            try:
                image = self._get_image_name(c)
                created = c.attrs.get('Created')
                
                cpu_percent = "N/A"
                mem_info = "N/A"

                if c.status == 'running':
                    try:
                        stats = self.client.containers.get(c.id).stats(stream=False)
                        cpu_percent = calculate_cpu_percent(stats)
                        mem_data = calculate_mem_usage(stats)
                        mem_info = f"{mem_data['usage']} / {mem_data['limit']}"
                    except Exception as e:
                        print(f"Error fetching stats for {c.name}: {e}")
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
            except Exception as ex:
                print(f"Error processing container {c.id}: {ex}")
                continue
        return out

    def start_container(self, cid):
        self.client.containers.get(cid).start()
        
    def stop_container(self, cid):
        self.client.containers.get(cid).stop()

    def get_container_details(self, cid):
        c = self.client.containers.get(cid)
        return {
            'id': c.id,
            'name': c.name,
            'status': c.status,
            'image': self._get_image_name(c),
            'created': c.attrs.get('Created'),
            'labels': c.labels if hasattr(c, 'labels') else c.attrs.get('Config', {}).get('Labels', {})
        }

    def get_container_logs(self, cid, tail=500):
        c = self.client.containers.get(cid)
        return c.logs(tail=tail).decode('utf-8', errors='replace')
