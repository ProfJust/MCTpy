"""Small software checks. Real Webots results are recorded separately."""
from pathlib import Path
import ast
import importlib.util
import math
import re
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'controllers/alvik_bridge'))
from beams import Beams, cylinder_pose

api = types.ModuleType('arduino_alvik')
api.ArduinoAlvik = object
sys.modules['arduino_alvik'] = api
import time
time.sleep_ms = lambda ms: None
time.ticks_ms = lambda: 0
time.ticks_diff = lambda a,b: a-b
spec = importlib.util.spec_from_file_location('behaviour', ROOT/'robot_code/main.py')
behaviour = importlib.util.module_from_spec(spec)
spec.loader.exec_module(behaviour)


class FakeAlvik:
    def __init__(self):
        self.pose = (0,0,0)
        self.command = None
    def get_pose(self): return self.pose
    def drive(self,v,w): self.command = (v,w)
    def brake(self): self.command = (0,0)


class ControllerTests(unittest.TestCase):
    def test_original_centroid_examples(self):
        for values, expected in [((50,300,50),0),((800,200,0),.8),((0,200,800),-.8),((0,0,0),0)]:
            self.assertAlmostEqual(behaviour.calculate_center(*values),expected)

    def test_short_way_across_heading_wrap(self):
        self.assertEqual(behaviour.angle_error(5,355),10)
        self.assertEqual(behaviour.angle_error(355,5),-10)

    def test_clearer_side_is_chosen_and_retained(self):
        a=FakeAlvik(); n=behaviour.Detour(a)
        n.start((9,10,11,350,350))
        self.assertEqual(n.side,-1)
        n.start((350,350,11,10,9))
        self.assertEqual(n.side,1)
        n.start((350,350,11,350,350))
        self.assertEqual(n.side,1)

    def test_zero_range_requests_backoff(self):
        n=behaviour.Detour(FakeAlvik()); n.start((350,350,0,350,350))
        self.assertEqual(n.state,'BACKOFF')

    def test_no_immediate_rejoin_on_original_tape(self):
        a=FakeAlvik(); n=behaviour.Detour(a); n.start((350,350,11,350,350))
        n.state='REJOIN'; n.off_line=False
        n.step((0,900,0),(350,)*5)
        self.assertEqual(n.state,'REJOIN')

    def test_rejoin_restores_forward_heading(self):
        a=FakeAlvik(); n=behaviour.Detour(a); n.start((350,350,11,350,350))
        n.state='ALIGN'; a.pose=(30,0,180)
        n.step((0,900,0),(350,)*5)
        self.assertEqual(n.state,'ALIGN')
        a.pose=(30,0,0)
        n.step((0,900,0),(350,)*5)
        self.assertEqual(n.state,'FOLLOW')
        self.assertEqual(n.rejoins,1)

    def test_stop_still_advances_time(self):
        waits=[]; previous=behaviour.sleep_ms
        behaviour.sleep_ms=waits.append
        try:
            n=behaviour.Detour(FakeAlvik()); n.state='STOP'
            n.step((0,0,0),(350,)*5)
            self.assertEqual(waits,[50])
        finally: behaviour.sleep_ms=previous

    def test_all_five_beams_point_forward_from_same_origin(self):
        origin=(.0394,0,.0275)
        for degrees in (40,20,0,-20,-40):
            direction=(math.cos(math.radians(degrees)),math.sin(math.radians(degrees)),0)
            center,rotation=cylinder_pose(origin,direction,.30)
            x,y,z,angle=rotation
            # Independently rotate native +Z with Rodrigues' rotation formula.
            c,s=math.cos(angle),math.sin(angle)
            actual=(y*s+x*z*(1-c),-x*s+y*z*(1-c),c+z*z*(1-c))
            for j in range(3):
                self.assertAlmostEqual(actual[j],direction[j])
                self.assertAlmostEqual(center[j]-.15*actual[j],origin[j])
            self.assertGreater(actual[0],0)
            self.assertAlmostEqual(actual[2],0)

    def test_vertical_extremes_have_valid_rotation(self):
        for direction,expected in [((0,0,1),0),((0,0,-1),math.pi)]:
            _,r=cylinder_pose((0,0,0),direction,.3)
            self.assertEqual(r[3],expected)

    def test_drawn_beams_start_at_the_active_range_sensors(self):
        proto=(ROOT/'protos/Alvik.proto').read_text()
        pattern=r'DistanceSensor\s*\{\s*translation\s+([\d.eE+ -]+)\s+rotation\s+[^}]+?name\s+"tof_[^"]+"'
        origins=[tuple(map(float,p.split())) for p in re.findall(pattern,proto)]
        self.assertEqual(len(origins),5)
        tree=ast.parse((ROOT/'controllers/alvik_bridge/beams.py').read_text())
        drawn=next(ast.literal_eval(n.args[0]) for n in ast.walk(tree)
                   if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)
                   and n.func.id=='enumerate' and isinstance(n.args[0],ast.Tuple))
        self.assertTrue(all(p==drawn for p in origins))

    def test_assumed_mass_is_inside_the_wheel_ball_support_triangle(self):
        proto=(ROOT/'protos/Alvik.proto').read_text()
        ball=re.search(r'translation\s+([-\d.]+) 0 0.0045 children \[ Sphere',proto)
        self.assertIsNotNone(ball)
        rear_x=float(ball.group(1))
        self.assertLess(rear_x,0)
        mass=re.search(r'centerOfMass \[ ([\d.eE+ -]+) \]',proto)
        x,y,z=map(float,mass.group(1).split())
        fraction=x/rear_x
        self.assertGreater(fraction,0)
        self.assertLess(fraction,1)
        self.assertLess(abs(y),(1-fraction)*.04475)

    def test_behaviour_has_no_privileged_simulator_access(self):
        tree=ast.parse((ROOT/'robot_code/main.py').read_text())
        calls={n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)}
        self.assertFalse(calls.intersection({'getSelf','getFromDef','getPosition','getOrientation','setSFVec3f'}))

    def test_display_uses_valid_label_slots(self):
        class Field:
            def setSFVec3f(self, value): pass
            def setSFRotation(self, value): pass
            def setSFFloat(self, value): pass
        class DrawingRobot:
            def __init__(self): self.labels = []
            def getSelf(self): return self
            def getFromDef(self, name): return self
            def getField(self, name): return Field()
            def getTime(self): return 1.
            def getPosition(self): return [0.,0.,0.]
            def getOrientation(self): return [1.,0.,0.,0.,1.,0.,0.,0.,1.]
            def setLabel(self, identifier, text, *args):
                if not 0 <= identifier <= 99:
                    raise ValueError('Webots R2025a label identifier outside 0..99')
                self.labels.append((identifier,text))
        robot = DrawingRobot()
        ranges = [99.,0.,350.,10.,float('nan')]
        alvik = types.SimpleNamespace(robot=robot,_keys=set(),tof=[
            types.SimpleNamespace(getValue=lambda value=value:value) for value in ranges])
        Beams(alvik).update()
        self.assertEqual([identifier for identifier,text in robot.labels],[0,1])
        for text in ('99.0','0.0','MAX','--'):
            self.assertIn(text,robot.labels[0][1])


if __name__ == '__main__': unittest.main()
