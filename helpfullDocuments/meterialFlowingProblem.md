# Is there a way to solve the problem of material continuing to flow after pressure is applied, or is this a physics limitation?

The continued flow after stopping is a real physical effect (stored pressure + fluid behavior). You can’t remove it entirely, but with retraction, timing, and mechanical tuning, you can reduce it to the point where it’s practically negligible.

## Practical ways to reduce it

1. Retraction (most common)

```
G91
G1 E-0.2
G90
```
It pulls back pressure to reduce dripping.

2. “Afterdrop compensation”

Instead of stopping exactly at the target, the movement starts stopping earlier and let residual flow finish the job.

- You intentionally under-extrude, letting physics complete it

3. Slower extrusion near the end

Fast → slow → stop: Reduces pressure buildup before stopping

4. Mechanical improvements

- Shorter tubing
- Stiffer syringe (metal > plastic)
- Smaller nozzle
- Direct drive (no slack)

5. Material tuning

- Higher viscosity → less dripping
- Shear-thinning materials → better control

6. Pressure-based control (advanced)

Instead of position (E-axis), control pressure directly:

- pneumatic systems
- pressure regulators

It is much more precise, but more complex.

7. Dwell (pause)

```
G4 P200  ; wait 200 ms
```
Lets pressure stabilize before moving