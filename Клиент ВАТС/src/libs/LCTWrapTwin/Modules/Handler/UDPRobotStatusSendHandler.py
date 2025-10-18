from src.libs.LCTWrapTwin.Modules.Core import BaseUDPSendHandler
class UDPRobotStatusSendHandler(BaseUDPSendHandler):
    def __init__(self, context):
        super().__init__(context, "127.0.0.1", 8034, send_interval=0.5)
    def _get_data_to_send(self):
        return {
            "r_speed": self.context.mission.r_speed,
            "brush_controller_temperature": self.context.mission.brush_controller_temperature,
        }
    def _process_message(self, message):
        pass