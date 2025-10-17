from threading import Thread

from Core import BaseHandler, BaseSPDMiddleware


class LctSPDHandler(BaseHandler):
    def __init__(self, context):
        super().__init__(context)

        self.sub_handlers = []

        if self.context.args.get_arg("twin"):
            self.devices = (
                BarrierSPDMiddleware(context, context.spd.barrier),
                BrushSPDMiddleware(context, context.spd.brush),
                MtsSPDMiddleware(context, context.spd.mts),
                *[PedestrianSPDMiddleware(context, _) for _ in context.spd.pedestrians],
                *[TLightSPDMiddleware(context, _) for _ in context.spd.t_lights],
            )
        else:
            self.devices = (
                BarrierSPDMiddleware(context, context.spd.barrier),
                RemoteSPDMiddleware(context, context.spd.remote),
                MtsSPDMiddleware(context, context.spd.mts),
                *[PedestrianSPDMiddleware(context, _) for _ in context.spd.pedestrians],
                *[TLightSPDMiddleware(context, _) for _ in context.spd.t_lights],
                *[FieldCellSPDMiddleware(context, _) for _ in context.spd.field_cells],
            )

    def run(self):
        for device in self.devices:
            self.sub_handlers.append(device)
        for handler in self.sub_handlers:
            runnable = Thread(target=handler.run, daemon=True, args=())
            runnable.start()


class PedestrianSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        return {"s": self.device.state}

    def process_response(self, message):
        pass


class BrushSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        return {"s": self.device.state}

    def process_response(self, message):
        pass


class MtsSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        return {"s": self.device.state}

    def process_response(self, message):
        pass


class BarrierSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        return {"s": self.device.state}

    def process_response(self, message):
        pass


class TLightSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        return {"c": self.device.color}

    def process_response(self, message):
        pass


class FieldCellSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device)

    def prepare_data(self):
        return {"s": self.device.state}

    def process_response(self, message):
        pass


class RemoteSPDMiddleware(BaseSPDMiddleware):
    def __init__(self, context, device):
        super().__init__(context, device, receive_data=True, send_interval=0.3)

    def prepare_data(self):
        leds_list = [0 for _ in range(20)]
        if self.context.robots.current_robot.r_id is not None:

            for i in range(10):
                leds_list[i] = 0
            if self.context.mission.status == 1:
                leds_list[10 - int(self.context.robots.current_robot.r_id)] = 2
            elif self.context.mission.status == 3 or self.context.mission.status == 4:
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
            self.context.mission.triggers.start_mission_trigger = message["b2"]
            self.context.mission.triggers.stop_mission_trigger = message["b1"]
        except Exception as e:
            pass
