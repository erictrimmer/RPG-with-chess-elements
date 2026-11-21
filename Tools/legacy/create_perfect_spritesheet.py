from PIL import Image
import numpy as np

# Load the original sprite sheet
img = Image.open(r"f:\pawn's-journey\Assets\Sprites\Characters\max_spritesheet.png")
img_array = np.array(img)

print(f"Original image size: {img.size}")

# Region settings
region_x = 3
region_y = 0
region_width = 122
region_height = 132

# Current cell size
cell_width = region_width // 4  # 30
cell_height = region_height // 4  # 33

print(f"Current cell size: {cell_width}x{cell_height}")

# Create a new sprite sheet with perfectly aligned cells
# Make it a clean 4x4 grid with no extra padding
new_cell_width = 32  # Nice round number for pixel art
new_cell_height = 32

new_width = new_cell_width * 4
new_height = new_cell_height * 4

print(f"New sprite sheet will be: {new_width}x{new_height}")
print(f"New cell size: {new_cell_width}x{new_cell_height}")

# Create new image with transparency
new_img_array = np.zeros((new_height, new_width, 4), dtype=np.uint8)

# Function to find bounding box of non-transparent pixels
def get_sprite_bounds(frame):
    """Find the bounding box of the actual sprite pixels"""
    if frame.shape[2] == 4:
        alpha = frame[:, :, 3]
        mask = alpha > 10
    else:
        mask = np.any(frame > 10, axis=2)
    
    if not mask.any():
        return None
    
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    
    return (x_min, y_min, x_max + 1, y_max + 1)

# Function to find glasses center
def find_glasses_center_x(frame):
    """Find the X center of the glasses"""
    head_region = frame[:int(frame.shape[0] * 0.4), :]
    
    if frame.shape[2] == 4:
        dark_mask = (head_region[:, :, 0] < 100) & (head_region[:, :, 3] > 200)
    else:
        dark_mask = head_region[:, :, 0] < 100
    
    if not dark_mask.any():
        return None
    
    y_coords, x_coords = np.where(dark_mask)
    if len(x_coords) == 0:
        return None
    
    return int(np.mean(x_coords))

print("\nProcessing frames...")

# First pass: find the average glasses X position across all frames
glasses_positions = []
for row in range(4):
    for col in range(4):
        y_start = region_y + row * cell_height
        x_start = region_x + col * cell_width
        frame = img_array[y_start:y_start+cell_height, x_start:x_start+cell_width]
        
        glasses_x = find_glasses_center_x(frame)
        if glasses_x is not None:
            glasses_positions.append(glasses_x)

target_glasses_x = int(np.mean(glasses_positions)) if glasses_positions else new_cell_width // 2
print(f"Target glasses X position: {target_glasses_x}")

# Second pass: center each frame based on glasses position
for row in range(4):
    for col in range(4):
        # Extract original frame
        y_start = region_y + row * cell_height
        x_start = region_x + col * cell_width
        frame = img_array[y_start:y_start+cell_height, x_start:x_start+cell_width]
        
        # Find glasses position in this frame
        glasses_x = find_glasses_center_x(frame)
        
        if glasses_x is None:
            # Fallback to sprite bounds
            bounds = get_sprite_bounds(frame)
            if bounds:
                x_min, y_min, x_max, y_max = bounds
                glasses_x = (x_min + x_max) // 2
            else:
                glasses_x = cell_width // 2
        
        # Calculate where to place the sprite in the new cell
        # We want the glasses to be at the center of the new cell
        offset_x = (new_cell_width // 2) - glasses_x
        
        # Also center vertically based on sprite bounds
        bounds = get_sprite_bounds(frame)
        if bounds:
            x_min, y_min, x_max, y_max = bounds
            sprite_height = y_max - y_min
            offset_y = (new_cell_height - sprite_height) // 2 - y_min
        else:
            offset_y = 0
        
        # Place sprite in new cell
        new_y = row * new_cell_height
        new_x = col * new_cell_width
        
        # Copy pixels with offset
        for y in range(cell_height):
            for x in range(cell_width):
                new_py = new_y + y + offset_y
                new_px = new_x + x + offset_x
                
                if 0 <= new_py < new_height and 0 <= new_px < new_width:
                    new_img_array[new_py, new_px] = frame[y, x]
        
        print(f"Frame ({row},{col}): Offset ({offset_x}, {offset_y})")

# Save the new sprite sheet
new_img = Image.fromarray(new_img_array)
output_path = r"f:\pawn's-journey\Assets\Sprites\Characters\max_spritesheet_fixed.png"
new_img.save(output_path)

print(f"\nFixed sprite sheet saved to: {output_path}")
print(f"  Size: {new_width}x{new_height}")
print(f"  Cell size: {new_cell_width}x{new_cell_height}")
print(f"  All sprites are now perfectly centered!")
