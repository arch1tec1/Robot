from threading import Thread

import const as c
from Core import BaseHandler
from Modules import Context
from Modules.Handler import (
    TwinPositionReceiveHandler,
    NavigationPositionReceiveHandler,
    ChvtMissionHandler,
    LctMissionHandler,
    ChvtHTTPMissionReceiver,
    LctHTTPMissionReceiver,
    RobotStatusReceiveHandler,
)
from Modules.Handler.CommandInterface import CommandInterface
from Modules.Handler.RenderHandler import RenderHandler
from Modules.Handler.SPDHandlers import ChvtSPDHandler, LctSPDHandler


class HandlerDispatcher(BaseHandler):
    def __init__(self, context: Context, init_ok: bool):
        super().__init__(context)
        self.init_ok = init_ok
        self.handlers = []
        context.lg.init(
            f"{context.config.get('general', 'app_name')}, версия {context.config.get('general', 'version')}"
        )

        if self.context.args.get_arg("twin"):
            self.handlers.append(TwinPositionReceiveHandler(self.context))
        else:
            self.handlers.append(NavigationPositionReceiveHandler(self.context))
        
        self.handlers.append(RobotStatusReceiveHandler(self.context))

        if c.MISSION_MODE == "chvt":
            self.handlers.append(ChvtSPDHandler(self.context))
            self.handlers.append(ChvtMissionHandler(self.context))
            self.handlers.append(ChvtHTTPMissionReceiver(self.context))
        elif c.MISSION_MODE == "lct":
            self.handlers.append(LctSPDHandler(self.context))
            self.handlers.append(LctMissionHandler(self.context))
            self.handlers.append(LctHTTPMissionReceiver(self.context))
        else:
            context.lg.error(f"Неверный режим миссии: {c.MISSION_MODE}")
            self.init_ok = False
            return

        self.handlers.append(CommandInterface(self.context))

        self.run()
        context.lg.init("Загрузка завершена.")
        if context.config.get("general", "show_frame"):
            RenderHandler(self.context).run()

    def run(self):
        for handler in self.handlers:
            runnable = Thread(target=handler.run, daemon=True, args=())
            runnable.start()
