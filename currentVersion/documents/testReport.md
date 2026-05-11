
# **Experimental Log – Nanofiber Deposition Test (05/05/2026)**

A fabrication test was conducted on **May 5, 2026**, using a horizontal fiber deposition strategy. The experiment aimed to evaluate the motion behavior and deposition consistency of the current implementation under the following parameters:

* **Fiber orientation:** Horizontal
* **Printing speed:** 2000 mm/min
* **Z-offset:** 0.4 mm
* **Z-hop:** 10.0 mm
* **Pause time:** 0 ms
* **Droplet amount:** 1.0 (extrusion units)
* **Afterdrop:** Enabled
* **Cleaning routine:** Enabled
* **Fiber length:** 81.0 mm
* **Fiber width:** 89.0 mm
* **Fiber spacing:** 1.0 mm

During execution, it was observed that the system was **not properly calibrated with respect to the printer bed**, resulting in incorrect absolute positioning of the deposited structure.

In addition to the calibration issue, an **unexpected motion pattern** was identified during the deposition process. The intended behavior for horizontal fiber fabrication is a **zig-zag trajectory**, in which the print head deposits a droplet, moves horizontally to the opposite side to form a fiber, performs a droplet and cleaning routine, and then returns along the same horizontal path to initiate the next fiber. This process should continue with strictly horizontal movements, combined with vertical indexing between lines.

However, the observed behavior deviated from this expected pattern. After completing a fiber and executing the cleaning routine, the system performed a **diagonal movement in the XYZ plane without material deposition**, followed by a return to a previous position before continuing the fiber deposition. This resulted in a sequence of movements characterized by:

1. Droplet deposition at the starting point
2. Go up
3. Horizontal motion with deposition
4. Afterdrop deposition and cleaning
5. Go up
4. Diagonal displacement without fiber formation
5. Return to a prior position
6. Resumption of deposition along the intended fiber path

This diagonal transition between fibers is inconsistent with the expected axis-aligned motion and was **not present in the legacy implementation**, where transitions between fibers were performed using sequential horizontal and vertical movements (i.e., orthogonal motion only).

In summary, the experiment revealed two primary issues:
(i) **misalignment between the software coordinate system and the physical printer bed**, and
(ii) **the presence of unintended diagonal transitions between fibers**, leading to deviations from the expected deposition pattern.

---

# **Experimental Log – Potential issue on `_run_custom_centered` Test (07/05/2026)**

A potential issue exists in the extrusion control logic regarding the use of coordinate modes. The initialization sequence configures the printer with `M82`, which enables absolute extrusion mode, while the droplet deposition functions later switch to `G91` and perform relative extrusion movements using commands such as `G1 E-...`. Depending on the firmware implementation, `G91` may affect only the XYZ axes and not the extruder axis (E).

This behavior should be experimentally verified on the target firmware. If extrusion is expected to behave relatively, the use of `M83` (relative extrusion mode) may be more appropriate and predictable than relying on `G91` alone.

To validate the current implementation, a controlled extrusion test was recommended. The test should execute sequential extrusion commands after enabling `G91` and observe whether the extrusion axis behaves relatively (`-1 mm` followed by another `-1 mm`) or absolutely (second command produces no additional movement). A comparison using `M83` (relative extrusion mode) is also recommended to determine whether it provides more predictable behavior for the extrusion system.

## Proposed Test

```
M82        ; absolute extrusion mode
G92 E0     ; reset extruder position

G91        ; relative positioning
G1 E-1 F100

G1 E-1 F100
```

### Expected Behaviors

* **Case 1 — Extrusion behaves RELATIVELY**

The syringe/extruder should move: `-1 mm` then another `-1 mm`

This means:

 - `G91` is affecting the E axis
 - current implementation is valid

* **Case 2 — Extrusion behaves ABSOLUTELY**

The first command moves to `E = -1`. The second command  attempts: `E = -1 again`

So it should:
 - second movement does not occur
 - or movement is inconsistent

This means:

 - `M82` still controls E independently
 - `G91` only affected XYZ axes

## Results

The proposed test was executed using both `M82` (absolute extrusion mode) and `M83` (relative extrusion mode) while maintaining the same relative positioning commands (`G91`) during extrusion. No observable difference in extrusion behavior was identified between the two configurations.

In both cases, sequential extrusion commands produced cumulative extrusion movement, indicating that the firmware correctly interpreted the extrusion axis relatively during execution. Therefore, under the tested firmware configuration, `G91` appears to affect the extrusion axis as expected, and the current implementation using `M82` together with temporary `G91` commands behaves correctly.

Although the issue was not reproduced on the tested system, the investigation remains relevant because extrusion behavior may vary depending on firmware implementation or configuration. Future validation may still be necessary when using different printer firmware versions or hardware platforms.


# **Experimental Log – Footer Execution Inside Drawing Loop (07/05/2026)**

A potential logic issue was identified in the placement of the footer section inside the main drawing loop. The commands:

```python id="fxyh8m"
send("M300 S440 P200")
send("G0 X10 Y190 Z30 F3000")
```

were being executed after every fiber iteration instead of only once at the end of the complete drawing process. As a consequence, the printer repeatedly moved to the parking position between fibers, interrupting the continuous serpentine deposition pattern and introducing unnecessary travel movements.

To investigate this behavior, the footer section was temporarily moved outside the `while True` drawing loop. A controlled drawing test was then conducted using a small multi-fiber pattern while monitoring the printer trajectory between consecutive fibers. The objective of the test was to verify whether relocating the footer outside the loop eliminated the undesired parking movement between fibers.

## Proposed Test

The test was performed using a small horizontal multi-fiber pattern (e.g., 3–5 fibers) with standard deposition parameters and the modified implementation containing the footer outside the loop. During execution, the printer motion was visually monitored to verify whether the system returned to the parking position (`X10 Y190 Z30`) between fibers.

### Expected Behaviors

* **Case 1 — Footer relocation fixes the behavior**

The printer should:

 - continuously execute the serpentine deposition pattern
 - move directly from one fiber to the next
 - execute the footer commands only once after all fibers are completed

This means:

 - the footer logic was the source of the issue
 - the original footer placement inside the loop was incorrect

* **Case 2 — Behavior persists after modification**

The printer should:

 - continue returning to the parking position after every fiber iteration
 - interrupt the serpentine movement pattern
 - perform unnecessary travel motion between fibers

This means:

 - the footer logic is not the source of the issue
 - another section of the drawing routine is responsible for the behavior

Here is the completed **Results** section for your footer execution experiment:

## Results

The experimental test confirmed the behavior described in **Case 1**. After relocating the footer section outside the `while True` drawing loop, the printer executed the deposition routine continuously without returning to the parking position between fibers.

During execution, the system maintained the expected serpentine movement pattern, transitioning directly from one fiber to the next while preserving uninterrupted deposition flow. The footer commands:

```python
send("M300 S440 P200")
send("G0 X10 Y190 Z30 F3000")
```

were executed only once after completion of the entire drawing routine, confirming that the original footer placement inside the loop was responsible for the undesired intermediate parking movements.

The modification successfully eliminated unnecessary travel operations between fibers and restored the intended continuous deposition behavior.




# **Experimental Log – Syringe Empty Validation During Drawing (11/05/2026)**

A safety issue was identified during the drawing process related to syringe depletion handling inside the deposition routines. During long fiber deposition sequences, the software continued executing extrusion commands even after the syringe became physically empty and the software counter reached zero. As a consequence, the system continued sending extrusion commands while the `syringe_current_amount` value became negative.

The original implementation inside both `extrusion()` and `afterdrop()` executed material deposition unconditionally:

```python
send("G91")
send(f"G1 E-{float(pp.droplet_amount)} F200")
send("G90")
```

while the syringe bookkeeping logic continuously subtracted material from the software counter:

```python
self.state.set_param(
    "syringe_current_amount",
    self.state.params.syringe_current_amount
    - float(pp.droplet_amount),
)
```

without validating whether sufficient material remained available in the syringe.

Additionally, the physical syringe sensor verification logic already existed through the `M119` command inside the `check_syringe()` routine:

```python
def check_syringe(self) -> Optional[str]:
    self.ser.write(("M119\r\n").encode("utf-8"))
```

however, the sensor validation was not integrated into the active deposition routines during drawing execution.

To investigate the issue, syringe depletion validation was added to both `extrusion()` and `afterdrop()`, combining:

* software-based syringe amount verification;
* hardware-based syringe sensor verification using `M119`;
* controlled interruption of the drawing loop through `SyringeEmptyError`;
* preservation of safe footer execution after depletion events.

## Proposed Test

The test was performed using a continuous multi-fiber deposition pattern with repeated extrusion cycles until the syringe approached depletion. During execution, the following behaviors were monitored:

* evolution of `syringe_current_amount`;
* response of the `M119` syringe sensor;
* interruption behavior after depletion detection;
* execution of the footer parking routine after stopping.

The objective of the experiment was to verify whether the new depletion protection prevented invalid extrusion operations while still allowing the machine to terminate the drawing safely.

### Expected Behaviors

* **Case 1 — Syringe depletion protection works correctly**

The system should:

* continuously execute deposition while material remains available;
* stop extrusion immediately after depletion is detected;
* prevent `syringe_current_amount` from becoming negative;
* interrupt the drawing loop safely using `SyringeEmptyError`;
* still execute the footer parking routine after interruption.

This means:

* the syringe validation logic is functioning correctly;
* the drawing process terminates safely after depletion;
* software and hardware depletion protection are operating properly.

- **Case 2 — Protection fails during deposition**

The system should:

* continue executing extrusion after depletion;
* allow `syringe_current_amount` to become negative;
* fail to interrupt the drawing process;
* skip or improperly execute footer logic after interruption.

This means:

* the depletion validation is incomplete or incorrectly integrated;
* the drawing interruption architecture requires revision.

## Results

The experimental tests confirmed the behavior described in **Case 1**. After integrating syringe validation into both `extrusion()` and `afterdrop()`, the system successfully interrupted the drawing process when depletion conditions were detected.

The software-based validation prevented extrusion attempts when the remaining syringe amount became smaller than the configured droplet deposition amount, while the hardware-based validation continuously monitored the physical syringe sensor through `M119`.

The tests also confirmed that the newly introduced `SyringeEmptyError` architecture correctly interrupted the drawing loop without activating the global `_stop_event`, allowing the footer section:

```python
send("M300 S440 P200")
send("G0 X10 Y190 Z30 F3000")
```

to execute safely after depletion events.

During the experiments, an additional observation was identified: the physical syringe sensor occasionally triggered before the software counter reached zero, indicating that the sensor behavior corresponds to a low-material threshold rather than an exact empty-volume condition. As a result, the software counter was preserved independently from the hardware sensor state to avoid artificially forcing the remaining amount to zero during premature sensor activation.

The modification successfully eliminated negative syringe amount values, prevented invalid extrusion operations after depletion, and restored safe controlled termination behavior during long deposition routines.


