import os

import psutil


def get_stats():
    disk_path = "C:\\" if os.name == "nt" else "/"
    try:
        disk = psutil.disk_usage(disk_path).percent
    except OSError:
        disk = 0.0
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": disk,
    }
