from PIL import Image

img = Image.open(r"f:\pawn's-journey\Assets\Sprites\Characters\New_max_spritesheet.png")
print(f"Image size: {img.size[0]}x{img.size[1]}")
print(f"Mode: {img.mode}")

# Calculate likely grid size
width, height = img.size

# Try common grid configurations
for grid in [(4, 4), (4, 3), (3, 4), (5, 4), (4, 5)]:
    cols, rows = grid
    cell_w = width / cols
    cell_h = height / rows
    print(f"{cols}x{rows} grid = {cell_w:.1f}x{cell_h:.1f} per cell")
