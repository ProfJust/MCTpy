# Validation — corrected Alvik model

3 November 2026. Webots R2025a, Python 3.15.2. All runs below used the revised shell, rear ball support and revised optical origins.

**32 software checks passed:** 19 adapter contracts and 13 controller/display/geometry checks. The new geometry checks verify agreement between the active ToF origins and the drawn beam origin, and that the assumed centre of mass lies inside the wheel/ball support triangle.

Actual Webots physics runs, 65 simulated seconds each, randomSeed=42; obstacle contacts sampled every 10 ms.

| Scenario | Side | Rejoin | Heading at rejoin | Obstacle contacts | Result |
| --- | --- | --- | --- | --- | --- |
| center_final | LEFT | 28.17 s | -2.02° | 0 | passed |
| right_final | RIGHT | 27.17 s | 3.18° | 0 | passed |
| left_final | LEFT | 28.17 s | -2.02° | 0 | passed |
| wide_final | LEFT | 27.92 s | -2.05° | 0 | passed |
| cancel | STOP | — | — | 0 | passed |

A deliberate collision control generated 79 contact records, confirming that the contact observer worked after the support/model change.

Passing a driving run required exactly one rejoin, heading within 8 degrees of the original direction, tape detected throughout a four-second window after rejoin, and reaching world x > 0.65 m. The stop run required zero motor commands after settling and less than 1 mm position drift.

The front fan was checked in a separate rendered moving run. Front, top and underside renders of the final model were inspected with temporary cameras. These cameras and inspection/test worlds are excluded from the delivered demo.

The previous starter project and both original follower functions are unchanged. Two detour distances changed to account for the new sensor-to-axle offsets; the controller states are unchanged.

These finite deterministic trials are not a guarantee for arbitrary obstacles or physical hardware. MODEL_LAYOUT.md records the photo-based estimates and remaining model approximations.

To rerun software checks from this project root:

    python validation/test_controller.py
    python validation/test_bridge_contract.py

results.json records the current test events and geometry. The simulation probe is observation-only instrumentation selected by --test; privileged world pose/contact data is not provided to the navigation code.

## PC compatibility correction — 3 November 2026

Replaced the unsupported decorative IndexedFaceSet `solid FALSE` field with the supported `ccw FALSE`, resized the default texture to 2048 x 2048, and removed the author's absolute Python COMMAND override. Every behaviour/bridge Python file is byte-identical to the preceding revision. The IndexedFaceSet fields were explicitly checked against the installed R2025a node schema.

A copied project with no per-controller Python COMMAND override loaded and ran for five simulated seconds. The robot advanced from x=-0.65 m to about -0.496 m with no obstacle contacts. The controller used the locally resolved Python interpreter. This is a startup/driving check on this PC; the professor's interpreter setup and customised loop have not been tested here.

The four longer navigation trials above are retained as evidence from before this compatibility correction. They were not repeated after the small texture resampling change. See PC_COMPATIBILITY.md for applying only the model/runtime fix while preserving a custom world and course image.
