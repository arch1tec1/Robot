import sys
import time

from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from Core import BaseHandler
from Modules.Context.Common import Field, Robots
from Modules.Context.Missions import ChvtMission, LctMission
from Modules.Context.SDPStores import ChvtSPDSet, LctSPDSet

is_windows = sys.platform == "win32"
if is_windows:
    import msvcrt

import const as c
class CommandInterface(BaseHandler):
    def __init__(self, context):
        super().__init__(context)
        self.command_history = []
        self.history_index = -1

    def run(self):
        time.sleep(2)
        self.context.lg.log("Ожидаю ввод команд (/help для получения списка доступных команд)...")

        if not is_windows:
            self.context.lg.warn(
                "Интерактивный ввод команд поддерживается только в Windows. Используйте /q для выхода."
            )
            while True:
                try:
                    command = input("> ")
                    if command == "/q":
                        break
                    self.process_command(command)
                except (KeyboardInterrupt, EOFError):
                    break
            return

        command_buffer = ""

        def get_renderable(text: str):
            cursor = "█" if int(time.time() * 2) % 2 == 0 else " "
            return Panel(Text(f"> {text}{cursor}", justify="left"), title="Командный ввод")

        with Live(get_renderable(""), console=self.context.lg.cls, refresh_per_second=10) as live:
            while True:
                try:
                    if msvcrt.kbhit():
                        char = msvcrt.getwch()
                        if char == "\r":  # Enter
                            if command_buffer:
                                self.process_command(command_buffer)
                                if not self.command_history or self.command_history[-1] != command_buffer:
                                    self.command_history.append(command_buffer)
                                self.history_index = len(self.command_history)
                                command_buffer = ""
                        elif char == "\xe0":
                            char = msvcrt.getwch()
                            if char == "H":  # Up arrow
                                if self.history_index > 0:
                                    self.history_index -= 1
                                    command_buffer = self.command_history[self.history_index]
                            elif char == "P":  # Down arrow
                                if self.history_index < len(self.command_history) - 1:
                                    self.history_index += 1
                                    command_buffer = self.command_history[self.history_index]
                                elif self.history_index == len(self.command_history) - 1:
                                    self.history_index += 1
                                    command_buffer = ""
                        elif char == "\x08":
                            command_buffer = command_buffer[:-1]
                        elif char == "\x03":
                            break
                        else:
                            command_buffer += char

                    live.update(get_renderable(command_buffer))
                    time.sleep(0.02)

                except (KeyboardInterrupt, EOFError):
                    break
                except Exception as e:
                    self.context.lg.error(f"Ошибка в цикле ввода: {e}")
                    pass

    def process_command(self, command: str):
        if not command.startswith("/"):
            self.context.lg.error("Ошибка ввода: команда должна начинаться с '/'")
            return

        if command.startswith("/start"):
            self.context.mission.triggers.start_mission_trigger = True
            self.context.lg.log("Команда '/start' успешно выполнена")
        elif command == "/stop":
            self.context.mission.triggers.stop_mission_trigger = True
            self.context.lg.log("Команда '/stop' успешно выполнена")
        elif command == "/reset":
            if c.MISSION_MODE == "chvt":
                self.context.mission = ChvtMission(self)
                self.context.spd = ChvtSPDSet(self)
            elif c.MISSION_MODE == "lct":
                self.context.mission = LctMission(self)
                self.context.spd = LctSPDSet(self)
            self.context.field = Field()
            self.context.robots = Robots(self)
            self.context.mission.triggers.reset_mission_trigger = True
            self.context.mission.triggers.reset_twin_trigger = True
            self.context.lg.log("Команда '/reset' успешно выполнена")
        elif command.startswith("/robot select"):
            args = command.split()
            try:
                self.context.robots.select_robot(args[2])
            except IndexError:
                self.context.lg.error("Ошибка ввода: не указан r_id робота")
        elif command.startswith("/robot list"):
            self.context.lg.add_to_batch("Статус роботов:")
            self.context.lg.add_to_batch("")
            for robot in self.context.robots.list:
                self.context.lg.add_to_batch(f"Робот {robot.r_id}: position_quality={robot.position_quality}")
            self.context.lg.flush_batch()
        else:
            self.context.lg.error("Неизвестная команда: {}".format(command))
