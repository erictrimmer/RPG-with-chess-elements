from PIL import Image
import numpy as np

# Load the sprite sheet
img = Image.open(r"f:\pawn's-journey\Assets\Sprites\Characters\max_spritesheet.png")
img_array = np.array(img)

print(f"Image size: {img.size}")
print(f"Mode: {img.mode}")

# Based on the region_rect from the .tscn file: Rect2(3, -1, 122, 132)
# This means the actual sprite area starts at x=3, y=-1 (adjusted to 0), width=122, height=132
region_x = 3
region_y = max(0, -1)  # Can't have negative, so 0
region_width = 122
region_height = 132

# Calculate cell size (4x4 grid)
cell_width = region_width // 4
cell_height = region_height // 4

print(f"Cell size: {cell_width}x{cell_height}")

# Function to find the glasses/eyes position in a frame
def find_glasses_center(frame_array):
    """Find the center of the darkest pixels (glasses) in the upper portion of the frame"""
    # Look only in the top 40% of the frame (where the head/glasses are)
    head_region = frame_array[:int(frame_array.shape[0] * 0.4), :]
    
    # Find dark pixels (glasses are typically dark/black)
    if frame_array.shape[2] == 4:  # RGBA
        # Look for dark, opaque pixels
        dark_mask = (head_region[:, :, 0] < 100) & (head_region[:, :, 3] > 200)
    else:  # RGB
        dark_mask = head_region[:, :, 0] < 100
    
    if not dark_mask.any():
        # Fallback: find any non-transparent pixels
        if frame_array.shape[2] == 4:
            dark_mask = head_region[:, :, 3] > 200
        else:
            return None
    
    # Find center of dark pixels
    y_coords, x_coords = np.where(dark_mask)
    if len(x_coords) == 0:
        return None
    
    center_x = int(np.mean(x_coords))
    center_y = int(np.mean(y_coords))
    
    return (center_x, center_y)

# Analyze each frame
print("\nAnalyzing frames...")
for row in range(4):
    for col in range(4):
        # Extract frame
        y_start = region_y + row * cell_height
        x_start = region_x + col * cell_width
        
        frame = img_array[y_start:y_start+cell_height, x_start:x_start+cell_width]
        
        glasses_pos = find_glasses_center(frame)
        if glasses_pos:
            print(f"Frame ({row},{col}): Glasses at x={glasses_pos[0]}, y={glasses_pos[1]}")
        else:
            print(f"Frame ({row},{col}): Could not detect glasses")

print("\nAnalysis complete!")
