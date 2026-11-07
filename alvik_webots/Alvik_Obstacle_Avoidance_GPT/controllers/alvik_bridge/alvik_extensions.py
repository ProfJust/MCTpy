"""Testable extensions backed by actual simulated devices; no dummy readings.

Geometry is the CURRENT MODEL geometry, not measured hardware calibration.
MicroPython firmware/IMU unit contracts are not asserted by this module.
"""
import math

WHEEL_RADIUS_M = 0.0169
WHEEL_TRACK_M = 0.0895
_DISTANCE = {"m": 1., "cm": .01, "mm": .001, "inch": .0254, "in": .0254}
_ANGLE = {"rad": 1., "deg": math.pi / 180, "rev": 2 * math.pi,
          "revolution": 2 * math.pi}
_SPEED = {"rad/s": 1., "deg/s": math.pi / 180,
          "rpm": math.pi / 30, "rev/s": 2 * math.pi}


def factor(table, unit):
    try:
        return table[unit]
    except KeyError:
        raise ValueError("Unsupported unit: " + str(unit)) from None


class AlvikExtensions:
    def _setup_extensions(self):
        if hasattr(self.robot, "getNumberOfDevices"):
            inventory = {self.robot.getDeviceByIndex(i).getName(): self.robot.getDeviceByIndex(i)
                         for i in range(self.robot.getNumberOfDevices())}
            self._optional = inventory.get
        else:
            self._optional = self.robot.getDevice  # Test doubles.
        self.encoders = [self._optional(side + " wheel sensor") for side in ("left", "right")]
        self.tof = [self._optional("tof_" + side) for side in
                    ("left", "center_left", "center", "center_right", "right")]
        self.accelerometer = self._optional("accelerometer")
        self.gyro = self._optional("gyro")
        self.inertial_unit = self._optional("inertial unit")
        self._encoder_previous = None
        self._encoder_angles = None
        self._wheel_rad_s = None
        self._pose = [0., 0., 0.]

    def _enable_extensions(self):
        for device in self.encoders + self.tof + [self.accelerometer, self.gyro, self.inertial_unit]:
            if device is not None:
                device.enable(self.timestep)

    def _sample_encoders(self):
        if any(sensor is None for sensor in self.encoders):
            return
        angles = tuple(sensor.getValue() for sensor in self.encoders)
        if not all(math.isfinite(v) for v in angles):
            raise RuntimeError("Wheel encoders are not ready or are invalid")
        self._encoder_angles = angles
        if self._encoder_previous is None:
            self._encoder_previous = angles
            return  # A speed estimate needs two samples, not an invented zero.
        increments = tuple(a - b for a, b in zip(angles, self._encoder_previous))
        self._encoder_previous = angles
        self._wheel_rad_s = tuple(v / (self.timestep / 1000) for v in increments)
        dl, dr = (v * WHEEL_RADIUS_M for v in increments)
        distance, turn = (dl + dr) / 2, (dr - dl) / WHEEL_TRACK_M
        heading = self._pose[2]
        if abs(turn) < 1e-10:
            self._pose[0] += distance * math.cos(heading)
            self._pose[1] += distance * math.sin(heading)
        else:
            radius = distance / turn
            self._pose[0] += radius * (math.sin(heading + turn) - math.sin(heading))
            self._pose[1] += radius * (math.cos(heading) - math.cos(heading + turn))
        self._pose[2] += turn

    def get_distance(self, unit="cm"):
        if any(sensor is None for sensor in self.tof):
            raise NotImplementedError("This robot model lacks the five ToF proxy rays")
        values = tuple(sensor.getValue() * .01 / factor(_DISTANCE, unit) for sensor in self.tof)
        if not all(math.isfinite(v) and v >= 0 for v in values):
            raise RuntimeError("Invalid ToF proxy reading")
        return values  # L, CL, C, CR, R. Max range is not proof of free space.

    def get_wheels_position(self, unit="deg"):
        if self._encoder_angles is None:
            raise RuntimeError("Wheel encoders missing or not sampled")
        return tuple(v / factor(_ANGLE, unit) for v in self._encoder_angles)

    def get_wheels_speed(self, unit="rpm"):
        if self._wheel_rad_s is None:
            raise RuntimeError("Measured wheel speed needs two encoder samples; call sleep_ms first")
        return tuple(v / factor(_SPEED, unit) for v in self._wheel_rad_s)

    def drive(self, linear_velocity, angular_velocity, linear_unit="cm/s", angular_unit="deg/s"):
        if not linear_unit.endswith("/s"):
            raise ValueError("Linear velocity unit must end in /s")
        v = linear_velocity * factor(_DISTANCE, linear_unit[:-2])
        w = angular_velocity * factor(_SPEED, angular_unit)
        if not all(math.isfinite(value) for value in (v, w)):
            raise ValueError("Drive velocities must be finite")
        self.set_wheels_speed((v - w * WHEEL_TRACK_M / 2) / WHEEL_RADIUS_M,
                              (v + w * WHEEL_TRACK_M / 2) / WHEEL_RADIUS_M, unit="rad/s")

    def get_drive_speed(self, linear_unit="cm/s", angular_unit="deg/s"):
        if not linear_unit.endswith("/s"):
            raise ValueError("Linear velocity unit must end in /s")
        left, right = self.get_wheels_speed("rad/s")
        v = WHEEL_RADIUS_M * (left + right) / 2
        w = WHEEL_RADIUS_M * (right - left) / WHEEL_TRACK_M
        return v / factor(_DISTANCE, linear_unit[:-2]), w / factor(_SPEED, angular_unit)

    def get_pose(self, distance_unit="cm", angle_unit="deg"):
        if self._encoder_angles is None:
            raise RuntimeError("Odometry needs wheel encoders")
        return (self._pose[0] / factor(_DISTANCE, distance_unit),
                self._pose[1] / factor(_DISTANCE, distance_unit),
                self._pose[2] / factor(_ANGLE, angle_unit))

    def reset_pose(self, x=0, y=0, theta=0, distance_unit="cm", angle_unit="deg"):
        values = [x * factor(_DISTANCE, distance_unit), y * factor(_DISTANCE, distance_unit),
                  theta * factor(_ANGLE, angle_unit)]
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Pose must be finite")
        self._pose = values  # Reset estimate, never teleport the simulated robot.

    def _touch(self, letter, special=None):
        codes = {ord(letter.upper()), ord(letter.lower())}
        if special is not None and hasattr(self.keyboard, special):
            codes.add(getattr(self.keyboard, special))
        return bool(self._keys.intersection(codes))

    def get_touch_up(self): return self._touch("W", "UP")
    def get_touch_down(self): return self._touch("S", "DOWN")
    def get_touch_left(self): return self._touch("A", "LEFT")
    def get_touch_right(self): return self._touch("D", "RIGHT")
    def get_touch_center(self): return self._touch("C")

    def get_touch_any(self):
        return (self._ok_pending or self._cancel_pending or
                bool(self._keys.intersection({10, 13, 32, 82, 114, 88, 120})) or
                any((self.get_touch_up(), self.get_touch_down(), self.get_touch_left(),
                     self.get_touch_right(), self.get_touch_center())))

    def get_line_raw(self):
        """Simulator diagnostic, not an asserted Arduino API call."""
        return tuple(sensor.getValue() for sensor in self.ground)

    def get_sim_imu(self):
        """Explicit simulator SI units. Not a drop-in Alvik IMU unit contract."""
        if any(d is None for d in (self.accelerometer, self.gyro, self.inertial_unit)):
            raise NotImplementedError("Open alvik_sensor_inspection.wbt to inspect the added IMU")
        values = {"acceleration_m_s2": tuple(self.accelerometer.getValues()),
                  "angular_velocity_rad_s": tuple(self.gyro.getValues()),
                  "orientation_rad": tuple(self.inertial_unit.getRollPitchYaw())}
        if not all(math.isfinite(v) for row in values.values() for v in row):
            raise RuntimeError("Simulated IMU is not ready or is invalid")
        return values

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        raise AttributeError("Alvik bridge does not implement '" + name +
                             "'. See API_COVERAGE.md; hardware features need a model and a verified contract.")
