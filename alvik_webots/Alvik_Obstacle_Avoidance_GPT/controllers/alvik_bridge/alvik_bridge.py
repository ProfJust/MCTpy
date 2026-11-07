"""Start the shared program and attach simulation-only drawing and tests."""
from pathlib import Path
import runpy
import sys
import time
from controller import Supervisor
import arduino_alvik
import micropython_time
from beams import Beams

arduino_alvik.Robot = Supervisor
original_begin = arduino_alvik.ArduinoAlvik.begin


def begin_with_display(self):
    original_begin(self)
    self._display = Beams(self)
    self._display.update()
    if '--test' in sys.argv:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'validation'))
        from simulation_probe import Probe
        self._observer = Probe(self)


arduino_alvik.ArduinoAlvik.begin = begin_with_display
previous = {name:getattr(time,name,None) for name in micropython_time.FUNCTIONS}
for name, function in micropython_time.FUNCTIONS.items():
    setattr(time,name,function)
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
try:
    runpy.run_path(str(Path(__file__).resolve().parents[2]/'robot_code/main.py'),run_name='__main__')
except arduino_alvik.SimulationEnded:
    pass
finally:
    if arduino_alvik._active is not None:
        arduino_alvik._active.stop()
    for name,function in previous.items():
        if function is None:
            delattr(time,name)
        else:
            setattr(time,name,function)
