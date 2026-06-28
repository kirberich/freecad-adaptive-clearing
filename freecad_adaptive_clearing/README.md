# FreeCAD's adaptive clearing algorithm as a standalone python library

Allows access for FreeCAD's adaptive clearing algorithm without having to build the entirety of FreeCAD or rely on specific pre-installed python bindings.
NOTE: If you have FreeCAD installed and you're happy to use the same python version, you can simply use FreeCAD's built-in bindings directly. I only created this because packaging and versioning difficulties made it easier to only compile the required parts of FreeCAD on demand.

This repo is a fork of FreeCAD for simplicity's sake, but no change to FreeCAD are made in here. See README_FREECAD.md for FreeCAD's original readme.

The only difference to FreeCAD is the freecad_adaptive_clearing folder which contains the python bindings.

## Build

The library can be compiled by pip-installing it, or built manually with cmake.

### Manual CMake build
Requires C++20 and CMake 3.14+.

```bash
cd freecad_adaptive_clearing
mkdir build && cd build
cmake .. && cmake --build .
```

## Usage Example

```python
from freecad_adaptive_clearing import Adaptive2d, MotionType, OperationType

a2d = Adaptive2d(
    tool_diameter=5.0,
    step_over_factor=0.20,
    tolerance=0.1,
    stock_to_leave=0.0,
    force_inside_out=True,
    finishing_profile=True,
    op_type=OperationType.ClearingInside,
)

results = a2d.execute(
    stock_paths=[[(0, 0), (50, 0), (50, 50), (0, 50)]],
    boundary_paths=[[(5, 5), (45, 5), (45, 45), (5, 45)]],
)

for region in results:
    print(f"Cleared {region.cleared_area:.1f} mm^2")
    for motion_type, points in region.adaptive_paths:
        if motion_type == MotionType.Cutting:
            ...  # G1 moves at feed rate
        elif motion_type == MotionType.LinkClear:
            ...  # G0 moves at safe height
        elif motion_type == MotionType.LinkNotClear:
            ...  # G0 moves at clearance height
```
