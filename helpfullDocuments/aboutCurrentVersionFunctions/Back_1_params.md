I was confused with

```python
fiber_orientation: str = "Horizontal"  # Horizontal | Vertical
fiber_length: float = 80.0            # L (mm)
fiber_width: float = 40.0             # W (mm)
fiber_spacing: float = 1.0            # S (mm) distância entre fibras
```

because why is there width and length? aren`t they the same thing?

Length (L) - how long each fiber is (X direction)
Width (W) - how tall the rectangle is (Y direction)
Spacing (S) - distance between each line

You draw MANY horizontal lines
Each line has length L
You stack them vertically across W

If the direction turns to be "Vertical", you just need to change X/Y, but the idea will be the same.