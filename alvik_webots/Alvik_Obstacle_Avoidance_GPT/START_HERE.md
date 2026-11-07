# Alvik Obstacle Avoidance GPT

**Model update — 3 November 2026:** front/rear CAD orientation corrected, rear caster restored, and the underside now shows three receivers plus four infrared emitters. Open **model_preview.png** for front/underside views. **MODEL_LAYOUT.md** explains the estimated sensor coordinates and remaining differences from physical hardware. The active sensors, beam origin and two detour distances were updated together and retested.

## Running on another PC

Set **Tools > Preferences > General > Python command** in Webots to that PC's Python executable. The project now uses that setting rather than a path tied to the author's PC. See **PC_COMPATIBILITY.md** for the professor's screenshot errors and how to apply this fix while keeping a customised track.

## Start here

1. Keep this entire folder together. Do not copy only the Python file or world.
2. In Webots, open **worlds/Alvik_Obstacle_Avoidance_GPT.wbt**. This is the only demo world.
3. Press **Play** if paused. The robot starts after two simulated seconds.
4. Watch it pass the green block, rejoin the tape and follow the gentle bend. It stops when the finite tape ends.

The five **red front beams are ON by default**. They follow the robot; no optional-rendering shortcut is needed. There are no upward ground-sensor posts in this project.

**X or Space:** stop. **R or Enter:** continue. **V:** hide/show front beams.
Click/select the robot and click the 3D view before using these keys. If a key is not received, use Webots' Pause button. Reload/reset the world for a fresh run at the starting position.

## The only behaviour file to edit

**robot_code/main.py** — about 200 lines including your original follower.

Start with its constants at the top:

| Setting | Default | Meaning |
| --- | --- | --- |
| AUTO_START | True | Start without needing a keyboard event |
| TRIGGER_CM | 12 | Begin the detour at a front reading below this distance |
| SIDE_OFFSET_CM | 12 | Detour axle offset from the original line direction; this is not the obstacle gap |
| OBJECT_DEPTH_CM | 8 | Assumed maximum front-to-back obstacle size for this first experiment |
| TURN_OUT_DEG | 60 | Initial outward turn |
| REJOIN_DEG | 35 | Shallow approach to the tape |

The existing kp=50 and 30±control rpm follower functions are preserved. The adapter and beam drawing live in controllers/alvik_bridge; leave those files alone for your first experiments.

## What avoidance does

It chooses the clearer side using L/CL versus CR/R readings, with a deterministic left-side choice on a tie. It keeps that choice throughout the detour. A 60-degree turn leads away from the tape, then the robot passes approximately parallel to its original heading and returns at 35 degrees.

On detecting tape again, it advances a short distance because the line sensors are ahead of the axle. It then restores the pre-obstacle heading before giving control back to the follower. This addresses the earlier wrong-direction rejoin problem. A very close front reading requests a short backoff. Search retries and individual manoeuvres are bounded.

## Read the beams correctly

These are display geometry for five simulated front range proxies, not five additional physical lasers. A beam ends at a detected range or the 35 cm drawing cap. MAX/no-hit readings use a 30 cm locator beam; they are not proof of free space. A reading such as 99 cm is valid. Missing/non-finite values show --, and invalid data stops motion rather than being treated as clear.

preview.png is an actual Webots render of the corrected front fan. The temporary camera used for that verification is not part of the demo robot.

## Scope of this first version

The supplied world has no border walls, one stationary block and a straight section around the obstacle, followed by a gentle bend. The default block is 6 cm deep, 5 cm wide and 6 cm tall. Five forward rays cannot continuously see an obstacle at the robot's side like the e-puck's lateral sensors can. This controller therefore uses encoder progress and the declared obstacle-depth assumption for its pass distance.

This is a tested starting experiment, not a general navigation system or a hardware-validated controller. Try one change at a time. For a deeper block, increase OBJECT_DEPTH_CM before testing; for a wider block, increase SIDE_OFFSET_CM. Check the full robot's clearance, not just the centre beam. The old project has not been modified.

Optional test details and results are under validation/. You do not need them to run the demo.
