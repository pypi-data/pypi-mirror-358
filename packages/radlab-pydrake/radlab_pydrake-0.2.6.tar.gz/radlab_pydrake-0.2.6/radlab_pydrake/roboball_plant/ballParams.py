from pathlib import Path
from importlib.resources import files

# Prefer this for long-term wheel-safe access:
URDF_DIR = files("radlab_pydrake.roboball_plant.roboball_urdf")

class RoboBall2Params:
    """
    Important Measurable Values for the Ball Plant
    NOT found in the URDF
    """
    def __init__(self):
        # Physical friction/damping values
        self.steer_dynamic_friction = 0.7
        self.steer_static_friction = 0.65
        self.steer_viscous_damping = 0.104

        # URDF paths (resolved within the installed package)
        self.package_path = str(URDF_DIR / "package.xml")
        self.robot_file = str(URDF_DIR / "RoboBall_URDF.urdf")
        self.lumpy_robot_file = str(URDF_DIR / "urdf" / "RoboBall_URDF_lumpy.urdf")
        self.shell_file = str(URDF_DIR / "urdf" / "RoboBall_shell.urdf")

        # Actuator gear ratios
        self.steerGearRatio = 9.0 * 50.0 / 30.0
        self.driveGearRatio = 9.0 * 3.0 * 50.0 / 30.0

        # Rotor inertia (from Derek's notes)
        self.NeoRotorInertia = 9.42e-4  # kg*m²
