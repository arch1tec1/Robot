import time
from random import randint, choice

import crc8

import Core.BaseFunctions as f
from Core import BaseMission
from Core.BaseMission import PanelData


class LctMission(BaseMission):

    @staticmethod
    def reset_panel_data():
        panel_mission_data = PanelData(
            "---",
            "--:--",
            "-----",
            0,
            [],
            {
                "autopilot": "good",
                "network": "good",
                "effect": "good",
                "motors": "good",
                "navigation": "good",
                "schedule": "good",
            },
            {
                "CybP_01": "pending",
                "CybP_02": "pending",
                "CybP_03": "pending",
                "CybP_04": "pending",
                "CybP_05": "pending",
                "CybP_06": "pending",
            },
        )

        return panel_mission_data

    def init_mission(self, cybs):
        self.cybs = cybs

        for cyb in cybs.keys():
            self.cyb_status[cyb] = "pending"

        if not self.cybs["CybP_01"]:
            self.panel_mission_data.sec_domains["autopilot"] = "trusted"

        if not self.cybs["CybP_02"]:
            self.panel_mission_data.sec_domains["network"] = "trusted"

        if not self.cybs["CybP_03"]:
            self.panel_mission_data.sec_domains["motors"] = "trusted"

        if not self.cybs["CybP_04"]:
            self.panel_mission_data.sec_domains["effect"] = "trusted"

        if not self.cybs["CybP_05"]:
            self.panel_mission_data.sec_domains["navigation"] = "trusted"

        if not self.cybs["CybP_06"]:
            self.panel_mission_data.sec_domains["schedule"] = "trusted"

        self.panel_mission_data = self.reset_panel_data()

        self.context.lg.log("Активация КП:")
        self.context.lg.log(cybs)

        self.time_start = time.time()
        self.mission_tasks = {
            "left_start_zone": False,
            "reach_finish_zone": False,
        }

        ap_code_hash = f.gen_uid(20)

        self.mission_vars = {
            "ap_original_code_hash": ap_code_hash,
            "ap_code_hash": ap_code_hash,
            "ap_reboot": False,
            "burn_electric_schemes": False,
            "last_short_message": "",
            "current_malfunction_drive_id": None,
            "drive_info": [
                {"d_id": 0, "data": "", "serial": self.context.system.gen_uid(5), "signature": "---"},
                {"d_id": 1, "data": "", "serial": self.context.system.gen_uid(5), "signature": "---"},
                {"d_id": 2, "data": "", "serial": self.context.system.gen_uid(5), "signature": "---"},
                {"d_id": 3, "data": "", "serial": self.context.system.gen_uid(5), "signature": "---"},
            ],
            "pedestrian_l_active": False,
            "pedestrian_r_active": False,
            "slip_direction": 0,
            "network_status": {
                "base_station_alpha_rssi": 0,
                "base_station_bravo_rssi": 0,
                "base_station_charlie_rssi": 0,
            },
        }

        for i in range(3):
            self.context.spd.t_lights[i].color = 2

        self.begin_mission_update()

    def make_actions(self):
        def run_cyb_01():
            check_zones = [
                *f.get_service_zone("pedestrian_l_trigger"),
                *f.get_service_zone("pedestrian_r_trigger"),
                *f.get_service_zone("barrier_trigger"),
                *f.get_service_zone("cyb_p_02_trigger"),
                *f.get_service_zone("cyb_p_04_trigger"),
            ]
            if self.check_robot_in_zones(check_zones):
                return False

            for cyb in self.cyb_status:
                if cyb == "active":
                    return False

            self.cyb_status["CybP_01"] = "active"
            self.mission_vars["ap_code_hash"] = f.gen_uid(20)
            self.panel_mission_data.events.append(
                {"m_type": 3, "message": "КП (CybP_01) активировано: Компрометация кода автопилота"}
            )
            self.context.lg.warn("КП (CybP_01) активировано: Компрометация кода автопилота")
            self.panel_mission_data.sec_domains["autopilot"] = "bad"
            self.panel_mission_data.sec_targets["CybP_01"] = "running"

            def stop_cyb_01():
                if not self.mission_vars["ap_reboot"]:
                    self.mission_vars["burn_electric_schemes"] = True
                    self.context.lg.error("КП (CybP_01) сработало: Автопилот сгорел, кулхацкеры победили(")
                else:
                    self.panel_mission_data.sec_domains["autopilot"] = "good"
                    self.panel_mission_data.sec_targets["CybP_01"] = "done"
                    self.mission_vars["ap_code_hash"] = self.mission_vars["ap_original_code_hash"]
                self.cyb_status["CybP_01"] = "done"

                return True

            self.once(5, callback=stop_cyb_01)

            return True

        def run_cyb_02():
            check_zones = [*f.get_service_zone("cyb_p_02_trigger")]
            if not self.check_robot_in_zones(check_zones):
                return False

            for cyb in self.cyb_status:
                if cyb == "active":
                    return False

            self.cyb_status["CybP_02"] = "active"
            self.panel_mission_data.events.append(
                {"m_type": 3, "message": "КП (CybP_02) активировано: Неполадки системы связи"}
            )
            self.context.lg.warn("КП (CybP_02) активировано: Неполадки системы связи")
            self.panel_mission_data.sec_domains["network"] = "bad"
            self.panel_mission_data.sec_targets["CybP_02"] = "running"

            def stop_cyb_02():
                self.cyb_status["CybP_02"] = "done"
                self.panel_mission_data.sec_domains["network"] = "good"
                self.panel_mission_data.sec_targets["CybP_02"] = "done"
                self.context.lg.log("КП (CybP_02) деактивировано: Система связи работает штатно")

                return True

            self.once(5, callback=stop_cyb_02)

            return True

        def run_cyb_03():
            check_zones = [
                *f.get_service_zone("pedestrian_l_trigger"),
                *f.get_service_zone("pedestrian_r_trigger"),
                *f.get_service_zone("barrier_trigger"),
                *f.get_service_zone("cyb_p_02_trigger"),
                *f.get_service_zone("cyb_p_04_trigger"),
            ]
            if self.check_robot_in_zones(check_zones):
                return False

            for cyb in self.cyb_status:
                if cyb == "active":
                    return False

            self.cyb_status["CybP_03"] = "active"
            self.mission_vars["current_malfunction_drive_id"] = randint(0, 3)
            self.panel_mission_data.events.append(
                {
                    "m_type": 3,
                    "message": f"КП (CybP_03) активировано: Компрометация кода приводов "
                    f"({self.mission_vars['current_malfunction_drive_id']})",
                }
            )
            self.context.lg.warn(
                f"КП (CybP_03) активировано: Компрометация кода приводов ({self.mission_vars['current_malfunction_drive_id']})"
            )
            self.mission_vars["drive_info"][self.mission_vars["current_malfunction_drive_id"]]["signature"] = f.gen_uid(
                12
            )
            self.panel_mission_data.sec_domains["motors"] = "bad"
            self.panel_mission_data.sec_targets["CybP_03"] = "running"

            def stop_cyb_02():
                self.cyb_status["CybP_03"] = "done"
                self.panel_mission_data.sec_domains["motors"] = "good"
                self.panel_mission_data.sec_targets["CybP_03"] = "done"

                return True

            self.once(10, callback=stop_cyb_02)

            return True

        def run_cyb_04():
            check_zones = [*f.get_service_zone("cyb_p_04_trigger")]
            if not self.check_robot_in_zones(check_zones):
                return False

            for cyb in self.cyb_status:
                if cyb == "active":
                    return False

            self.cyb_status["CybP_04"] = "active"
            self.panel_mission_data.events.append(
                {"m_type": 3, "message": "КП (CybP_04) активировано: Компрометация системы навигации"}
            )
            self.context.lg.warn("КП (CybP_02) активировано: Компрометация системы навигации")
            self.panel_mission_data.sec_domains["navigation"] = "bad"
            self.panel_mission_data.sec_targets["CybP_04"] = "running"

            def stop_cyb_04():
                stop_check_zones = [*f.get_service_zone("cyb_p_04_trigger")]
                if self.check_robot_in_zones(stop_check_zones):
                    return False

                self.cyb_status["CybP_04"] = "done"
                self.panel_mission_data.sec_domains["navigation"] = "good"
                self.panel_mission_data.sec_targets["CybP_04"] = "done"

                return True

            self.once(5, callback=stop_cyb_04)

            return True

        if self.cybs["CybP_01"]:
            self.once(duration=randint(40, 110), callback=run_cyb_01)

        if self.cybs["CybP_02"]:
            self.once(0, callback=run_cyb_02)

        if self.cybs["CybP_03"]:
            self.once(duration=randint(10, 15), callback=run_cyb_03)

        if self.cybs["CybP_04"]:
            self.once(0, callback=run_cyb_04)

    def update_polygon_state(self):
        def set_pedestrian_l_state():
            if self.check_robot_in_zones(f.get_service_zone("pedestrian_l_trigger"), frame=False):
                if not self.mission_vars["pedestrian_l_active"]:
                    self.mission_vars["pedestrian_l_active"] = True
                    self.context.spd.pedestrians[0].state = 1

                    def reset_pedestrian_l_state():
                        self.context.spd.pedestrians[0].state = 0

                    self.once(4, reset_pedestrian_l_state)
            else:
                self.mission_vars["pedestrian_l_active"] = False

        def set_pedestrian_r_state():
            if self.check_robot_in_zones(f.get_service_zone("pedestrian_r_trigger"), frame=False):
                if not self.mission_vars["pedestrian_r_active"]:
                    self.mission_vars["pedestrian_r_active"] = True
                    self.context.spd.pedestrians[1].state = 1

                    def reset_pedestrian_r_state():
                        self.context.spd.pedestrians[1].state = 0

                    self.once(4, reset_pedestrian_r_state)
            else:
                self.mission_vars["pedestrian_r_active"] = False

        def set_slip_status():
            if self.check_robot_in_zones(f.get_zone("slip")):
                self.mission_vars["slip_direction"] = choice([90, -90])
            else:
                self.mission_vars["slip_direction"] = 0

        def set_base_stations_rssi():
            self.mission_vars["base_station_alpha_rssi"] = f.get_points_range(
                (2.0, 2.0), (self.context.robots.current_robot.chassis.x, self.context.robots.current_robot.chassis.y)
            )

            self.mission_vars["base_station_bravo_rssi"] = f.get_points_range(
                (1.0, 3.0), (self.context.robots.current_robot.chassis.x, self.context.robots.current_robot.chassis.y)
            )

            self.mission_vars["base_station_charlie_rssi"] = f.get_points_range(
                (1.4, 1.9), (self.context.robots.current_robot.chassis.x, self.context.robots.current_robot.chassis.y)
            )

        def set_traffic_lights_status():
            for i in range(3):
                if time.time() - self.context.spd.t_lights[i].last_update_time > 10:
                    if randint(0, 10) > 5:
                        self.context.spd.t_lights[i].color = 1 if self.context.spd.t_lights[i].color == 2 else 2
                    self.context.spd.t_lights[i].last_update_time = time.time()

        def set_barrier_status():
            color = 1
            if self.context.mission.check_robot_in_zones(f.get_service_zone("barrier_trigger")):
                color = 4
            if self.context.spd.barrier.state == 1:
                color = 2
            self.context.spd.barrier.color = color

        set_pedestrian_l_state()
        set_pedestrian_r_state()
        set_slip_status()
        set_base_stations_rssi()
        set_traffic_lights_status()
        set_barrier_status()

    def update_cybs_state(self):
        def set_drive_info():
            for i in range(0, 4):
                c_hash = crc8.crc8()
                mock_data = str(randint(0, 255))
                if self.cyb_status["CybP_03"] == "active" and i == self.mission_vars["current_malfunction_drive_id"]:
                    c_hash.update(bytes(str(f.gen_uid(20) + mock_data).encode("utf-8")))
                    signature = c_hash.hexdigest()
                else:
                    c_hash.update(bytes(str(self.mission_vars["drive_info"][i]["serial"] + mock_data).encode("utf-8")))
                    signature = c_hash.hexdigest()
                n_data = {
                    "d_id": i,
                    "data": mock_data,
                    "serial": self.mission_vars["drive_info"][i]["serial"],
                    "signature": signature,
                }
                self.mission_vars["drive_info"][i] = n_data

        set_drive_info()

    def make_short_message(self):
        c_hash = crc8.crc8()
        if self.context.mission.cyb_status["CybP_02"] == "active":
            result = "do_move({'x': 'azazaza', 'y': 'kekekkeke'})"
        else:
            c_hash.update(bytes(self.context.mission.mission_vars["last_short_message"].encode("utf-8")))
            result = c_hash.hexdigest()

        return result

    def reboot_drive(self, d_id):
        if self.cyb_status["CybP_03"] == "active":
            if self.mission_vars["current_malfunction_drive_id"] == d_id:
                self.panel_mission_data.events.append(
                    {"m_type": 2, "message": f"ДМ запросил перезагрузку привода {d_id} - выполняется"}
                )
                self.context.lg.warn(f"ДМ запросил перезагрузку привода {d_id} - выполняется")
                self.mission_vars["current_malfunction_drive_id"] = 99
                self.cyb_status[f"CybP_03"] = "done"
            else:
                self.panel_mission_data.events.append(
                    {"m_type": 2, "message": f"ДМ запросил перезагрузку привода {d_id} - и так здоров"}
                )
                self.context.lg.warn(f"ДМ запросил перезагрузку привода {d_id} - и так здоров")

    def reboot_ap(self):
        self.context.lg.warn(f"ДМ запросил перезагрузку автопилота - выполняется.")
        self.panel_mission_data.events.append(
            {"m_type": 2, "message": f"ДМ запросил перезагрузку автопилота - выполняется."}
        )
        self.send_robot_request("emergency_stop")
        self.mission_vars["ap_reboot"] = True
