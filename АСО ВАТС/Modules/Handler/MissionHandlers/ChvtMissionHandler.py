from fastapi import Request

import const as c
from Core import BaseMissionHandler, BaseHttpTransport


class ChvtMissionHandler(BaseMissionHandler):
    def set_status(self, status):
        if status == 0:
            self.context.spd.controls[0].color = 0
            self.context.spd.controls[1].color = 0
            self.context.spd.controls[2].color = 0

            self.context.spd.controls[0].glitch = False
            self.context.spd.controls[1].glitch = False
            self.context.spd.controls[2].glitch = False

            self.context.spd.pipes.color = [0, 0, 0, 0]
            self.context.spd.pipes.twin_color = [0, 0, 0, 0]
            self.context.spd.pipes.pipes_glitch = [1, 1, 1, 1]
            self.context.spd.cleaning.color = 0

            self.context.spd.pipes.barrel_glitch = True
        super().set_status(status)

    def process_status_idle(self, mission):
        super().process_status_idle(mission)

    def process_status_stopped(self, mission):
        super().process_status_stopped(mission)

    def process_status_running(self, mission):
        if self.check_reach_finish_zone():
            if self.send_robot_request("stop_mission"):
                self.set_status(2)
                self.context.mission.panel_mission_data.events.append(
                    {
                        "m_type": 1,
                        "message": f"Заезд ({mission.mission_uid}): остановлен - по достижению зоны финиша",
                    }
                )
                self.context.lg.log(f"Заезд ({mission.mission_uid}): остановлен - по достижению зоны финиша")
                return self._continue()
            else:
                self.context.lg.error("Ошибка при остановке заезда (достижение зоны финиша)")
                self.drop_triggers()

        self.check_left_start_zone()
        self.check_reach_load_zone()
        self.check_reach_fire_zone()
        self.check_reach_cleaning_zone()
        self.check_left_cleaning_zone()
        self.check_control_sensor_select_zone()
        self.check_pollution_sensor_select_zone()

        super().process_status_running(mission)
        return None

    def check_reach_finish_zone(self):
        if self.context.mission.mission_tasks["left_start_zone"]:
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("finish")[0]:
                self.context.mission.mission_tasks["reach_finish_zone"] = True
                self.context.mission.panel_mission_data["events"].append(
                    {"m_type": 1, "message": "Робот достиг финишной зоны"}
                )
                self.context.lg.log("Робот достиг финишной зоны")
                return True
        return False

    def check_left_start_zone(self):
        if not self.context.mission.mission_tasks["left_start_zone"]:
            if self.context.robots.current_robot.current_cell_frame != c.get_zone("start")[0]:
                self.context.mission.mission_tasks["left_start_zone"] = True
                self.context.mission.panel_mission_data["events"].append(
                    {"m_type": 1, "message": "Робот покинул стартовую зону"}
                )
                self.context.lg.log("Робот покинул стартовую зону")

    def check_reach_load_zone(self):
        if not self.context.mission.mission_tasks["reach_load_zone"]:
            if c.get_zone("load")[0] in self.context.robots.current_robot.two_wheels:
                self.context.mission.mission_tasks["reach_load_zone"] = True
                self.context.mission.panel_mission_data["events"].append(
                    {"m_type": 1, "message": "Робот достиг зоны погрузки"}
                )
                self.context.lg.log("Робот достиг зоны погрузки")

    def check_reach_fire_zone(self):
        if not self.context.mission.mission_tasks["reach_fire_zone"]:
            if c.get_zone("fire")[0] in self.context.robots.current_robot.two_wheels:
                self.context.mission.mission_tasks["reach_fire_zone"] = True
                self.context.mission.panel_mission_data["events"].append(
                    {"m_type": 1, "message": "Робот достиг зоны тушения"}
                )
                self.context.lg.log("Робот достиг зоны тушения")

    def check_reach_cleaning_zone(self):
        if not self.context.mission.mission_tasks["reach_cleaning_zone"]:
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("cleaning")[0]:
                self.context.mission.mission_tasks["reach_cleaning_zone"] = True
                self.context.mission.panel_mission_data["events"].append(
                    {"m_type": 1, "message": "Робот достиг зоны очистки"}
                )
                self.context.lg.log("Робот достиг зоны очистки")

    def check_left_cleaning_zone(self):
        if (
            self.context.mission.mission_tasks["requested_cleaning"]
            and not self.context.mission.mission_tasks["awaited_cleaning_correctly"]
            and not self.context.mission.mission_tasks["awaited_cleaning_incorrectly"]
        ):
            if self.context.robots.current_robot.current_cell_frame != c.get_zone("cleaning")[0]:
                if self.context.mission.mission_vars["finished_cleaning"]:
                    self.context.mission.mission_tasks["awaited_cleaning_correctly"] = True
                    self.context.mission.panel_mission_data["events"].append(
                        {"m_type": 1, "message": "Робот успешно прошёл очистку в установленное время"}
                    )
                    self.context.lg.log("Робот успешно прошёл очистку в установленное время")
                else:
                    self.context.mission.panel_mission_data["events"].append(
                        {"m_type": 1, "message": "Робот покинул зону очистки ранее окончания процесса"}
                    )
                    self.context.mission.mission_tasks["awaited_cleaning_incorrectly"] = True
                    self.context.lg.error("Робот покинул зону очистки ранее окончания процесса")
                self.context.spd.cleaning.color = 0

    def check_control_sensor_select_zone(self):
        zone_idx = None
        if self.context.mission.mission_tasks["left_start_zone"]:
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("control_sensor_select")[0]:
                zone_idx = 0
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("control_sensor_select")[1]:
                zone_idx = 1
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("control_sensor_select")[2]:
                zone_idx = 2
        if zone_idx is not None and self.context.mission.cybs["CybZ_03"]:
            self.context.mission.panel_mission_data["sec_domains"]["sensors"] = "bad"
            self.context.mission.panel_mission_data["sec_targets"]["CybZ_03"] = "running"
        else:
            self.context.mission.panel_mission_data["sec_domains"]["sensors"] = "good"
            if self.context.mission.panel_mission_data["sec_targets"]["CybZ_03"] == "running":
                self.context.mission.panel_mission_data["sec_targets"]["CybZ_03"] = "success"
        self.context.mission.mission_vars["control_sensor_position"] = zone_idx

    def check_pollution_sensor_select_zone(self):
        zone_idx = None
        if self.context.mission.mission_tasks["left_start_zone"]:
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("check")[0]:
                zone_idx = 0
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("check")[1]:
                zone_idx = 1
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("check")[2]:
                zone_idx = 2
            if self.context.robots.current_robot.current_cell_frame == c.get_zone("check")[3]:
                zone_idx = 3
        if zone_idx is not None and self.context.mission.cybs["CybZ_04"]:
            self.context.mission.panel_mission_data["sec_domains"]["sensors"] = "bad"
            self.context.mission.panel_mission_data["sec_targets"]["CybZ_04"] = "running"
        else:
            self.context.mission.panel_mission_data["sec_domains"]["sensors"] = "good"
            if self.context.mission.panel_mission_data["sec_targets"]["CybZ_04"] == "running":
                self.context.mission.panel_mission_data["sec_targets"]["CybZ_04"] = "success"
        self.context.mission.mission_vars["pollution_sensor_position"] = zone_idx


class ChvtHTTPMissionReceiver(BaseHttpTransport):
    def __init__(self, context):
        super().__init__(context, "mission_receiver")

    def make_routes(self):
        @self.api.post("/grab_payload")
        async def grab_payload(data: Request):
            self.context.mission.mission_tasks["grab_payload_attempt"] = True
            self.context.lg.log("Робот совершил попытку захвата груза")
            return {"status": "OK"}

        @self.api.post("/drop_payload")
        async def drop_payload(data: Request):
            self.context.mission.mission_tasks["drop_payload_attempt"] = True
            self.context.lg.log("Робот совершил попытку сброса груза")
            return {"status": "OK"}

        @self.api.post("/begin_cleaning")
        async def begin_cleaning(data: Request):
            self.context.mission.mission_tasks["requested_cleaning"] = True
            self.context.lg.log("Робот запросил активацию очистки")
            self.context.mission.begin_cleaning()
            return {"status": "OK"}

        @self.api.post("/cleaning_status")
        async def cleaning_status(data: Request):
            return {
                "status": "OK",
                "content": {"cleaning_finished": self.context.mission.mission_vars["finished_cleaning"]},
            }

        @self.api.post("/get_control_status")
        async def get_control_status(data: Request):
            color = self.context.mission.get_control_sensor_color()
            if color is not None:
                self.context.lg.log(
                    f"Робот запросил цвет блока диспетчерской ({self.context.mission.mission_vars['control_sensor_position']}):"
                    f" {color}"
                )
                return {
                    "status": "OK",
                    "content": {"control_color": color},
                }
            else:
                return {"status": "ERROR", "content": "Не удалось установить датчик цвета"}

        @self.api.post("/get_control_color_temperature")
        async def get_control_color_temperature(data: Request):
            color = self.context.mission.get_control_sensor_temperature()
            if color is not None:
                self.context.lg.log(
                    f"Робот запросил цветовую температуру блока диспетчерской"
                    f" ({self.context.mission.mission_vars['control_sensor_position']}):"
                    f" {color}"
                )
                return {
                    "status": "OK",
                    "content": {"control_color_temp": color},
                }
            else:
                return {"status": "ERROR", "content": "Не удалось установить датчик цветовой температуры"}

        @self.api.post("/get_pollution_status")
        async def get_pollution_status(data: Request):
            state = self.context.mission.get_pollution_sensor_state()
            if state is not None:
                self.context.lg.log(
                    f"Робот запросил уровень загрязнения в текущей клетке "
                    f"({self.context.mission.mission_vars['pollution_sensor_position'] + 1}):"
                    f" {state}"
                )
                return {
                    "status": "OK",
                    "content": {"pollution_status": state},
                }
            else:
                return {"status": "ERROR", "content": "Не удалось установить датчик загрязнения робота"}

        @self.api.post("/get_reserved_cell_pollution_status")
        async def get_reserved_cell_pollution_status(data: Request):
            state = self.context.mission.get_reserved_pollution_sensor_state()
            if state is not None:
                self.context.lg.log(
                    f"Доверенный модуль запросил уровень загрязнения в текущей клетке "
                    f"({self.context.mission.mission_vars['pollution_sensor_position'] + 1}):"
                    f" {state}"
                )
                return {
                    "status": "OK",
                    "content": {"state": state},
                }
            else:
                return {"status": "ERROR", "content": "Не удалось установить датчик загрязнения доверенного модуля"}

        @self.api.post("/ap_force_reset")
        async def ap_force_reset(data: Request):
            self.context.mission.reboot_ap()
            return {"status": "OK"}

        @self.api.post("/get_ap_code_hash")
        async def get_ap_code_hash(data: Request):
            return {"status": "OK", "content": {"ap_code_hash": self.context.mission.mission_vars["ap_code_hash"]}}

        @self.api.post("/get_short_message")
        async def get_short_message(data: Request):
            c_hash = self.context.mission.make_short_message()
            return {"status": "OK", "content": {"message": c_hash}}

        @self.api.post("/set_short_message")
        async def set_short_message(data: Request):
            datum = await data.json()
            try:
                self.context.mission.mission_vars["last_short_message"] = datum.get("content", {}).get("message", "")
                return {"status": "OK"}
            except Exception as e:
                return {"status": "ERROR", "content": "Неверный формат сообщения"}

        @self.api.post("/get_drive_data")
        async def get_drive_data(data: Request):
            return {"status": "OK", "content": {"drive_data": self.context.mission.mission_vars["drive_info"]}}

        @self.api.post("/drive_force_reset")
        async def drive_force_reset(data: Request):
            datum = await data.json()
            try:
                d_id = datum.get("content", {}).get("d_id", "")
                self.context.mission.reboot_drive(d_id)
                return {"status": "OK"}
            except Exception as e:
                pass
            return {"status": "ERROR", "content": "Неверный формат запроса: Ожидается {'d_id': 'ID'}"}

        @self.api.post("/get_service_zones")
        async def get_service_zones(data: Request):
            return {"status": "OK", "content": {"service_zones": self.context.mission.get_service_zones()}}

        @self.api.post("/emergency_stop")
        async def emergency_stop(data: Request):
            if self.context.mission.send_robot_request_with_ack("emergency_stop"):
                self.context.lg.warn("ДМ запросил блокировку приводов - выполняется")
                return {"status": "OK"}
            else:
                return {"status": "ERROR", "content": "Не удалось выключить приводы робота"}

        @self.api.post("/emergency_stop_release")
        async def emergency_stop_release(data: Request):
            if self.context.mission.send_robot_request_with_ack("emergency_stop_release"):
                self.context.lg.warn("ДМ запросил снятие блокировки приводов - выполняется")
                return {"status": "OK"}
            else:
                return {"status": "ERROR", "content": "Не удалось включить приводы робота"}

        @self.api.post("/speed_controller_reset")
        async def speed_controller_reset(data: Request):
            if self.context.mission.send_robot_request_with_ack("force_slow_end"):
                self.context.lg.warn("ДМ запросил корректировку скорости движения - выполняется")
                return {"status": "OK"}
            else:
                return {"status": "ERROR", "content": "Не удалось перезагрузить контроллер скорости"}

        @self.api.post("/get_system_messages")
        async def get_system_messages(data: Request):
            messages = self.context.mission.mission_vars["system_messages"].copy()
            self.context.mission.mission_vars["system_messages"] = []
            return {
                "status": "OK",
                "content": {"system_messages": messages},
            }

        @self.api.post("/payload_lock")
        async def payload_lock(data: Request):
            self.context.lg.warn("ДМ запросил блокировку устройства захвата - выполняется")
            self.context.mission.mission_vars["payload_block"] = True
            return {"status": "OK"}

        @self.api.post("/payload_unlock")
        async def payload_unlock(data: Request):
            self.context.lg.warn("ДМ запросил снятие блокировки устройства захвата - выполняется")
            self.context.mission.mission_vars["payload_block"] = False
            return {"status": "OK"}
