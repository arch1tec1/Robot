import json
import requests
import time
from abc import abstractmethod, ABC
from dataclasses import dataclass
from threading import Thread

import const as c


@dataclass
class PanelData:
    competitor_id: str
    time_elapsed: str
    mission_id: str
    mission_status: int
    events: list[dict[str, str]]
    sec_domains: dict[str, str]
    sec_targets: dict[str, str]


class BaseMission(ABC):
    def __init__(self, context):
        self.update_running = None
        self.context = context

        # 0 - не начат, 1 - запущен, 3 - завершён (автоматический), 4 - завершён (ручной)
        self.status = 0
        self.mission_uid = None
        self.competitor_uid = None
        self.time_start = 0

        self.mission_tasks = {}
        self.mission_vars = {}
        self.cybs = {}
        self.cyb_status = {}

        self.timeouts = {}

        self.panel_mission_data = PanelData("---", "--:--", "-----", 0, [], {}, {})
        self.last_competitor_id = None

        self.triggers = Triggers(context)

        Thread(target=self.send_panel_data, daemon=True).start()
        Thread(target=self.send_mission_status, daemon=True).start()

    @staticmethod
    @abstractmethod
    def reset_panel_data():
        raise NotImplementedError("Subclasses should implement this method.")

    def send_panel_data(self):
        pass

    def send_robot_request(self, method, data=None, pass_response=False, silent=False):
        if data is None:
            data = {}
        result = {} if pass_response else False
        try:
            req = requests.post(
                f"http://{self.context.robots.current_robot.ip_address}:13500/{method}",
                json=json.dumps(data),
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
            if not silent:
                if "timeout" in str(e):
                    self.context.lg.error(f"Ошибка отправки команды: робот не отвечает")
        return result

    def check_timer(self):
        elapsed_time = time.time() - self.time_start
        return elapsed_time >= c.MISSION_TIME_LIMIT

    @abstractmethod
    def init_mission(self, cybs):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def update_polygon_state(self):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def update_cybs_state(self):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def make_actions(self):
        raise NotImplementedError("Subclasses must implement this method")

    def begin_mission_update(self):
        self.update_running = True
        self.make_actions()
        Thread(target=self.do_mission_update, daemon=True).start()

    def check_robot_in_zones(self, zones, frame=True):
        if frame:
            ccf = self.context.robots.current_robot.current_cell_frame
        else:
            ccf = self.context.robots.current_robot.current_cell_point
        for zone in zones:
            if ccf == zone:
                return True
        return False

    def do_mission_update(self):
        while self.update_running:
            time.sleep(0.02)
            self.update_polygon_state()
            self.update_cybs_state()

            for timeout, callback in list(self.timeouts.items()):
                if time.time() >= timeout:
                    self.timeouts.pop(timeout)
                    if callback:
                        if not callback():
                            self.once(1, callback)
                    else:
                        self.context.lg.error("Ошибка выполнения миссии.")

            if self.status != 1:
                self.update_running = False

    def once(self, duration: int = 0, callback=None):
        self.timeouts[time.time() + duration] = callback

    def send_mission_status(self):
        while True:
            self.send_robot_request(
                "set_status",
                {"status": self.status, "cyb_status": self.cyb_status, "mission_vars": self.mission_vars},
                pass_response=False,
                silent=True,
            )
            time.sleep(0.3)


class Triggers:
    def __init__(self, context):
        self.context = context

        self.start_mission_trigger = False
        self.stop_mission_trigger = False
        self.reset_mission_trigger = False
        self.reset_twin_trigger = False
        self.begin_trigger = False
