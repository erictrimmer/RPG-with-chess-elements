from PIL import Image
import os

path = r"f:\pawn's-journey\Assets\Sprites\Characters\New_max_spritesheet.png"
if os.path.exists(path):
    with Image.open(path) as img:
        print(f"Dimensions: {img.width}x{img.height}")
else:
    print("File not found")
