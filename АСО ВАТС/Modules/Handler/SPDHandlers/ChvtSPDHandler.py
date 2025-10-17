from threading import Thread

import const as c
from Core import BaseHandler, BaseSPDMiddleware


class ChvtSPDHandler(BaseHandler):
    def __init__(self, context):
        super().__init__(context)

        self.sub_handlers = []

        self.devices = (
            *[ControlSPDMiddleware(self.context, device) for device in context.spd.controls],
            CleaningSPDMiddleware(self.context, context.spd.cleaning),
            PipesSPDMiddleware(self.context, context.spd.pipes),
            RemoteSPDMiddleware(self.context, context.spd.remote),
        )

    def run(self):
        for device in self.devices:
            self.sub_handlers.append(device)
        for handler in self.sub_handlers:
            runnable = Thread(target=handler.run, daemon=True, args=())
            runnable.start()


class ControlSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        self.context.field.cells[c.get_zone("control")[self.device.d_id] - 1].set_indicator(self.device.color)
        return {"c": self.device.color, "glitch": self.device.glitch}

    def process_response(self, message):
        pass


class CleaningSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        self.context.field.cells[c.get_zone("cleaning")[0] - 1].set_indicator(self.device.color)
        return {"c": self.device.color, "glitch": self.device.glitch}

    def process_response(self, message):
        pass


class PipesSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        if self.context.args.get_arg("twin"):
            color = self.device.twin_color
        else:
            color = self.device.color
        m = {
            "m0": f"{self.device.pipes_glitch[0]}{color[0]}",
            "m1": f"{self.device.pipes_glitch[1]}{color[1]}",
            "m2": f"{self.device.pipes_glitch[2]}{color[2]}",
            "m3": f"{self.device.pipes_glitch[3]}{color[3]}",
            "barrel_glitch": self.device.barrel_glitch,
        }
        self.context.field.cells[c.get_zone("check")[0] - 1].set_indicator(self.device.twin_color[0])
        self.context.field.cells[c.get_zone("check")[1] - 1].set_indicator(self.device.twin_color[1])
        self.context.field.cells[c.get_zone("check")[2] - 1].set_indicator(self.device.twin_color[2])
        self.context.field.cells[c.get_zone("check")[3] - 1].set_indicator(self.device.twin_color[3])
        return m

    def process_response(self, message):
        pass


class RemoteSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device, receive_data=True)

    def prepare_data(self):
        leds_list = [0 for _ in range(20)]
        if self.context.robots.current_robot.r_id is not None:

            for i in range(10):
                leds_list[i] = 0
            if self.context.mission.status == 1:
                leds_list[10 - int(self.context.robots.current_robot.r_id)] = 2
            elif self.context.mission.status == 2:
                leds_list[10 - int(self.context.robots.current_robot.r_id)] = 1
            else:
                leds_list[10 - int(self.context.robots.current_robot.r_id)] = 4

            for robot in self.context.robots.list:
                leds_list[9 + int(robot.r_id)] = 1
                if robot.position_quality > 0.1:
                    leds_list[9 + int(robot.r_id)] = 3
                if robot.position_quality > 0.7:
                    leds_list[9 + int(robot.r_id)] = 2

        return {"c": leds_list, "cmd": "get_buttons"}

    def process_response(self, message):
        try:
            self.context.mission.triggers.start_mission_trigger = message["b1"]
            self.context.mission.triggers.stop_mission_trigger = message["b2"]
        except Exception as e:
            pass
