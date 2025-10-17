class Mission:
    def __init__(self, context):
        self.context = context

        self.motors_enable = False

        self.status = 0
        self.cybs = {}
        self.cyb_status = {}
        self.mission_vars = {}
        self.mission_checks_ok = False

        self.emergency_stop = False
        self.wait_flag = False
        self.r_speed = 0.0001
        self.brush_speed = 100
        self.camera_frame = None

        self.messages = []

        self.brush_controller_temperature = 0.0
        self.brush_controller_burned = False
