import json
import time
from abc import abstractmethod

import requests

from .BaseHandler import BaseHandler


class BaseMissionHandler(BaseHandler):
    def set_status(self, status: int):
        self.context.mission.status = status
        self.drop_triggers()

    def drop_triggers(self):
        self.context.mission.triggers.start_mission_trigger = False
        self.context.mission.triggers.stop_mission_trigger = False
        self.context.mission.triggers.reset_mission_trigger = False

    @staticmethod
    def _continue():
        return "C"

    @staticmethod
    def _pass():
        return "P"

    @abstractmethod
    def process_status_idle(self, mission):
        if self.context.mission.triggers.start_mission_trigger:
            cyb_config = self.send_robot_request("get_cybs", pass_response=True)
            if cyb_config.get("content", None) is not None:
                mission.mission_uid = self.context.system.gen_uid(6)
                self.context.lg.add_to_batch("")
                self.context.lg.add_to_batch("")
                self.context.lg.add_to_batch("")
                self.context.lg.flush_batch()
                self.set_status(1)
                mission.init_mission(cyb_config["content"])
                self.context.mission.panel_mission_data.events.append(
                    {"m_type": 1, "message": f"Заезд ({mission.mission_uid}): запущен"}
                )
                self.context.lg.log(f"Заезд ({mission.mission_uid}): запущен")
                self.drop_triggers()
                return self._continue()
            else:
                self.context.lg.error("Среда выполнения не инициализирована или информация об активации КП не передана")
                self.drop_triggers()
        return self._pass()

    @abstractmethod
    def process_status_running(self, mission):
        if mission.triggers.stop_mission_trigger:
            self.set_status(2)
            mission.panel_mission_data.events.append(
                {"m_type": 1, "message": f"Заезд ({mission.mission_uid}): остановлен - по внешней команде"}
            )
            self.context.lg.log(f"Заезд ({mission.mission_uid}): остановлен - по внешней команде")
            self.drop_triggers()
            return self._continue()

        if self.context.mission.triggers.reset_mission_trigger:
            self.set_status(2)
            self.set_status(0)
            self.context.mission.panel_mission_data = self.context.mission.reset_panel_data()
            self.context.lg.log(f"Заезд ({mission.mission_uid}): завершён и сохранён")
            self.context.lg.log("Возможно начать новый заезд")
            self.drop_triggers()
            return self._continue()

        if mission.check_timer():
            self.set_status(2)
            self.context.mission.panel_mission_data.events.append(
                {
                    "m_type": 1,
                    "message": f"Заезд ({mission.mission_uid}): остановлен - по истечении времени",
                }
            )
            self.context.lg.log(f"Заезд ({mission.mission_uid}): остановлен - по истечении времени")
            self.drop_triggers()
            return self._continue()
        return self._pass()

    @abstractmethod
    def process_status_stopped(self, mission):
        if mission.triggers.reset_mission_trigger:
            self.set_status(0)
            self.context.mission.panel_mission_data = self.context.mission.reset_panel_data()
            self.context.lg.log(f"Заезд ({mission.mission_uid}): завершён и сохранён")
            self.context.lg.log("Возможно начать новый заезд")
            return self._continue()

        return self._pass()

    def run(self):
        mission = self.context.mission
        self.set_status(0)
        while True:
            time.sleep(0.01)

            if self.context.mission.status == 0:
                r = self.process_status_idle(mission)
                if r == "C":
                    continue

            if self.context.mission.status == 1:
                r = self.process_status_running(mission)
                if r == "C":
                    continue

            if self.context.mission.status == 2:
                r = self.process_status_stopped(mission)
                if r == "C":
                    continue

    def send_robot_request(self, method, pass_response=False):
        result = {} if pass_response else False
        try:
            req = requests.post(
                f"http://{self.context.robots.current_robot.ip_address}:13500/{method}",
                timeout=1,
            )
            if req.status_code == 200:
                response = json.loads(req.text)
                if pass_response:
                    response = json.loads(req.text)
                    result = response
                else:
                    if response["status"] == "OK":
                        result = True
        except Exception as e:
            if "timeout" in str(e):
                self.context.lg.error(f"Ошибка отправки команды: робот не отвечает")
        return result
