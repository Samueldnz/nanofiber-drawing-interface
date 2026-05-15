# Day 5 Notes — Volumetric Flow, Pressure Behavior and Extrusion Dynamics

## Pressure and Corner Behavior

The extruder pushes filament at a constant rate along the line. As the printer approaches the end of the line, the motion system slows the print head, but the extrusion rate may not immediately follow the same deceleration.

This creates a temporary mismatch:

```text
slow motion + same extrusion flow
```

As a result, the nozzle deposits more material than necessary for that slower movement speed.

The excess material accumulates near the corner or line ending, creating:

* blobs,
* bulges,
* thicker corners.

Once the printer accelerates into the next movement, the extrusion flow and motion speed become synchronized again and the line returns to normal width.

Simplified behavior:

```text
accelerate → constant speed → decelerate
```

while extrusion pressure may lag behind motion changes.

---

### Observation About This Project

This may not become a major issue in the current project because:

* the system generates only a single layer,
* paths are mostly parallel lines,
* retraction and cleaning happen between fibers,
* there are fewer continuous sharp corners compared to traditional FDM printing.

However, pressure behavior and extrusion lag may still become relevant at:

* line starts,
* line endings,
* perpendicular crossings,
* short fibers.

---

## Volumetric Flow Rate

The most important theoretical concept identified was:

Q = v \cdot A

Where:

| Variable | Meaning                        |
| -------- | ------------------------------ |
| (Q)      | volumetric flow rate           |
| (v)      | movement speed                 |
| (A)      | deposited cross-sectional area |

---

### Example Calculation

Given:

* movement speed = 50 mm/s
* line width = 0.45 mm
* layer height = 0.2 mm

Cross-sectional area:

```text
A = 0.45 × 0.2
A = 0.09 mm²
```

Volumetric flow:

```text
Q = 50 × 0.09
Q = 4.5 mm³/s
```

Meaning:

```text
during motion, the nozzle must continuously supply
4.5 mm³ of material every second
```

---

### Main Interpretation

Faster motion requires more material flow because the nozzle is covering more distance every second.

Therefore:

* higher speed → higher required flow,
* lower speed → lower required flow.

---

## Relationship Between Speed and Material

### Low Speed + High Flow

Too much material for the movement speed may cause:

* blobs,
* excess width,
* nozzle dragging,
* poor crossings.

---

### High Speed + Low Flow

Too little material for the movement speed may cause:

* gaps,
* weak lines,
* inconsistent fibers,
* underextrusion.

---

## Extruder Physical Limits

Another important observation is that:

* the hotend has a maximum melting capability,
* the extruder cannot infinitely increase flow.

If the required volumetric flow becomes higher than the hotend can melt and supply, problems may occur such as:

* underextrusion,
* unstable flow,
* inconsistent deposition.

Possible solutions:

* reduce movement speed,
* reduce extrusion width,
* reduce layer height.

These adjustments are typically determined experimentally.

---

### Flow Adjustment With M221

General extrusion flow can be experimentally adjusted using:

```gcode
M221
```

Examples:

```gcode
M221 S105
```

adds:

```text
5% more material globally
```

Useful for correcting:

* weak lines,
* gaps,
* underextrusion.

---

If there are:

* blobs,
* nozzle dragging,
* excessive width,
* excess material,

flow can be reduced:

```gcode
M221 S95
```

which reduces extrusion globally by 5%.

---

### Temperature and Material Flow

Temperature directly affects filament viscosity.

---

#### Higher Temperature

Results:

* lower viscosity,
* easier flow,
* smoother extrusion.

However:

* excessive temperature may increase ooze and stringing.

---

#### Lower Temperature

Results:

* harder flow,
* cleaner extrusion,
* more controlled material behavior.

However:

* temperature that is too low may cause underextrusion and inconsistent flow.

---

### Extrusion Width vs Nozzle Diameter

An important difference from the syringe system is that the melted filament becomes flattened against the bed.

Because of this:

* a 0.4 mm nozzle may produce lines with:

  * 0.45 mm width,
  * 0.48 mm width,
  * or even larger widths depending on squish and flow.

Therefore:

```text
extrusion width is not necessarily equal to nozzle diameter
```

This must be considered during extrusion calculations.
