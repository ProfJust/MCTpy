"""Test observer only. World pose and contacts are NOT given to the behaviour."""
from pathlib import Path
import json
import math
import sys
import builtins


class Probe:
    def __init__(self, alvik):
        self.alvik = alvik
        self.robot = alvik.robot
        self.body = self.robot.getSelf()
        self.obstacle = self.robot.getFromDef('OBSTACLE')
        self.samples = []
        self.contacts = []
        self.events = []
        self.last = -1
        self.captured = set()
        self.directory = Path(__file__).resolve().parent/'last_run'
        self.directory.mkdir(exist_ok=True)
        self.test_name = sys.argv[sys.argv.index('--test')+1]
        self.duration = 15. if self.test_name == 'collision_oracle' else 65.
        self.camera = alvik._optional('validation camera')
        if self.camera is not None:
            self.camera.enable(200)
        previous_print = builtins.print
        def record(*args, **kwargs):
            message = ' '.join(str(v) for v in args)
            if message.startswith(('[STATE]', '[AVOID]', '[REJOINED]', '[STOP')):
                self.events.append(dict(t=self.robot.getTime(),message=message,pose=self.alvik.get_pose()))
            previous_print(*args, **kwargs)
        builtins.print = record

    def step(self):
        t = self.robot.getTime()
        for mark in (1,10,18,26,38,50):
            if t >= mark and mark not in self.captured:
                self.captured.add(mark)
                image_path = str(self.directory/(self.test_name+'_%02d.png'%mark))
                if self.camera is not None:
                    self.camera.saveImage(image_path,100)
                else:
                    self.robot.exportImage(image_path,100)
        if t-self.last >= .1-1e-8:
            self.last = t
            p = self.body.getPosition()
            r = self.body.getOrientation()
            row = dict(t=round(t,3),position=p,heading=math.atan2(r[3],r[0]),
                       line=self.alvik.get_line_sensors(),raw_line=self.alvik.get_line_raw(),
                       ranges=self.alvik.get_distance(),command=self.alvik._command_rad_s,
                       odometry=self.alvik.get_pose())
            self.samples.append(row)
        # Observe the static block directly; contact node IDs need not name the other body.
        for c in self.obstacle.getContactPoints():
            self.contacts.append((t,c.point))
        if self.test_name == 'collision_oracle' and t >= 2:
            self.alvik.set_wheels_speed(30,30)  # Deliberately collide to validate this test oracle.
        if self.test_name == 'cancel':
            if 5 <= t < 5.02:
                self.alvik._cancel_pending = True
        if t >= self.duration:
            self.alvik.brake()
            result = dict(test=self.test_name,simulation_seconds=t,contacts=self.contacts,
                          last=self.samples[-1],samples=self.samples,events=self.events)
            (self.directory/(self.test_name+'.json')).write_text(json.dumps(result,indent=2))
            print('SIMULATION_PROBE '+json.dumps({k:v for k,v in result.items() if k!='samples'}),flush=True)
            self.robot.simulationQuit(0)
            import arduino_alvik
            raise arduino_alvik.SimulationEnded()
