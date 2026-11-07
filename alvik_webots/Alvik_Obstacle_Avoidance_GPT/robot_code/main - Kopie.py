"""Edit THIS file. Alvik line follower plus a short, measured detour.

Default course: small stationary block, no border walls. Units: cm and degrees.
The behaviour uses Alvik calls; Webots drawing lives in the bridge folder.
"""
from arduino_alvik import ArduinoAlvik
from time import sleep_ms, ticks_ms, ticks_diff
import math

AUTO_START = True           # Starts after two simulated seconds; X/Cancel stops.
TRIGGER_CM = 12.0
SIDE_OFFSET_CM = 12.0       # Axle centre offset, not the gap to the block.
OBJECT_DEPTH_CM = 8.0       # Assumed maximum depth for this first experiment.
TURN_OUT_DEG = 60.0
REJOIN_DEG = 35.0
LINE_SEEN = 180


def calculate_center(left: int, center: int, right: int):
    centroid = 0
    sum_weight = left + center + right
    sum_values = left + 2 * center + 3 * right
    if sum_weight != 0:
        centroid = sum_values / sum_weight
        centroid = 2 - centroid
    return centroid


def run_line_follower(alvik):
    kp = 50.0
    line_sensors = alvik.get_line_sensors()
    print(f' {line_sensors}')

    error = calculate_center(*line_sensors)
    control = error * kp

    if control > 0.2:
        alvik.left_led.set_color(1, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
    elif control < -0.2:
        alvik.left_led.set_color(1, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
    else:
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)

    alvik.set_wheels_speed(30 - control, 30 + control)
    sleep_ms(100)


def angle_error(target, current):
    return (target - current + 180) % 360 - 180


class Detour:
    def __init__(self, alvik):
        self.alvik = alvik
        self.state = 'FOLLOW'
        self.searches = 0
        self.rejoins = 0
        self.lost = 0

    def enter(self, state):
        self.state = state
        self.phase_pose = self.alvik.get_pose()
        self.phase_time = ticks_ms()
        print('[STATE]', state)

    def heading(self, target, speed=0):
        error = angle_error(target, self.alvik.get_pose()[2])
        self.alvik.drive(speed, max(-65, min(65, 4 * error)))
        return abs(error) < 3

    def travel(self):
        x, y, _ = self.alvik.get_pose()
        return math.sqrt((x-self.phase_pose[0])**2 + (y-self.phase_pose[1])**2)

    def coordinates(self):
        x, y, _ = self.alvik.get_pose()
        h = self.origin[2] * math.pi / 180
        dx, dy = x-self.origin[0], y-self.origin[1]
        return dx*math.cos(h)+dy*math.sin(h), -dx*math.sin(h)+dy*math.cos(h)

    def start(self, ranges):
        self.origin = self.alvik.get_pose()
        left = min(35, ranges[0]) + min(35, ranges[1])
        right = min(35, ranges[3]) + min(35, ranges[4])
        self.side = 1 if left >= right else -1  # Tie: pass on the left.
        self.offset = SIDE_OFFSET_CM
        self.pass_at = min(ranges[1:4]) + 3.94 + OBJECT_DEPTH_CM + 5
        self.inward = -self.side * REJOIN_DEG
        self.searches = 0
        self.off_line = False
        print('[AVOID] pass', 'LEFT' if self.side == 1 else 'RIGHT')
        self.enter('BACKOFF' if min(ranges[1:4]) < 5 else 'TURN_OUT')

    def step(self, line, ranges):
        front = min(ranges[1:4])
        if self.state == 'FOLLOW':
            if front < TRIGGER_CM:
                self.start(ranges)
            else:
                self.lost = self.lost + 1 if max(line) < LINE_SEEN else 0
                if self.lost >= 8:
                    self.enter('STOP')  # Includes the end of this finite tape.
                else:
                    run_line_follower(self.alvik)
                    return
        if self.state == 'STOP':
            self.alvik.brake()
            sleep_ms(50)
            return
        forward, lateral = self.coordinates()
        h = self.origin[2]
        self.off_line = self.off_line or max(line) < LINE_SEEN
        if ticks_diff(ticks_ms(), self.phase_time) > 15000:
            self.enter('STOP')
            self.alvik.brake()
            print('[STOP] manoeuvre timeout; inspect and reload the world')
            return
        if self.state not in ('TURN_OUT', 'TURN_PARALLEL', 'TURN_IN', 'ALIGN', 'BACKOFF') and front < 5:
            self.searches += 1
            if self.searches > 3:
                self.enter('STOP')
            else:
                self.offset += 4
                self.pass_at = max(self.pass_at, forward + 15)
                self.enter('BACKOFF')
        if self.state == 'BACKOFF':
            self.alvik.drive(-3, 0)
            if self.travel() >= 2:
                self.enter('TURN_OUT')
        elif self.state == 'TURN_OUT':
            if self.heading(h + self.side * TURN_OUT_DEG):
                self.enter('OUT')
        elif self.state == 'OUT':
            self.heading(h + self.side * TURN_OUT_DEG, 4)
            if self.side * lateral >= self.offset:
                self.enter('TURN_PARALLEL')
        elif self.state == 'TURN_PARALLEL':
            if self.heading(h):
                self.enter('PASS')
        elif self.state == 'PASS':
            self.heading(h, 5)
            if forward >= self.pass_at:
                self.enter('TURN_IN')
        elif self.state == 'TURN_IN':
            if self.heading(h + self.inward):
                self.enter('REJOIN')
        elif self.state == 'REJOIN':
            self.heading(h + self.inward, 3)
            if self.off_line and max(line) >= LINE_SEEN:
                self.enter('CROSS')
            elif abs(lateral) > self.offset + 3:
                self.searches += 1
                self.inward = -self.inward
                self.enter('TURN_IN' if self.searches <= 3 else 'STOP')
        elif self.state == 'CROSS':
            # Advance after the outer receiver first sees tape, then align the axle.
            self.heading(h + self.inward, 3)
            if self.travel() >= 7.0:
                self.enter('ALIGN')
        elif self.state == 'ALIGN':
            # Restore the pre-obstacle direction rather than following backwards.
            if self.heading(h):
                self.rejoins += 1
                self.lost = 0
                self.enter('FOLLOW')
                print('[REJOINED]', self.rejoins)
        if self.state == 'STOP':
            self.alvik.brake()
        sleep_ms(50)


def main():
    alvik = ArduinoAlvik()
    alvik.begin()
    detour = Detour(alvik)
    running = AUTO_START
    print('Starts in 2 seconds. X/Space: stop. R/Enter: start.')
    if AUTO_START:
        sleep_ms(2000)
    try:
        while True:
            if alvik.get_touch_cancel():
                running = False
                alvik.brake()
                print('[STOPPED] press R to continue; reload to reset position')
            if not running:
                if alvik.get_touch_ok():
                    running = True
                    detour.phase_time = ticks_ms()
                else:
                    sleep_ms(50)
                    continue
            line = alvik.get_line_sensors()
            ranges = alvik.get_distance()
            if not all(math.isfinite(v) and v >= 0 for v in ranges):
                raise RuntimeError('Invalid front range: inspect the sensor model')
            detour.step(line, ranges)
    finally:
        alvik.brake()
        alvik.stop()


if __name__ == '__main__':
    main()
