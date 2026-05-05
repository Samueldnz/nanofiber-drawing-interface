
### **Experimental Log – Nanofiber Deposition Test (05/05/2026)**

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