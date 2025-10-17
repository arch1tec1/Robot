import os
import random
import string
import threading
from functools import wraps

import const as c


def run_in_thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
            thread.start()
            return thread
        except Exception as e:
            print(f"Ошибка при обработке: {e}")
            return None

    return wrapper


def get_zone(zone):
    return c.FIELD_SCHEMA["zones"].get(zone, None)


def get_service_zone(zone):
    return c.FIELD_SCHEMA["service_zones"].get(zone, None)


def gen_uid(length):
    letters = string.ascii_lowercase + string.ascii_uppercase
    return "".join(random.choice(letters) for i in range(length))


def get_points_range(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x2 - x1), abs(y2 - y1)


def hard_reboot():
    os.system("sudo reboot")


def app_restart():
    os.system("pm2 restart all")
