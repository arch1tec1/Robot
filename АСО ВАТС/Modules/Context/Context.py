import configparser
import os

from openlog import Logger

import const as c
from .Common import ArgParser, System, Robots, Field
from .Missions import ChvtMission, LctMission
from .SDPStores import ChvtSPDSet, LctSPDSet


class Context:
    def __init__(self, init_ok: bool):
        self.init_ok = init_ok

        self.config = Config(self)
        self.lg = Logger(
            write_to_file=not bool(self.config.get("general", "short_timestamps")),
            in_dir=True,
            session=True,
            short_timestamp=bool(self.config.get("general", "short_timestamps")),
        )
        self.system = System(self)

        self.args = ArgParser(self)

        self.field = Field()
        self.robots = Robots(self)

        if c.MISSION_MODE == "chvt":
            self.mission = ChvtMission(self)
            self.spd = ChvtSPDSet(self)
        elif c.MISSION_MODE == "lct":
            self.mission = LctMission(self)
            self.spd = LctSPDSet(self)
        else:
            self.lg.error("Неверный режим миссии! Работа невозможна.")


class Config:
    def __init__(self, context: Context):
        self.context = context
        config = configparser.ConfigParser()
        if os.path.getsize(os.path.dirname(os.path.abspath(__file__)) + "/../../config.ini") < 20:
            context.lg.error("config.ini повреждён или недоступен.")
            self.context.init_ok = False
            return
        config.read(os.path.dirname(os.path.abspath(__file__)) + "/../../config.ini")
        self.config = config

    def get(self, section: str, key: str):
        try:
            if self.config[section][key] is not None:
                try:
                    val = int(self.config[section][key])
                    if val == 0 or val == 1:
                        return bool(val)
                    else:
                        return val
                except:
                    try:
                        val = float(self.config[section][key])
                        return val
                    except:
                        return self.config[section][key]
            else:
                raise ValueError("Couldn't find '" + key + "' in '" + section + "'")
        except:
            raise ValueError("Couldn't find '" + key + "' in '" + section + "'")

    def set(self, section: str, key: str, value):
        self.config.set(section, key, value)
        config_file = open(os.path.dirname(os.path.abspath(__file__)) + "/../../config.ini", "w")
        self.config.write(config_file)
