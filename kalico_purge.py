## kalico_purge.py
# Kalico Addon Module: Adaptive Purge with Calibration Stubs

import os
import time
from kalico.addon import KalicoAddon
from kalico.util import kalico_macro
from logging import getLogger

logger = getLogger(__name__)

class KalicoPurge(KalicoAddon):
    def __init__(self, config):
        self.config = config
        self.default_length = float(config.get("default_length", 30.0))
        self.default_speed = float(config.get("default_speed", 1000.0))
        self.default_z_hop = float(config.get("default_z_hop", 0.3))
        self.blob_enabled = config.getboolean("enable_blob_mode", False)
        self.ext_test_enabled = config.getboolean("enable_ext_test", True)

    def register(self, context):
        self.context = context
        context.register_command("PURGE", self.cmd_purge)
        context.register_command("SET_PURGE_DEFAULTS", self.cmd_set_defaults)

    def cmd_purge(self, params):
        length = float(params.get("LENGTH", self.default_length))
        speed = float(params.get("SPEED", self.default_speed))
        z_hop = float(params.get("Z_HOP", self.default_z_hop))
        blob = int(params.get("BLOB", 0))
        ext_test = int(params.get("EXT_TEST", 0))

        x_start = params.get("X")
        y_start = params.get("Y")
        placement = params.get("PLACEMENT", "mesh_min")

        if x_start and y_start:
            x_pos, y_pos = float(x_start), float(y_start)
        elif placement == "mesh_min":
            x_pos, y_pos = self.get_mesh_min()
        elif placement == "mesh_max":
            x_pos, y_pos = self.get_mesh_max()
        elif placement == "front":
            x_min, y_min = self.get_mesh_min()
            x_max, _ = self.get_mesh_max()
            x_pos = (x_min + x_max) / 2
            y_pos = y_min - 5
        elif placement == "center_side":
            x_min, y_min = self.get_mesh_min()
            x_max, y_max = self.get_mesh_max()
            x_pos = x_min - 5
            y_pos = (y_min + y_max) / 2
        else:
            logger.warning("No valid purge position provided. Using default (0,0).")
            x_pos, y_pos = 0.0, 0.0

        logger.info(f"Starting PURGE at X={x_pos} Y={y_pos}: length={length}, speed={speed}, z_hop={z_hop}, blob={blob}, ext_test={ext_test}")

        if ext_test:
            self.run_ext_test(length, speed)

        if blob:
            self.run_blob_purge()
        else:
            self.run_line_purge(length, speed, z_hop, x_pos, y_pos)

        self.log_purge_run(length, speed, z_hop, x_pos, y_pos, blob, ext_test)

    def cmd_set_defaults(self, params):
        if "LENGTH" in params:
            self.config.set("default_length", str(params["LENGTH"]))
            self.default_length = float(params["LENGTH"])
        if "SPEED" in params:
            self.config.set("default_speed", str(params["SPEED"]))
            self.default_speed = float(params["SPEED"])
        if "Z_HOP" in params:
            self.config.set("default_z_hop", str(params["Z_HOP"]))
            self.default_z_hop = float(params["Z_HOP"])
        if "BLOB" in params:
            self.config.set("enable_blob_mode", str(bool(int(params["BLOB"]))))
            self.blob_enabled = bool(int(params["BLOB"]))
        logger.info("Updated kalico_purge defaults. Use SAVE_CONFIG to persist.")

    def run_line_purge(self, length, speed, z_hop, x, y):
        logger.info(f"Running linear purge from X={x}, Y={y}")
        gcode = self.context.lookup_object("gcode")
        script = f"""
SAVE_GCODE_STATE NAME=purge
G90
G1 Z{z_hop:.2f} F600
G1 X{x:.2f} Y{y:.2f} F6000
G1 Z0.28 F300
G1 X{x + length:.2f} E5 F{speed:.2f}
G1 Z{z_hop + 1:.2f} F300
RESTORE_GCODE_STATE NAME=purge
"""
        gcode.run_script(script)

    def run_ext_test(self, length, speed):
        logger.info("Running extrusion ramp test")
        pass

    def run_blob_purge(self):
        logger.info("Running blob-style purge")
        pass

    def log_purge_run(self, length, speed, z_hop, x, y, blob, ext_test):
        printer = self.context.lookup_object("printer")
        config_path = printer.lookup_object("configfile").get_file_path()
        log_dir = os.path.join(os.path.dirname(config_path), "kalico_purge")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "purge_log.csv")

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp},{x},{y},{length},{speed},{z_hop},{blob},{ext_test}\n"

        with open(log_path, "a") as f:
            f.write(log_line)

    def get_mesh_min(self):
        return (10.0, 10.0)

    def get_mesh_max(self):
        return (190.0, 190.0)

def load_config(config):
    return KalicoPurge(config)
