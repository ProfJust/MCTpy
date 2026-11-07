"""Five thick red, purely visual beams. No movement decisions or extra steps.

World-level geometry avoids dependencies on private PROTO field interfaces.
Supervisor pose is used ONLY for drawing, never by robot_code/main.py.
"""
import math


def cylinder_pose(origin, direction, length):
    """Position/orient a Webots +Z cylinder so its near end is at origin."""
    d = direction
    axis = (-d[1], d[0], 0.)
    norm = math.sqrt(sum(v*v for v in axis))
    rot = [v/norm for v in axis] + [math.acos(max(-1,min(1,d[2])))] if norm > 1e-9 else [1,0,0,0 if d[2]>0 else math.pi]
    return [origin[j]+.5*length*d[j] for j in range(3)], rot


class Beams:
    def __init__(self, alvik):
        self.alvik = alvik
        self.robot = alvik.robot
        self.body = self.robot.getSelf()
        self.last = -1
        self.visible = True
        self.old_keys = set()
        self.nodes = []
        for i in range(5):
            pose = self.robot.getFromDef('RAY_' + str(i))
            geometry = self.robot.getFromDef('RAY_GEOMETRY_' + str(i))
            if pose is None or geometry is None:
                raise RuntimeError('Open worlds/Alvik_Obstacle_Avoidance_GPT.wbt')
            self.nodes.append((pose.getField('translation'), pose.getField('rotation'), geometry.getField('height')))

    def update(self):
        keys = self.alvik._keys
        if (keys-self.old_keys).intersection((ord('V'), ord('v'))):
            self.visible = not self.visible
        self.old_keys = set(keys)
        now = self.robot.getTime()
        if now-self.last < .05-1e-9:
            return
        self.last = now
        p, r = self.body.getPosition(), self.body.getOrientation()
        origin = [p[j] + sum(r[3*j+k]*v for k,v in enumerate((.0394,0,.0275))) for j in range(3)]
        values = [s.getValue() for s in self.alvik.tof]
        for angle, cm, (translation, rotation, height) in zip((40,20,0,-20,-40), values, self.nodes):
            a = math.radians(angle)
            d = [r[3*j]*math.cos(a) + r[3*j+1]*math.sin(a) for j in range(3)]
            length = min(.35,max(.005,cm*.01)) if math.isfinite(cm) and 0 <= cm < 349.9 else .30
            center, rot = cylinder_pose(origin, d, length)
            translation.setSFVec3f(center)
            rotation.setSFRotation(rot)
            height.setSFFloat(length if self.visible else .00001)
        text = ' / '.join('--' if not math.isfinite(v) else 'MAX' if v>=349.9 else '%.1f'%v for v in values)
        # R2025a supports label IDs 0 through 99. These IDs are text slots, not ranges.
        self.robot.setLabel(0,'Front cm L / CL / C / CR / R: '+text,.02,.02,.035,0x203040,0,'Arial')
        self.robot.setLabel(1,'X stop | R start | V beams (ON by default) | drawn range capped at 35 cm',.02,.07,.025,0x203040,0,'Arial')
