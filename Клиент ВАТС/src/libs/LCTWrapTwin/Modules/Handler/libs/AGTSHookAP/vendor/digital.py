import json
import random
import socket

import requests

from src.libs.LCTWrapTwin.Modules import BaseUDPSendHandler


class UDPDigitalDriver(BaseUDPSendHandler):
    def __init__(self, context, address, port, root):
        super().__init__(context, address, port, 0.02)
        self.controls = {"x": 0, "y": 0, "r": 0}
        self.root = root

    def set_controls(self, data=None):
        if data is None:
            data = {}
        if self.context.mission.mission_vars.get("burn_electric_schemes", False):
            data = {"x": 0, "y": 0, "r": 0}
        if data.get("x") is not None:
            self.controls["x"] = data["x"]
        if data.get("y") is not None:
            self.controls["y"] = data["y"]
        if data.get("r") is not None:
            if self.context.mission.cyb_status.get("CybP_03", None) == "active":
                if random.randint(0, 10) > 6:
                    self.controls["r"] = round(random.uniform(-10, 10))
                else:
                    self.controls["r"] = data["r"]
            else:
                self.controls["r"] = data["r"]

        brush_speed = self.context.mission.brush_speed
        if self.context.mission.brush_controller_burned:
            brush_speed = 0

        self._send_request_with_response("set_brush_speed", {"speed": brush_speed})

    def _send_request_with_response(self, method, data):
        try:
            req = requests.post(
                f"http://127.0.0.1:13501/{method}",
                data=json.dumps({"content": data}),
                timeout=1,
            )
            if req.status_code == 200:
                response = json.loads(req.text)
                return response["content"]
        except Exception as e:
            if "timeout" in str(e):
                self.context.lg.error(f"Ошибка отправки команды: АСО не отвечает")
        return False

    def _get_data_to_send(self):
        self.root.current_max_speed = self.context.mission.r_speed
        if self.context.mission.emergency_stop:
            m = {
                "speed_x": 0,
                "speed_y": 0,
                "speed_r": 0,
            }
        else:
            m = {
                "speed_x": self.controls["x"],
                "speed_y": self.controls["y"],
                "speed_r": self.controls["r"],
            }
        if self.context.mission.status == 1:
            if self.context.mission.cybs.get("CybP_05", None):
                if not self.context.mission.brush_controller_burned:
                    sum_speed = sum(map(abs, m.values()))
                    if sum_speed > 0 and self.context.mission.brush_speed > 0:
                        self.context.mission.brush_controller_temperature += (
                            random.uniform(0.02, 0.2) * sum_speed
                            if self.context.mission.brush_controller_temperature > 120
                            else 0.02
                        )
                    else:
                        self.context.mission.brush_controller_temperature -= 0.1

                    if self.context.mission.brush_controller_temperature >= 150:
                        self.context.mission.brush_controller_burned = True
                        self.context.lg.error("Контроллер щётки успешно сгорел.")

        return m

    def _process_message(self, message):
        pass
