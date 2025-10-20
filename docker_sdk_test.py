import docker
def format_bytes(b):
    """Преобразует байты в KiB, MiB, GiB и т.д."""
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
    """Расчитывает использование RAM и лимит."""
    mem_usage = stats['memory_stats']['usage']
    # Для получения реального использования RAM вычитаем кэш (как в `docker stats`)
    mem_cache = stats['memory_stats'].get('stats', {}).get('cache', 0)
    
    real_mem_usage = mem_usage - mem_cache
    mem_limit = stats['memory_stats']['limit']

    if mem_limit == 0: # 0 означает отсутствие лимита, используем значение хоста
        mem_limit = None
    
    return {
        'usage': format_bytes(real_mem_usage),
        'limit': format_bytes(mem_limit),
    }

# --- Основной код ---

client = docker.from_env()
containers = client.containers.list(all=True)

print(f"{'Контейнер':<26} | {'Статус':<10} | {'CPU %':<10} | {'RAM (Использовано / Лимит)':<30}")
print("-" * 75)
for c in containers:
    cpu_info = "N/A"
    mem_info = "N/A / N/A"
    
    if c.status == 'running':
        try:
            # Получаем моментальный снимок статистики. stream=False обязателен!
            stats = c.stats(stream=False)
            
            # Расчет CPU
            cpu_info = calculate_cpu_percent(stats)
            
            # Расчет RAM
            mem_data = calculate_mem_usage(stats)
            mem_info = f"{mem_data['usage']} / {mem_data['limit']}"

        except Exception as e:
            # c.stats() может вызвать ошибку, если контейнер только что запустился/остановился
            pass 
            
    print(f"{c.name:<20} | {c.status:<10} | {cpu_info:<10} | {mem_info:<30}")
