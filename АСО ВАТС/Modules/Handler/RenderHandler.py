import arcade
import pyglet

import const as c
from Core import BaseHandler


class RenderHandler(BaseHandler):
    def __init__(self, context):
        super().__init__(context)

        arcade.configure_logging(level=0)

        app = AppWindow(context)
        try:
            arcade.run()
        except KeyboardInterrupt as e:
            self.context.lg.log("Нажмите ещё раз для выхода...")
        except Exception as e:
            pass

    def run(self):
        pass


class AppWindow(arcade.Window):
    def __init__(self, context):
        super().__init__(
            width=c.WINDOW_WIDTH,
            height=c.WINDOW_HEIGHT,
            title="AGTS-TRACKING",
            antialiasing=True,
            vsync=True,
        )
        self.app_context = context

        arcade.set_background_color(arcade.color.ARSENIC)
        arcade.enable_timings()

        if c.MISSION_MODE == "chvt":
            self.background = arcade.load_texture("Modules/Assets/background_chvt.jpg")
        elif c.MISSION_MODE == "lct":
            self.background = arcade.load_texture("Modules/Assets/background_lct.jpg")
        else:
            context.lg.error("Неизвестный режим миссии: %s", c.MISSION_MODE)
            return

    def reset(self):
        pass

    def on_draw(self):
        self.clear()

        try:
            self.draw_background()
            self.draw_polygon_zones()
            self.draw_robots()
            self.draw_fps()
            # self.draw_grid()
            # self.draw_borders()
            # self.draw_split()
        except Exception as e:
            print(e)

    def draw_background(self):
        arcade.draw_texture_rect(
            self.background,
            arcade.LRBT(
                c.FIELD_OFFSET_X,
                c.WINDOW_WIDTH - c.FIELD_OFFSET_X,
                c.FIELD_OFFSET_Y,
                c.WINDOW_HEIGHT - c.FIELD_OFFSET_Y,
            ),
        )

    @staticmethod
    def draw_fps():
        fps = arcade.Text(f"FPS: {round(arcade.get_fps())}", 0, c.WINDOW_HEIGHT - 30, arcade.color.ASH_GREY, 18)
        fps.draw()

    def draw_split(self):
        for cell in self.app_context.field.cells:
            if hasattr(cell, "fill"):
                if cell.fill is not None:
                    for fill_cell in cell.fill:
                        vertices = fill_cell.get_translated_vertices()
                        arcade.draw_polygon_outline(vertices, (0, 0, 0))
                        if fill_cell.fill:
                            arcade.draw_polygon_filled(vertices, (0, 0, 254, 200))

    def draw_polygon_zones(self):
        for cell in self.app_context.field.cells:
            color = c.ZONE_COLORS.get(cell.zone_type, c.ZONE_COLORS[None])
            for robot in self.app_context.robots.list:
                if (
                    cell.contains(robot.chassis)
                    and cell.zone_type != "road"
                    and cell.zone_type != "start"
                    and cell.zone_type != "finish"
                ):
                    color = (color[0], color[1], color[2], 220)
            arcade.draw_polygon_filled(cell.get_translated_vertices(), color)

    def draw_robots(self):
        for robot in self.app_context.robots.list:
            if robot.r_id is not None:
                if robot.position_quality < 0.1:
                    continue
                if self.app_context.spd.brush.state > 0:
                    color = (0, 254, 0)
                else:
                    color = (254, 0, 0)
                arcade.draw_polygon_filled(robot.chassis.get_translated_vertices(), (254, 254, 0))
                arcade.draw_polygon_filled(robot.brush.get_translated_vertices(), color)
                if robot.r_id != "002":
                    arcade.Text(
                        "t: " + str(round(robot.brush_controller_temperature)) + "°C",
                        robot.chassis.get_translated_center()[0],
                        robot.chassis.get_translated_center()[1] + 40,
                        font_size=18,
                        color=(20, 20, 20, 200),
                    ).draw()
                for wheel in robot.wheels:
                    color = (200, 200, 200)
                    for cell in self.app_context.field.cells:
                        if cell.contains(wheel) and cell.zone_type != "road":
                            color = (254, 0, 0)
                        if cell.contains(wheel) and (
                            cell.zone_type == "slip"
                            or cell.zone_type == "pedestrian"
                            or cell.zone_type == "start_finish"
                        ):
                            color = (0, 0, 254)
                            # arcade.draw_polygon_filled(cell.get_translated_vertices(), (0, 254, 0))
                    arcade.draw_polygon_filled(wheel.get_translated_vertices(), color)

    @staticmethod
    def draw_grid():
        for x in range(c.FIELD_OFFSET_X, c.WINDOW_WIDTH, round(c.FIELD_CELL_SIZE * c.FIELD_TO_WINDOW_SCALE)):
            arcade.draw_line(x, 0, x, c.WINDOW_HEIGHT, arcade.color.BLUEBERRY, 1)
        for y in range(c.FIELD_OFFSET_Y, c.WINDOW_HEIGHT, round(c.FIELD_CELL_SIZE * c.FIELD_TO_WINDOW_SCALE)):
            arcade.draw_line(0, c.WINDOW_HEIGHT - y, c.WINDOW_WIDTH, c.WINDOW_HEIGHT - y, arcade.color.BLUEBERRY, 1)

    @staticmethod
    def draw_borders():
        arcade.draw_line(c.FIELD_OFFSET_X, 0, c.FIELD_OFFSET_X, c.WINDOW_HEIGHT, arcade.color.RED, 1)
        arcade.draw_line(
            c.WINDOW_WIDTH - c.FIELD_OFFSET_X,
            0,
            c.WINDOW_WIDTH - c.FIELD_OFFSET_X,
            c.WINDOW_HEIGHT,
            arcade.color.RED,
            1,
        )
        arcade.draw_line(0, c.FIELD_OFFSET_Y, c.WINDOW_WIDTH, c.FIELD_OFFSET_Y, arcade.color.RED, 1)
        arcade.draw_line(
            0,
            c.WINDOW_HEIGHT - c.FIELD_OFFSET_Y,
            c.WINDOW_WIDTH,
            c.WINDOW_HEIGHT - c.FIELD_OFFSET_Y,
            arcade.color.RED,
            1,
        )

    @staticmethod
    def draw_edges(rect, color=arcade.color.YELLOW):
        vertices = rect.get_translated_vertices()
        for i in range(len(vertices)):
            start_point = vertices[i]
            end_point = vertices[(i + 1) % len(vertices)]
            arcade.draw_line(start_point[0], start_point[1], end_point[0], end_point[1], color, 2)
            arcade.draw_circle_filled(vertices[i][0], vertices[i][1], 1, color)
