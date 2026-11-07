# Alvik model layout — 3 November 2026

This revision corrects the visible orientation and reconstructs the missing optical components. `model_preview.png` shows actual Webots renders of the revised model. Dimensions below are metres in the PROTO and millimetres in this document. +X is forward, +Y left and +Z up; the origin is midway between the wheels at nominal floor level.

## What the real underside contains

Arduino's Alvik User Manual, topology table, specifies **three phototransistors and four infrared LEDs** for the line follower. The three receivers provide left/centre/right measurements. The four LEDs illuminate the floor; they do not create four extra line-reading channels. The underside also exposes the main PCB with the colour sensor and IMU. The front has **one** VL53L7CX multizone ToF package. The five red simulation lines represent five range regions, rather than five physical ToF modules.

Official references, checked 3 November 2026:

- Manual, topology and bottom-view illustrations: https://docs.arduino.cc/resources/datasheets/AKX00066-datasheet.pdf (topology on PDF page 9; underside photo on page 13 in the checked revision).
- Official product gallery, including underside and front photographs: https://store.arduino.cc/products/alvik
- Hardware page and reference STEP download: https://docs.arduino.cc/hardware/alvik

## Changes in this revision

- Rotated the mechanical shell and top PCB by 180 degrees around Z. Their front opening now faces the sensor rays; the Nano is above the front PCB/window area.
- Moved both the visible ball and its collision support to the rear. Reversed the assumed centre-of-mass X offset to keep it within the rear-supported wheel/ball triangle.
- Opened the simplified shell's front and underside optical windows. The visible shell mesh was remeshed from the supplied `Alvik_body.step` from the earlier project, with added visual cuts. These are reconstructed openings, not newly measured manufacturer CAD features.
- Added an alternating row of four light emitter packages and three dark receiver packages, a single front ToF package, front PCB graphics and an underside PCB with colour-sensor/IMU/reset details. Small electronic packages are simplified visual geometry, without added collision shapes or new active API sensors.
- Moved the three active downward optical origins to the visible receiver row and moved the five front range origins to just ahead of the reconstructed ToF package. The red beam drawing uses the same new origin.
- Each downward reading now samples a small nine-ray cone (0.8 rad aperture, roughly 2.5 mm footprint at 3 mm height). This replaces an infinitesimal point sample, which left narrow blind gaps between the wider-spaced receivers on the 15 mm tape. This footprint is a simulation approximation, not a measured phototransistor response.
- Adjusted two geometric distances in the existing detour: the ToF-to-axle offset from 5.02 to 3.94 cm and the tape-crossing distance from 6.0 to 7.0 cm. The wider sensor row sees the tape earlier with its outer receiver during the 35-degree approach; the longer crossing brings the axle close to the tape before aligning. The two original line follower functions and the avoidance states are unchanged.

## Coordinates and confidence

| Element | Local position in mm | Basis / limitation |
| --- | --- | --- |
| Wheel axles | (0, +44.75, 16.9), (0, -44.75, 16.9) | Existing model, retained; loaded physical track/radius not measured |
| Rear ball centre | (-41.329, 0, 4.5) | Existing CAD offset reversed to agree with the photographed rear location; nominal 9 mm diameter matches Arduino's manual |
| Three line optical origins | (37.2, +16.2/0/-16.2, 3.0) | Plan-view spacing estimated from official underside photo using nominal chassis width; height remains provisional |
| Four emitter centres | (37.2, +24.3/+8.1/-8.1/-24.3, 6.0) | Alternating arrangement and count from photo/manual; package sizes and height approximate |
| Five ToF ray origins | (39.4, 0, 27.5) | Estimated recessed-front location, just ahead of the visible package; not a measured optical datum |
| Colour sensor / IMU visuals | Near (21.5, 0/+6, 28) | Approximate PCB/window placement only; not simulated devices in this version |

These estimates replace the earlier unverified layout; they are **not a dimensional certification**. The five-ray ToF approximation, IR reflectance lookup, mass, friction, simplified body collision box and fixed low-friction ball support remain approximations. The front and underside visual cuts do not change that collision box. Cosmetic white/black packages do not simulate the real illumination or phototransistor electronics.

To obtain a calibrated model, measure each optical centre relative to the axle, floor clearance, wheel track and loaded wheel radius on the physical Alvik. Adjust the sensor nodes and matching beam/detour distances together, then repeat the documented simulation checks before hardware testing.
