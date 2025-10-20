import pytest
from app.utils import format_bytes, calculate_cpu_percent, calculate_mem_usage

def test_format_bytes_basic():
    assert format_bytes(1024) == "1.00 KiB"
    assert format_bytes(0) == "0.00 B"
    assert format_bytes(1048576) == "1.00 MiB"

def test_format_bytes_invalid():
    assert format_bytes(None) == "N/A"
    assert format_bytes(-10) == "N/A"

def test_calculate_cpu_percent():
    stats = {
        "cpu_stats": {
            "cpu_usage": {"total_usage": 2000},
            "system_cpu_usage": 4000,
            "online_cpus": 2
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 1000},
            "system_cpu_usage": 2000
        }
    }
    result = calculate_cpu_percent(stats)
    assert result.endswith("%")
    assert float(result.strip("%")) > 0

def test_calculate_mem_usage():
    stats = {
        "memory_stats": {
            "usage": 4096,
            "limit": 8192,
            "stats": {"cache": 1024}
        }
    }
    res = calculate_mem_usage(stats)
    assert "usage" in res and "limit" in res
    assert "B" in res["usage"]
    assert "B" in res["limit"]