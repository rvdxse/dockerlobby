def format_bytes(b):
        if b is None or b < 0:
            return "N/A"
        b = float(b)
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
