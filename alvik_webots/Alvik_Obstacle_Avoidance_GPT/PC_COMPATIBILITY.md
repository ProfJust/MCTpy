# PC compatibility correction — 3 November 2026

## Red model error

The earlier Alvik.proto contained `solid FALSE` in the decorative face's IndexedFaceSet. Webots R2025a's IndexedFaceSet does not define a `solid` field. This was a model authoring error, unrelated to collision meshes, physical support, sensor range or the professor's PC. The corrected file uses the supported `ccw FALSE` setting to orient that decorative face outward.

## Yellow texture warning

The 1600 x 1600 track image was automatically enlarged by Webots to 2048 x 2048. This is a texture-size warning. The supplied image is now already 2048 x 2048, with the original course preserved through nearest-neighbour resizing. The world, navigation code, sensor origins and collision shapes have not changed in this correction.

## Python on another PC

The previous controller/runtime.ini also contained an absolute Python path from the author's PC. This was not the red error shown in the screenshot, but would cause a separate launch problem on a different computer. The corrected runtime.ini has no COMMAND override. In Webots, open Tools > Preferences > General and select the local Python executable under Python command. Use a locally installed compatible Python 3; this project was exercised with Python 3.15.2 and Webots R2025a. Restart/reload the world after changing it. The screenshot's simulation time is still zero, so it does not demonstrate whether the Python controller has launched.

## Keep an existing customised course

If you or your professor changed the course, copy only these two files from the updated project into the matching directories of that existing project:

1. protos/Alvik.proto
2. controllers/alvik_bridge/runtime.ini

Keep the existing worlds/*.wbt and worlds/textures/line.png. The yellow texture warning can safely remain while testing. To remove it for that custom course too, resize that existing image to 2048 x 2048 in an image editor, preserving its aspect ratio and saving under the same name. Do not replace a custom course image with the default course supplied here.

References:

- Installed Webots R2025a resources/nodes/IndexedFaceSet.wrl (supported field schema).
- https://www.cyberbotics.com/doc/reference/indexedfaceset
- https://github.com/cyberbotics/webots/blob/master/docs/guide/using-python.md
- https://github.com/cyberbotics/webots/blob/master/docs/guide/preferences.md
