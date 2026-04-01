# Mechanical Package

## Included

- `enclosure.scad`: editable source for quick prototype enclosure iteration

## Export Guidance

Use OpenSCAD or FreeCAD to export:

- STL for 3D printing
- STEP for MCAD / injection mold workflow

Suggested shell split:

- Front shell with display lip
- Midframe for PCB and battery retention
- Back shell with antenna windows and service access

## Injection Mold Notes

- Use uniform nominal wall thickness near 1.2 mm
- Add draft to vertical faces
- Replace sharp internal edges with tool-friendly radii
- Separate cosmetic A-surface from snap features early
