"""Cooperative simulation clock for the supported MicroPython time API."""
import math
import arduino_alvik

# MicroPython tick arithmetic uses a power-of-two wrap interval.
# The interval here is an adapter convention, not a guarantee for every port.
TICKS_PERIOD = 1 << 30

def sleep(seconds):
    arduino_alvik.sleep_ms(math.ceil(seconds * 1000))

def _now():
    if arduino_alvik._active is None or not arduino_alvik._active._begun:
        raise RuntimeError("Simulation time requires alvik.begin() first")
    return arduino_alvik._active.robot.getTime()

def ticks_ms(): return round(_now() * 1000) % TICKS_PERIOD
def ticks_us(): return round(_now() * 1000000) % TICKS_PERIOD
def ticks_diff(new, old):
    return ((new - old + TICKS_PERIOD // 2) % TICKS_PERIOD) - TICKS_PERIOD // 2
def ticks_add(ticks, delta): return (ticks + delta) % TICKS_PERIOD

FUNCTIONS = dict(sleep=sleep, sleep_ms=arduino_alvik.sleep_ms, ticks_ms=ticks_ms,
                 ticks_us=ticks_us, ticks_diff=ticks_diff, ticks_add=ticks_add)
