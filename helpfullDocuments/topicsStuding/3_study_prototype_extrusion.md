# Day 3 — Continuous Extrusion Prototype and FDM Transition

## Objective

The objective of Day 3 was to begin the transition from the current syringe-based discrete deposition system to a continuous extrusion model compatible with FDM-style printing, while preserving the stability of the main backend.

Instead of modifying the production backend directly, the work focused on understanding how synchronized motion and extrusion behave in FDM systems and how this logic could be integrated into the existing architecture in the future.

---

# Main Conceptual Transition

The current syringe system is based on discrete deposition events:

```text
move()
deposit()
move()
deposit()
```

In contrast, FDM printing works through synchronized continuous extrusion:

```python
def move_with_extrusion()
```

where movement and material deposition occur simultaneously.

This was identified as the central conceptual difference between the current implementation and a future FDM-compatible backend.

---

# Core FDM Extrusion Concept

A key relationship studied during this stage was:

E \propto d

meaning that the extrusion amount (`E`) is proportional to the traveled distance (`d`).

This differs fundamentally from the syringe system, where extrusion occurs as isolated deposition events independent from movement length.

---

# Continuous Extrusion Refactor

A first experimental refactor of the deposition logic was developed.

The original architecture:

```python
extrusion()
afterdrop()
```

was conceptually replaced by:

```python
move_with_extrusion()
```

using synchronized XY movement and extrusion:

```gcode
G1 X... Y... E... F...
```

This represented the first prototype of continuous volumetric deposition inside the existing line-generation logic.

---

# Relative Extrusion Mode

The experimental implementation adopted relative extrusion mode using:

```gcode
M83
```

instead of absolute extrusion (`M82`).

Relative extrusion was chosen because:

* it simplifies experimental calculations,
* avoids accumulation of large E values,
* makes debugging easier,
* better fits isolated line generation.

---

# Extrusion Math Implementation

The prototype implemented the complete basic volumetric extrusion pipeline.

---

## 1. Line Length Calculation

The distance between two points was computed using:

```python
def line_length(x0, y0, x1, y1):
    return math.sqrt(pow((x1 - x0), 2) + pow((y1 - y0), 2))
```
This distance represents the physical toolpath length traveled during extrusion.

---

## 2. Deposited Volume Estimation

The deposited volume was approximated as:

V = d \cdot W \cdot H

where:

* (d) = line length,
* (W) = extrusion width,
* (H) = layer height.

The experimental implementation used:

* extrusion width = 0.45 mm
* layer height = 0.2 mm

---

## 3. Filament Cross-Sectional Area

Considering standard 1.75 mm filament:

A_f = \pi r^2

with:

```text
r = 0.875 mm
```

---

## 4. Filament Length Required for Extrusion

The final extrusion amount was computed using:

E = \frac{V}{A_f}

This converts deposited material volume into the required raw filament length.

---

# Architectural Reuse

A major observation from the experiments was that a large portion of the syringe backend architecture can be reused for FDM deposition.

The following concepts remain compatible:

* safe movement boundaries,
* serpentine motion generation,
* horizontal/vertical line generation,
* cleaning routines,
* safe positioning,
* motion synchronization,
* travel logic.

The main architectural difference lies specifically in the deposition primitive:

* discrete droplet deposition,
  vs
* continuous synchronized extrusion.

---

# Serpentine Path Preservation

The alternating serpentine logic was preserved:

```python
if (i % 2) == 0:
    xs, xe = x0, x1
else:
    xs, xe = x1, x0
```

This minimizes unnecessary travel movement and maintains continuous path efficiency.

---

# Retraction and Recovery

Firmware retraction was integrated using:

* `G10` for retract,
* `G11` for recovery.

The experiments also introduced the concept of pressure rebuilding before fiber generation.

A small priming movement was added:

```gcode
G1 E0.1 F300
```

to help stabilize nozzle pressure before beginning the next fiber.

This introduced the concept that retraction systems are fundamentally pressure-management systems rather than simple filament-position systems.

---

# Pressure Stabilization Concepts

An important observation from the experiments was that after retraction:

* nozzle pressure decreases,
* extrusion does not restart instantly,
* line starts may become inconsistent.

This behavior was identified as conceptually similar to the stabilization pauses used in the syringe system after droplet deposition.

The FDM equivalent involves:

* recovery,
* priming,
* pressure rebuilding.

---

# Experimental Scope

The prototype intentionally remained:

* single-layer,
* line-oriented,
* constrained to parallel fibers,
* experimental and isolated from the main backend.

The goal was not to create a complete slicer, but rather to understand:

* synchronized extrusion,
* geometry-driven material flow,
* continuous deposition behavior.

---

# Main Technical Corrections Identified During Analysis

Several issues were identified and corrected during the experimental review process:

* incorrect coordinate ordering during extrusion calculation,
* incorrect XY argument ordering in vertical extrusion moves,
* unnecessary repeated `M109` calls inside loops,
* inappropriate use of `G1` for travel motions,
* unsafe use of cold extrusion (`M302 S0`),
* missing pressure rebuild considerations after retract.

---

# Final Observation

By the end of Day 3, the system successfully transitioned from:

```text
discrete deposition events
```

to:

```text
continuous geometry-driven extrusion
```

This represented the first functional prototype of an FDM-oriented deposition backend built on top of the original syringe deposition architecture.
