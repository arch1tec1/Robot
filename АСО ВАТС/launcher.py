import time

from Modules import HandlerDispatcher
from Modules import Context

if __name__ == "__main__":
    init_ok = True

    CTX = Context(init_ok)
    HD = HandlerDispatcher(CTX, init_ok)

    try:
        while init_ok:
            time.sleep(0.5)
        CTX.lg.error("Завершение работы: ошибка инициализации.")
    except KeyboardInterrupt as e:
        CTX.lg.log("KeyboardInterrupt, остановлено пользователем.")
