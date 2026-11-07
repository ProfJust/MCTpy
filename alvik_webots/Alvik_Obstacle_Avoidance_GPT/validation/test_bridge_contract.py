import importlib.util
import math
import contextlib
import io
from pathlib import Path
import sys
import types
import runpy
import unittest

class Motor:
    def setPosition(self, value): self.position = value
    def setVelocity(self, value): self.velocity = value
    def getMaxVelocity(self): return 10.05
class Sensor:
    def __init__(self, value): self.value = value
    def enable(self, period): self.period = period
    def getValue(self): return self.value
class VectorSensor:
    def __init__(self, values): self.values = values
    def enable(self, period): self.period = period
    def getValues(self): return self.values
    def getRollPitchYaw(self): return self.values
class Keyboard:
    def __init__(self): self.keys = []
    def enable(self, period): self.period = period
    def getKey(self): return self.keys.pop(0) if self.keys else -1
class Robot:
    def __init__(self):
        self.keyboard = Keyboard()
        self.steps = []
        self.result = 0
        self.devices = {'left wheel motor': Motor(), 'right wheel motor': Motor(),
                        'gs0': Sensor(850), 'gs1': Sensor(575), 'gs2': Sensor(300)}
        self.devices.update({s+' wheel sensor': Sensor(0) for s in ('left','right')})
        self.devices.update({'tof_'+s: Sensor(v) for s,v in zip(
            ('left','center_left','center','center_right','right'), (10,20,30,40,50))})
        self.devices.update({'accelerometer': VectorSensor((0,0,9.81)),
                             'gyro': VectorSensor((0,0,.5)), 'inertial unit': VectorSensor((0,0,.2))})
    def getBasicTimeStep(self): return 10
    def getDevice(self, name): return self.devices.get(name)
    def getKeyboard(self): return self.keyboard
    def step(self, period): self.steps.append(period); return self.result
    def getTime(self): return sum(self.steps) / 1000
sys.modules['controller'] = types.SimpleNamespace(Robot=Robot)
path = Path(__file__).resolve().parents[1] / 'controllers/alvik_bridge/arduino_alvik.py'
sys.path.insert(0, str(path.parent))
spec = importlib.util.spec_from_file_location('bridge', path)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class Contract(unittest.TestCase):
    def setUp(self):
        bridge._active = None
        self.alvik = bridge.ArduinoAlvik()
        self.alvik.begin()
    def test_rpm_units_and_clipping(self):
        self.alvik.set_wheels_speed(30, -30)
        self.assertAlmostEqual(self.alvik.motors[0].velocity, math.pi)
        self.assertAlmostEqual(self.alvik.motors[1].velocity, -math.pi)
        self.alvik.set_wheels_speed(10000, -10000)
        self.assertEqual([m.velocity for m in self.alvik.motors], [10.05, -10.05])
        self.alvik.brake()
        self.assertEqual([m.velocity for m in self.alvik.motors], [0, 0])
    def test_sensor_order_polarity_and_bounds(self):
        self.assertEqual(self.alvik.get_line_sensors(), (0, 500, 1000))
        self.alvik.ground[0].value = -10
        self.alvik.ground[2].value = 2000
        self.assertEqual(self.alvik.get_line_sensors(), (1000, 500, 0))
    def test_delay_advances_simulation(self):
        before = len(self.alvik.robot.steps)
        bridge.sleep_ms(100)
        self.assertEqual(len(self.alvik.robot.steps) - before, 10)
        self.assertEqual(set(self.alvik.robot.steps), {10})
    def test_keyboard_cancel_survives_delay(self):
        self.alvik.keyboard.keys = [13]
        self.alvik._step()
        self.assertTrue(self.alvik.get_touch_ok())
        self.alvik.keyboard.keys = [32]
        self.alvik._step()
        self.alvik._step()
        self.assertFalse(self.alvik.get_touch_ok())
        self.assertTrue(self.alvik.get_touch_cancel())
        self.assertFalse(self.alvik.get_touch_cancel())
    def test_short_start_press_survives_delay(self):
        self.alvik.keyboard.keys = [13]
        self.alvik._step()
        bridge.sleep_ms(100)
        self.assertTrue(self.alvik.get_touch_ok())
        self.assertFalse(self.alvik.get_touch_ok())
    def test_alternative_keys_and_immediate_stop(self):
        self.alvik.keyboard.keys = [ord('R')]
        self.alvik._step()
        bridge.sleep_ms(50)
        self.assertTrue(self.alvik.get_touch_ok())
        self.alvik.set_wheels_speed(30, 30)
        self.alvik.keyboard.keys = [ord('X')]
        self.alvik._step()
        self.assertEqual([m.velocity for m in self.alvik.motors], [0, 0])
        bridge.sleep_ms(100)
        self.assertTrue(self.alvik.get_touch_cancel())
    def test_cancel_has_priority_over_start(self):
        self.alvik.keyboard.keys = [13, 32]
        self.alvik._step()
        bridge.sleep_ms(50)
        self.assertFalse(self.alvik.get_touch_ok())
        self.assertTrue(self.alvik.get_touch_cancel())
    def test_clean_reload(self):
        self.alvik.robot.result = -1
        with self.assertRaises(bridge.SimulationEnded): bridge.sleep_ms(100)
        self.alvik.stop()
    def test_shared_program_with_brief_start_stop_restart(self):
        class ScenarioRobot(Robot):
            def __init__(self): super().__init__(); self.history = []
            def step(self, period):
                super().step(period)
                tick = round(self.getTime() * 100)
                self.keyboard.keys = {222:[32], 262:[82], 322:[88]}.get(tick, [])[:]
                self.history.append((tick, [self.devices[s+' wheel motor'].velocity for s in ('left','right')]))
                return -1 if tick >= 380 else 0
        old_robot = bridge.Robot
        bridge.Robot = ScenarioRobot
        bridge._active = None
        saved_module = sys.modules.get('arduino_alvik')
        sys.modules['arduino_alvik'] = bridge
        import time
        names = ('sleep_ms','ticks_ms','ticks_diff')
        previous = {name:getattr(time,name,None) for name in names}
        time.sleep_ms = bridge.sleep_ms
        time.ticks_ms = lambda: round(bridge._active.robot.getTime()*1000)
        time.ticks_diff = lambda a,b:a-b
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                with self.assertRaises(bridge.SimulationEnded):
                    runpy.run_path(str(path.parents[2] / 'robot_code/main.py'), run_name='__main__')
            self.assertEqual(output.getvalue().count('[STOPPED]'), 2)
            history = bridge._active.robot.history
            first = [speeds for tick,speeds in history if 207<=tick<=218]
            pause = [speeds for tick,speeds in history if 224<=tick<=250]
            resume = [speeds for tick,speeds in history if 275<=tick<=315]
            final = [speeds for tick,speeds in history if 324<=tick<=370]
            self.assertTrue(first and any(s!=[0,0] for s in first))
            self.assertTrue(pause and all(s==[0,0] for s in pause))
            self.assertTrue(resume and any(s!=[0,0] for s in resume))
            self.assertTrue(final and all(s==[0,0] for s in final))
        finally:
            bridge.Robot = old_robot
            if saved_module is None: sys.modules.pop('arduino_alvik', None)
            else: sys.modules['arduino_alvik'] = saved_module
            for name,value in previous.items():
                if value is None: delattr(time,name)
                else: setattr(time,name,value)
    def test_tof_order_units_and_enabling(self):
        self.assertEqual(self.alvik.get_distance(), (10,20,30,40,50))
        self.assertEqual(self.alvik.get_distance('mm'), (100,200,300,400,500))
        self.assertAlmostEqual(self.alvik.get_distance('m')[2], .3)
        self.assertTrue(all(s.period == 10 for s in self.alvik.tof+self.alvik.encoders))
    def test_drive_turn_sign(self):
        self.alvik.drive(0, 30)
        l,r = [m.velocity for m in self.alvik.motors]
        self.assertLess(l,0); self.assertGreater(r,0)
        self.assertAlmostEqual(l,-r)
        self.alvik.drive(.05,0,linear_unit='m/s')
        self.assertAlmostEqual(self.alvik.motors[0].velocity,.05/.0169)
    def test_measured_speed_not_commanded_speed(self):
        self.alvik.set_wheels_speed(30,30)
        self.assertEqual(self.alvik.get_wheels_speed(), (0,0))
        for e in self.alvik.encoders: e.value = .01
        self.alvik._step()
        self.assertAlmostEqual(self.alvik.get_wheels_speed('rad/s')[0],1.)
        self.assertAlmostEqual(self.alvik.get_drive_speed()[0],1.69)
    def test_odometry_reset_and_units(self):
        for e in self.alvik.encoders: e.value=1.
        self.alvik._step()
        self.assertAlmostEqual(self.alvik.get_pose()[0],1.69)
        self.assertAlmostEqual(self.alvik.get_wheels_position()[0],180/math.pi)
        self.alvik.reset_pose(10,20,90)
        for e in self.alvik.encoders: e.value=2.
        self.alvik._step()
        x,y,t = self.alvik.get_pose()
        self.assertAlmostEqual(x,10); self.assertAlmostEqual(y,21.69); self.assertAlmostEqual(t,90)
    def test_arc_odometry(self):
        self.alvik.encoders[1].value=1
        self.alvik._step()
        angle=.0169/.0895
        x,y,t=self.alvik.get_pose('m','rad')
        self.assertAlmostEqual(t,angle)
        self.assertAlmostEqual(x,.0895/2*math.sin(angle))
        self.assertAlmostEqual(y,.0895/2*(1-math.cos(angle)))
    def test_missing_imu_and_unsupported_calls_fail_clearly(self):
        self.assertEqual(self.alvik.get_sim_imu()['acceleration_m_s2'],(0,0,9.81))
        self.alvik.gyro=None
        with self.assertRaises(NotImplementedError): self.alvik.get_sim_imu()
        with self.assertRaisesRegex(AttributeError,'API_COVERAGE'): self.alvik.get_battery_charge()
    def test_directional_buttons(self):
        self.alvik._keys={ord('W'),ord('A'),ord('C')}
        self.assertTrue(self.alvik.get_touch_up()); self.assertTrue(self.alvik.get_touch_left())
        self.assertTrue(self.alvik.get_touch_center()); self.assertTrue(self.alvik.get_touch_any())
        self.assertFalse(self.alvik.get_touch_right())
    def test_invalid_inputs_do_not_partially_command_motors(self):
        with self.assertRaises(ValueError): self.alvik.set_wheels_speed(30,float('nan'))
        self.assertEqual([m.velocity for m in self.alvik.motors],[0,0])
        with self.assertRaises(ValueError): self.alvik.drive(1,0,linear_unit='wrong')
    def test_tick_arithmetic(self):
        sys.modules['arduino_alvik']=bridge
        import micropython_time as clock
        period=clock.TICKS_PERIOD
        self.assertEqual(clock.ticks_diff(3,period-2),5)
        self.assertEqual(clock.ticks_diff(period-2,3),-5)
        self.assertEqual(clock.ticks_add(period-2,5),3)
        before=clock.ticks_ms()
        clock.sleep(.1)
        self.assertEqual(clock.ticks_diff(clock.ticks_ms(),before),100)
    def test_invalid_sensor_data_is_not_silently_converted(self):
        self.alvik.ground[0].value=float('nan')
        with self.assertRaisesRegex(RuntimeError,'ground'): self.alvik.get_line_sensors()
        self.alvik.accelerometer.values=(0,0,float('nan'))
        with self.assertRaisesRegex(RuntimeError,'IMU'): self.alvik.get_sim_imu()

unittest.main()
