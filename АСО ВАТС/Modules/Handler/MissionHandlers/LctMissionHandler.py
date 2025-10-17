import random

from fastapi import Request

import const as c

import Core.BaseFunctions as f
from Core import BaseMissionHandler, BaseHttpTransport


class LctMissionHandler(BaseMissionHandler):
    def set_status(self, status: int):
        if status == 0:
            for cell in self.context.field.cells:
                cell.fill = None
                cell.fill_status = 0
            for i in range(3):
                self.context.spd.t_lights[i].color = 2
            for field_cell in self.context.spd.field_cells:
                field_cell.state = 0
        if status == 2:
            fill_whole = 0
            for cell in self.context.field.cells:
                fill_whole += cell.fill_status
            self.context.lg.log(
                f"Всего очищено: {fill_whole*0.25} м2 ({round(((fill_whole*0.25) / (39*16)) * 100, 2)}%) из {39*16} м2 доступных"
            )
        super().set_status(status)

    def process_status_idle(self, mission):
        super().process_status_idle(mission)

    def process_status_stopped(self, mission):
        super().process_status_stopped(mission)

    def process_status_running(self, mission):
        if self.check_reach_finish_zone():
            self.set_status(2)
            self.context.mission.panel_mission_data.events.append(
                {
                    "m_type": 1,
                    "message": f"Заезд ({mission.mission_uid}): остановлен - по достижению зоны финиша",
                }
            )
            self.context.lg.log(f"Заезд ({mission.mission_uid}): остановлен - по достижению зоны финиша")
            self.drop_triggers()
            return self._continue()

        self.check_left_start_zone()
        self.check_field_cell_cleaning_status()

        super().process_status_running(mission)
        return None

    def check_left_start_zone(self):
        if not self.context.mission.mission_tasks["left_start_zone"]:
            if self.context.robots.current_robot.current_cell_frame != f.get_zone("start_finish")[0]:
                self.context.mission.mission_tasks["left_start_zone"] = True
                self.context.mission.panel_mission_data.events.append(
                    {"m_type": 1, "message": "Робот покинул стартовую зону"}
                )
                self.context.lg.log("Робот покинул стартовую зону")

    def check_reach_finish_zone(self):
        if self.context.mission.mission_tasks["left_start_zone"]:
            if self.context.robots.current_robot.current_cell_frame == f.get_zone("start_finish")[0]:
                self.context.mission.mission_tasks["reach_finish_zone"] = True
                self.context.mission.panel_mission_data.events.append(
                    {"m_type": 1, "message": "Робот достиг финишной зоны"}
                )
                self.context.lg.log("Робот достиг финишной зоны")
                return True
        return False

    def check_field_cell_cleaning_status(self):
        if self.context.spd.brush.state == 0:
            return
        cell_idx = self.context.robots.current_robot.current_cell_point
        if cell_idx is not None:
            if cell_idx <= len(self.context.field.cells):
                cell = self.context.field.cells[cell_idx - 1]
                if hasattr(cell, "fill"):
                    if cell.fill is None:
                        vertices = cell.get_vertices()
                        split = cell.split_rect(vertices, 8)
                    else:
                        split = cell.fill
                else:
                    vertices = cell.get_vertices()
                    split = cell.split_rect(vertices, 8)
                cell.fill_status = 0
                for split_cell in split:
                    if hasattr(split_cell, "fill"):
                        split_cell.fill = (
                            self.context.robots.current_robot.chassis.contains(split_cell) or split_cell.fill
                        )
                    else:
                        split_cell.fill = self.context.robots.current_robot.chassis.contains(split_cell)
                    if split_cell.fill:
                        cell.fill_status += 1
                cell.fill = split

                if str(cell_idx) in c.CELL_NUMBER_TRANSFORM:
                    if cell.fill_status > 55:
                        self.context.spd.field_cells[c.CELL_NUMBER_TRANSFORM[str(cell_idx)]].state = 1
                    elif cell.fill_status > 28:
                        self.context.spd.field_cells[c.CELL_NUMBER_TRANSFORM[str(cell_idx)]].state = 2
                    else:
                        self.context.spd.field_cells[c.CELL_NUMBER_TRANSFORM[str(cell_idx)]].state = 0


class LctHTTPMissionReceiver(BaseHttpTransport):
    def __init__(self, context):
        super().__init__(context, "mission_receiver")

    def make_routes(self):
        @self.api.post("/barrier_toggle")
        async def barrier_toggle(data: Request):
            if self.context.mission.check_robot_in_zones(f.get_service_zone("barrier_trigger"), frame=False):
                state = 1 - self.context.spd.barrier.state
                if random.randint(0, 10) > 5:
                    self.context.spd.barrier.state = 1 - self.context.spd.barrier.state
                return {"status": "OK", "content": {"state": 1 - state}}
            else:
                return {"status": "ERROR", "content": "too far"}

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

        @self.api.post("/emergency_stop")
        async def emergency_stop(data: Request):
            if self.context.mission.send_robot_request("emergency_stop"):
                self.context.lg.warn("ДМ запросил блокировку приводов - выполняется")
                return {"status": "OK"}
            else:
                return {"status": "ERROR", "content": "Не удалось выключить приводы робота"}

        @self.api.post("/emergency_stop_release")
        async def emergency_stop_release(data: Request):
            if self.context.mission.send_robot_request("emergency_stop_release"):
                self.context.lg.warn("ДМ запросил снятие блокировки приводов - выполняется")
                return {"status": "OK"}
            else:
                return {"status": "ERROR", "content": "Не удалось включить приводы робота"}

        @self.api.post("/set_brush_speed")
        async def set_brush_speed(data: Request):
            datum = await data.json()
            try:
                datum = datum["content"]
                self.context.spd.brush.state = datum["speed"]
                return {"status": "OK"}
            except Exception as e:
                pass
            return {"status": "ERROR", "content": "Неверный формат запроса: Ожидается {'speed': int}"}
