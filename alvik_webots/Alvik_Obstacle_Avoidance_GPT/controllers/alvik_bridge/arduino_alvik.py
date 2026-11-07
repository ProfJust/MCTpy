"""Bounded Webots implementation of the Alvik API; see API_COVERAGE.md.

Never upload this file to the robot: use its installed Arduino library there.
Ground mapping is inherited from the existing project, not hardware calibrated.
"""
import math
from controller import Robot
from alvik_extensions import AlvikExtensions, _SPEED, factor

GROUND_WHITE = 850.0
GROUND_BLACK = 300.0
_active = None


class SimulationEnded(BaseException):
    """Normal Webots termination, including Reload World."""


class _LED:
    # Existing PROTO has decorative shapes, not controllable LED devices.
    # Keep the requested colour available without pretending it is rendered.
    def __init__(self):
        self.color = (0, 0, 0)

    def set_color(self, red, green, blue):
        self.color = (red, green, blue)


class ArduinoAlvik(AlvikExtensions):
    def __init__(self):
        global _active
        if _active is not None:
            raise RuntimeError("This starter supports one ArduinoAlvik instance")
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.motors = [self._device(s + " wheel motor") for s in ("left", "right")]
        self.ground = [self._device("gs" + str(i)) for i in range(3)]
        self.keyboard = self.robot.getKeyboard()
        self.left_led, self.right_led = _LED(), _LED()
        self._keys = set()
        self._ok_pending = False
        self._cancel_pending = False
        self._input_hint_shown = False
        self._ended = False
        self._begun = False
        self._display = None
        self._observer = None
        self._command_rad_s = (0., 0.)
        self._setup_extensions()
        _active = self

    def _device(self, name):
        device = self.robot.getDevice(name)
        if device is None:
            raise RuntimeError("Missing Webots device: " + name)
        return device

    def begin(self):
        for motor in self.motors:
            motor.setPosition(float("inf"))
            motor.setVelocity(0)
        for sensor in self.ground:
            sensor.enable(self.timestep)
        self.keyboard.enable(self.timestep)
        self._enable_extensions()
        self._begun = True
        self._step()  # Obtain the first valid sensor sample before main.py runs.
        if self._encoder_angles is not None:
            self._step()  # A measured wheel speed requires two samples.
        print("ALVIK OBSTACLE GPT ready | select/click robot in 3D view", flush=True)
        print("Enter or R: OK/start | Space or X: Cancel/stop | received keys print [KEY]", flush=True)

    def _step(self):
        if self._ended or self.robot.step(self.timestep) == -1:
            self._ended = True
            raise SimulationEnded()
        self._sample_encoders()
        previous_keys = self._keys
        self._keys = set()
        raw_keys = []
        key = self.keyboard.getKey()
        while key != -1:
            self._keys.add(key & 0xFFFF)
            raw_keys.append(key)
            key = self.keyboard.getKey()
        new_keys = self._keys - previous_keys
        if new_keys:
            print("[KEY] raw=" + str(raw_keys) + " decoded=" + str(sorted(new_keys)), flush=True)
            self._input_hint_shown = True
        if new_keys.intersection((10, 13, ord("R"), ord("r"))):
            self._ok_pending = True
        if self._keys.intersection((ord(" "), ord("X"), ord("x"))):
            self._cancel_pending = True
            self._ok_pending = False
            self.brake()  # React during sleep_ms, before the next behaviour poll.
        if not self._input_hint_shown and self.robot.getTime() >= 3:
            print("[INPUT] Simulation is advancing, but no keys received. Select the robot,"
                  " click the 3D view and try R / X. Check that Webots is not paused.", flush=True)
            self._input_hint_shown = True

        if self._display is not None:
            self._display.update()
        if self._observer is not None:
            self._observer.step()

    def get_touch_ok(self):
        pressed = self._ok_pending or bool(self._keys.intersection((10, 13, ord("R"), ord("r"))))
        self._ok_pending = False
        return pressed

    def get_touch_cancel(self):
        pressed = self._cancel_pending or bool(self._keys.intersection((ord(" "), ord("X"), ord("x"))))
        self._cancel_pending = False
        return pressed

    def get_line_sensors(self):
        # Same ordering as Alvik: left, centre, right. Black high, white low.
        raw = self.get_line_raw()
        if not all(math.isfinite(value) for value in raw):
            raise RuntimeError("Invalid ground sensor reading")
        return tuple(round(max(0, min(1000, (GROUND_WHITE - s.getValue()) *
                        1000 / (GROUND_WHITE - GROUND_BLACK)))) for s in self.ground)

    def set_wheels_speed(self, left, right, unit="rpm"):
        conversion = factor(_SPEED, unit)
        if not all(math.isfinite(speed) for speed in (left, right)):
            raise ValueError("Wheel speed must be finite")
        for motor, speed in zip(self.motors, (left, right)):
            if not math.isfinite(speed):
                raise ValueError("Wheel speed must be finite")
            limit = motor.getMaxVelocity()
            motor.setVelocity(max(-limit, min(limit, speed * conversion)))
        self._command_rad_s = tuple(max(-motor.getMaxVelocity(), min(motor.getMaxVelocity(), speed*conversion))
                                   for motor, speed in zip(self.motors, (left, right)))

    def brake(self):
        if not self._ended:
            self.set_wheels_speed(0, 0)

    def stop(self):
        self.brake()


def sleep_ms(milliseconds):
    if _active is None or not _active._begun:
        raise RuntimeError("Call alvik.begin() before sleep_ms()")
    if milliseconds < 0:
        raise ValueError("sleep_ms requires a nonnegative duration")
    # Whole physics steps, rounded up. Supplied world uses 10 ms: 50 and 100 exact.
    steps = max(1, math.ceil(milliseconds / _active.timestep))
    for _ in range(steps):
        _active._step()
