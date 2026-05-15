# Studies — Path Optimization and Perpendicular Fiber Deposition

Optimization of machine movements is extremely important to reduce:

* execution time,
* unnecessary movements,
* energy consumption,
* mechanical wear,
* and process instability.

There are several strategies used in manufacturing and toolpath planning to accomplish this goal.

The objective of today’s studies is to understand how horizontal, vertical, and perpendicular (crossed) fiber paths are generated and handled inside the current nanofiber drawing system.

---

# Serpentine Path Strategy

The current implementation already uses a serpentine path strategy to reduce unnecessary travel movements and improve motion efficiency.

This logic can be found in:

`nanofiber-drawing-interface/currentVersion/backend.py`

approximately at:

* lines 754–757
* lines 805–808

for horizontal and vertical paths respectively.  

The code alternates the movement direction between fibers:

```python
if (i % 2) == 0:
    xs, xe = x0, x1
else:
    xs, xe = x1, x0
```

This creates the following movement pattern:

```text
->->->->->
<-<-<-<-<-
->->->->->
```

Instead of returning to the same side after every line, the nozzle continues from the nearest endpoint, minimizing travel distance and improving efficiency.

This same concept is applied to both horizontal and vertical deposition.

---

# Goal of the Current Studies

The main objective now is to understand how perpendicular fiber paths can be implemented without damaging or deforming previously deposited fibers.

More specifically:

* horizontal fibers are deposited first,
* then vertical fibers must cross over them,
* while maintaining structural integrity and process efficiency.

---

# Legacy Implementation

In the legacy `GUI.py` implementation, perpendicular paths are handled relatively simply.

The system:

1. performs extrusion,
2. applies a Z-hop,
3. moves to the next position,
4. lowers back to deposition height,
5. performs the afterdrop,
6. and repeats the process.

The implementation essentially performs:

* one full horizontal pass,
* followed by one full vertical pass.

---

# Important Manufacturing Problem

A potential issue appears when generating perpendicular paths.

Consider the following example:

* fiber width = 0.45 mm
* fiber height = 0.20 mm
* spacing between fibers = 0.40 mm

After all horizontal fibers are deposited, the surface is no longer flat.

If the vertical fibers are then deposited at the same Z height (`Z = 0.20 mm`), the nozzle may collide with the previously deposited horizontal fibers.

This could cause:

* deformation,
* dragging,
* smearing,
* or complete damage of the existing fibers.

---

# Initial Proposed Solution

One possible solution would be:

1. draw a short segment,
2. retract,
3. lift the nozzle,
4. cross the existing fiber,
5. lower the nozzle,
6. continue deposition,
7. repeat for every crossing.

Although geometrically correct, this solution is highly inefficient.

Problems include:

* excessive accelerations,
* many Z movements,
* large number of pauses,
* poor throughput,
* increased mechanical wear,
* and significantly longer execution times.

This technique is known as **segmented crossing avoidance**.

It is sometimes used in:

* conductive ink printing,
* hydrogel deposition,
* PCB dispensing,
* and bioprinting,

but usually only when collision avoidance is absolutely necessary.

---

# Current Project Considerations

At the current stage of the project, collision avoidance may not yet be necessary.

The process still requires experimental validation to determine:

* whether collisions actually occur,
* how severe they are,
* and whether the deposited fibers tolerate crossing interactions.

Therefore, practical testing will be essential.

---

# Possible Experimental Solutions

## Solution 1 — Increase Z Height for the Second Orientation

Example:

```text
Horizontal pass → Z = 0.20 mm
Vertical pass   → Z = 0.35 mm
```

Advantages:

* simple implementation,
* minimal code modifications,
* maintains continuous serpentine motion,
* avoids segmented deposition,
* preserves process efficiency.

This is probably the first solution that should be experimentally tested.

This approach is also common in several deposition and additive manufacturing systems.

---

## Solution 2 — Reduce Overlap Pressure

Another possible strategy is reducing the interaction force between crossing fibers by adjusting process parameters such as:

* smaller extrusion amount,
* higher movement speed,
* slightly larger spacing,
* smaller second-pass droplets.

This may reduce mechanical interference during crossing.

---

# Current Conclusion

At the moment, the most promising solution appears to be:

```text
Horizontal pass → Z = 0.20 mm
Vertical pass   → Z = 0.30–0.40 mm
```

while maintaining:

* continuous serpentine motion,
* continuous deposition,
* and no segmented crossing avoidance.

This likely provides the best balance between:

* simplicity,
* execution speed,
* manufacturability,
* and implementation complexity.

---

# Next Steps

To finalize today’s studies, a separate `perpendicular_deposition.py` will be created to prototype and test the perpendicular path implementation described below.

```python
if orient == "Horizontal":
    run_horizontal_pass()

elif orient == "Vertical":
    run_vertical_pass()

elif orient == "Both":
    run_horizontal_pass()
    run_vertical_pass()
```
