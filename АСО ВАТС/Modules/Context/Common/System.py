import os
import random
import string


class System:
    def __init__(self, context):
        self.context = context

    @staticmethod
    def gen_uid(length):
        letters = string.ascii_lowercase + string.ascii_uppercase
        return "".join(random.choice(letters) for i in range(length))

    @staticmethod
    def hard_reboot():
        os.system("sudo reboot")

    @staticmethod
    def app_restart():
        os.system("pm2 restart all")
