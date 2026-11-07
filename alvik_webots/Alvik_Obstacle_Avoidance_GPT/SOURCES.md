# Sources and changes

Prepared 2 November 2026 for Webots R2025a and the configured Windows Python 3.15.2.

- The Alvik CAD meshes, wheel/joint model and supported API adapter were reused from the local Alvik_MicroPython_Starter baseline. Sensor centres, physical properties and five-ray ToF representation remain approximations; this work does not certify hardware accuracy.
- The two original follower functions were retained from the user's working Arduino example. Official example: https://github.com/arduino/arduino-alvik-mpy/blob/main/examples/demo/line_follower.py
- The installed Cyberbotics R2025a e-puck_line_demo.c was read. Its separation of line following, obstacle avoidance and line entering informed the structure; its side-sensor weights and C source were not copied into this controller. Source: https://github.com/cyberbotics/webots/blob/R2025a/projects/robots/gctronic/e-puck/controllers/e-puck_line_demo/e-puck_line_demo.c
- Device semantics: https://github.com/cyberbotics/webots/blob/R2025a/docs/reference/distancesensor.md
- Supervisor drawing and validation APIs: https://github.com/cyberbotics/webots/blob/R2025a/docs/reference/supervisor.md
- Cylinder orientation in the current z-up convention: https://cyberbotics.com/doc/guide/tutorial-5-compound-solid-and-physics-attributes

The new drawing uses ordinary visible cylinders and world-level fields. It is independent of optional sensor-ray rendering and private PROTO interfaces. Cylinder +Z is explicitly rotated into each ray direction. The drawing observer uses world pose only to place graphics; the transferable behaviour uses line/range readings and encoder odometry, not privileged object coordinates.

The package is a new project. The earlier project remains the reference baseline.

## Model revision — 3 November 2026

The original baseline geometry is superseded in this obstacle project by the orientation/optical-layout correction described in MODEL_LAYOUT.md. Arduino's official User Manual specifies three phototransistors and four infrared LEDs, rather than seven independent line readings: https://docs.arduino.cc/resources/datasheets/AKX00066-datasheet.pdf . The manufacturer's underside and front product photographs supplied the component arrangement: https://store.arduino.cc/products/alvik . The shell's added openings were reconstructed using FreeCAD from the earlier project's supplied Alvik_body.step. Shell/PCB rotation, rear support placement, photo-estimated active optical origins and the corresponding display/behaviour offsets were updated together. Fine electronics dimensions and optical heights remain estimates. The earlier starter project remains unchanged.

## Compatibility correction

Webots R2025a resources/nodes/IndexedFaceSet.wrl was checked directly: IndexedFaceSet defines ccw but no solid field. The model now uses ccw FALSE for its outward-facing decoration. Python selection follows Webots' Preferences without a runtime.ini COMMAND override, as described in https://github.com/cyberbotics/webots/blob/master/docs/guide/using-python.md and https://github.com/cyberbotics/webots/blob/master/docs/guide/preferences.md . The default image is resized to a power-of-two dimension. The custom course in the professor's screenshot is not included or overwritten by this change.
