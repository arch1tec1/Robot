# X - ВЫСОТА, горизонталь, направлен вправо
# Y - ШИРИНА, вертикаль, направлен вверх
# направление по умолчанию - по X
# Повороты: по часовой - отрицательный, против часовой - положительный

# Нотация для прямоугольников (любых): ЛН ПН ПВ ЛВ (с левого нижнего по кругу против часовой стрелки)

# Все размеры в мм (либо безразмерные)

# Поле 9х9 клеток
FIELD_WIDTH_CELLS = 9
FIELD_HEIGHT_CELLS = 9

# Размер ячейки поля в пикселях (400 мм)
FIELD_CELL_SIZE = 400

# Масштаб для отображения в окне (1 пиксель = 5 мм)
FIELD_TO_WINDOW_SCALE = 0.2

# Отступы поля от края окна в пикселях (для центрирования)
FIELD_OFFSET_X = round(FIELD_CELL_SIZE * FIELD_TO_WINDOW_SCALE)
FIELD_OFFSET_Y = round(FIELD_CELL_SIZE * FIELD_TO_WINDOW_SCALE)

# Размер окна в пикселях (с учётом отступов)
WINDOW_WIDTH = round(FIELD_CELL_SIZE * FIELD_WIDTH_CELLS * FIELD_TO_WINDOW_SCALE + FIELD_OFFSET_X * 2)
WINDOW_HEIGHT = round(FIELD_CELL_SIZE * FIELD_HEIGHT_CELLS * FIELD_TO_WINDOW_SCALE + FIELD_OFFSET_Y * 2)


# КОНСТАНТЫ ДЛЯ ЗАЕЗДОВ

# chvt или lct
MISSION_MODE = "lct"

# Общие константы
MISSION_TIME_LIMIT = 10 * 60
AP_REBOOT_TIME = 5

# Для ЧВТ (и подобных)

CLEANING_TIME_LIMIT = 5

# Для ЛЦТ (и подобных)


if MISSION_MODE == "chvt":

    # Нумерация ячеек начинается с левой нижней (1), идёт вправо и переносится по строкам (НЕ ЗМЕЙКОЙ, СО СДВИГОМ)
    FIELD_SCHEMA = {
        "roads": [12, 13, 17, 22, 23, 24, 25, 26, 31, 33, 35, 40, 44, 49, 51, 53, 58, 59, 60, 61, 62, 65, 66, 67, 70],
        "zones": {
            "control": [74, 75, 76],
            "control_sensor_select": [65, 66, 67],
            "load": [79],
            "fire": [11],
            "check": [47, 48, 38, 39],
            "cleaning": [42],
            "start": [18],
            "finish": [54],
        },
        "service_zones": {
            "CybP_01_trigger": [25, 35],
            "CybZ_01_trigger": [49, 44],
            "CybZ_02_trigger": [61],
            "Cyb_04_variants": [[33, 51], [58, 67], [53, 62]],
        },
        "markers": [1, 5, 9, 37, 41, 45, 73, 77, 81],
    }

    ZONE_COLORS = {
        "road": (36, 35, 40, 1),
        "control": (50, 70, 200, 150),
        "control_sensor_select": (50, 70, 200, 60),
        "load": (253, 127, 0, 150),
        "fire": (254, 0, 0, 140),
        "check": (254, 254, 0, 140),
        "cleaning": (254, 102, 254, 140),
        "start": (127, 254, 0, 140),
        "finish": (0, 254, 254, 140),
        "markers": (140, 140, 140, 100),
        None: (80, 80, 80, 100),
    }

if MISSION_MODE == "lct":
    FIELD_SCHEMA = {
        "roads": [
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            22,
            26,
            27,
            29,
            31,
            35,
            38,
            40,
            44,
            47,
            49,
            50,
            51,
            52,
            53,
            56,
            58,
            62,
            65,
            66,
            67,
            68,
            69,
            71,
            75,
            76,
            78,
            79,
            80,
        ],
        "zones": {
            "slip": [62, 71, 31, 40],
            "pedestrian": [56, 15],
            "start_finish": [19],
        },
        "service_zones": {
            "pedestrian_l_trigger": [47, 56, 65, 66, 38],
            "pedestrian_r_trigger": [14, 15, 16, 13, 17],
            "barrier_trigger": [29, 38, 47],
            "cyb_p_02_trigger": [26],
            "cyb_p_04_trigger": [67, 68, 69],
        },
        "markers": [1, 5, 9, 37, 41, 45, 73, 77, 81],
    }

    ZONE_COLORS = {
        "road": (36, 35, 40, 1),
        "slip": (50, 70, 200, 150),
        "start_finish": (253, 127, 0, 150),
        "pedestrian": (254, 102, 254, 140),
        "markers": (140, 140, 140, 100),
        None: (80, 80, 80, 100),
    }

    CELL_NUMBER_TRANSFORM = {
        "11": 8,
        "12": 7,
        "13": 6,
        "14": 5,
        "15": 4,
        "16": 3,
        "17": 2,
        "18": 1,
        "19": 13,
        "20": 12,
        "22": 11,
        "26": 10,
        "27": 9,
        "29": 16,
        "31": 15,
        "35": 14,
        "38": 19,
        "40": 18,
        "44": 17,
        "47": 25,
        "49": 24,
        "50": 23,
        "51": 22,
        "52": 21,
        "53": 20,
        "56": 28,
        "58": 27,
        "62": 26,
        "65": 34,
        "66": 33,
        "67": 32,
        "68": 31,
        "69": 30,
        "71": 29,
        "75": 39,
        "76": 38,
        "78": 37,
        "79": 36,
        "80": 35,
    }


ROBOT_WIDTH = 210
ROBOT_HEIGHT = 260
ROBOT_WHEEL_OFFSET_X = 165
ROBOT_WHEEL_OFFSET_Y = 165
ROBOT_WHEEL_WIDTH = 55
ROBOT_WHEEL_RADIUS = 105

NUM_ROBOTS = 5
