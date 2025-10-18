from Core import BaseUDPReceiveHandler
class RobotStatusReceiveHandler(BaseUDPReceiveHandler):
    def __init__(self, context, host="0.0.0.0", port=8034):
        super().__init__(context, host, port)
    def _process_message(self, message):
        try:
            self.context.robots.current_robot.brush_controller_temperature = message.get("brush_controller_temperature")
            self.context.robots.current_robot.r_speed = message.get("r_speed")
        except Exception as e:
            pass