def _run_custom_centered(sef, status_signal: Signal) -> None:

    send = self._send_checked()

    #header 
    send("M220 S100") #Sets movement speed multiplier to 100%.
    send("M221 S100") #Sets extrusion flow multiplier to 100%.
    send("M207 S1.0 F1500") # configure retract 
    send("M208 F1500") # configure recovery 

    send("G90") # absolute positioning
    send("M83") # relative extrusion mode
    send("G0 Z2 F1500") 

    send("G92 E0") #Reset extruder position to zero.

    send(f"M109 S{float(self.state.params.temperature)}")

    def move_with_extrusion(x, y, E, speedrate) -> None:
        send(f"G1 X{x:.3f} Y{y:.3f} E{E:.3f} F{speedrate}")

    def line_length(x0, y0, x1, y1):
        return math.sqrt(pow((x1 - x0), 2) + pow((y1 - y0), 2))
    
    def deposited_volume(d):
        # d = distance calculed with line_length
        # w = layer`s width default 0.45
        # h = layer`s height default 0.2
        # V = deposited volume
        V = d * 0.45 * 0.2
        return V
    
    def filament_area():
        # considering diameter = 1.75mm
        r = 1.75 / 2 # 0.875mm
        A_f = math.pi * pow(r, 2)
        return A_f
    
    def filament_length_to_extrude(x0, y0, x1, y1):
        d = line_length(x0, y0, x1, y1)

        V = deposited_volume(d)
        A_f = filament_area()

        E = V / A_f
        return E

    is_retracted = False
    i = 0
    while True:
        # allow live updates to apply to the NEXT fiber safely
        pp = self.state.params

        orient = str(pp.fiber_orientation)
        L = float(pp.fiber_length)
        W = float(pp.fiber_width)
        S = float(pp.fiber_spacing)

        if L <= 0 or W < 0:
            raise RuntimeError("Fiber length must be > 0 and width must be >= 0")
        if S <= 0:
            raise RuntimeError("Fiber spacing must be > 0")
        
        # SAFE HARD rectangle (raises if out of bounds)
        x0, x1, y0, y1 = self._compute_anchored_rect(
            L, W, orient, float(pp.start_x), float(pp.start_y)
        )

        speed = int(pp.speed)
        zoff = float(pp.z_offset)
        zhop = float(pp.z_hop)
        pause_ms = int(pp.pause_ms)
        clean = bool(pp.clean)
        temperature = float(pp.temperature)

        if orient == "Horizontal":
            y = y0 + i * S

            if y > y1 + 1e-6: #if new y is bigger than safe rect
                break

            # Alternate fiber direction to create a continuous serpentine path
            # Even fibers: left → right
            # Odd fibers: right → left
            if (i % 2) == 0:
                xs, xe = x0, x1
            else:
                xs, xe = x1, x0

            E = filament_length_to_extrude(xs, y, xe, y)


            # Move to fiber start position
            send(f"G0 X{xs:.3f} Y{y:.3f} F{speed}")

            # Lower nozzle/syringe to deposition height
            send(f"G0 Z{zoff:.3f} F{speed}")

            if is_retracted:
                send("G11")
                send("G1 E0.1 F300") # slightly pushes filament, rebuilds pressure, prepares the nozzle.

            move_with_extrusion(xe, y, E, speed)

            send("G10")
            is_retracted = True

            if clean:
                x_min, x_max, y_min, y_max, _, _ = self._safe_center()
                # move a bit further outside the end side (clamped to safe)
                if xe >= (x0 + x1) / 2.0:
                    x_a = self._clamp(xe + 5.0, x_min, x_max)
                    x_b = self._clamp(xe + 10.0, x_min, x_max)
                else:
                    x_a = self._clamp(xe - 5.0, x_min, x_max)
                    x_b = self._clamp(xe - 10.0, x_min, x_max)
                send(f"G0 X{x_a:.3f} Z0 F{speed}")
                send(f"G0 X{x_b:.3f} F{speed}")
                send(f"G0 Z3 F{speed}")

            send("M400")
        else:
            x = x0 + i * S
            if x > x1 + 1e-6:
                break

            if (i % 2) == 0:
                ys, ye = y0, y1
            else:
                ys, ye = y1, y0
            
            E = filament_length_to_extrude(x, ys, x, ye)

            send(f"G0 X{x:.3f} Y{ys:.3f} F{speed}")

            send(f"G0 Z{zoff:.3f} F{speed}")

            if is_retracted:
                send("G11")
                send("G1 E0.1 F300") # slightly pushes filament, rebuilds pressure, prepares the nozzle.

            move_with_extrusion(x, ye, E, speed)

            send("G10")
            is_retracted = True

            if clean:
                x_min, x_max, y_min, y_max, _, _ = self._safe_center()
                if ye >= (y0 + y1) / 2.0:
                    y_a = self._clamp(ye + 5.0, y_min, y_max)
                    y_b = self._clamp(ye + 10.0, y_min, y_max)
                else:
                    y_a = self._clamp(ye - 5.0, y_min, y_max)
                    y_b = self._clamp(ye - 10.0, y_min, y_max)
                send(f"G0 Y{y_a:.3f} Z0 F{speed}")
                send(f"G0 Y{y_b:.3f} F{speed}")
                send(f"G0 Z3 F{speed}")
            
            send("M400")

        i += 1

    send("M300 S440 P200")
    send("G0 X10 Y190 Z30 F3000")



















