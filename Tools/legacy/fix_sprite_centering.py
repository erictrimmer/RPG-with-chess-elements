from PIL import Image
import numpy as np

# Load the sprite sheet
img = Image.open(r"f:\pawn's-journey\Assets\Sprites\Characters\max_spritesheet.png")
img_array = np.array(img)

# Region settings from analysis
region_x = 3
region_y = 0
region_width = 122
region_height = 132

# Calculate cell size (4x4 grid)
cell_width = region_width // 4
cell_height = region_height // 4

print(f"Cell size: {cell_width}x{cell_height}")

# Target glasses X position (use the middle value: 15)
target_glasses_x = 15

# Function to find the glasses/eyes position in a frame
def find_glasses_center(frame_array):
    """Find the center of the darkest pixels (glasses) in the upper portion of the frame"""
    head_region = frame_array[:int(frame_array.shape[0] * 0.4), :]
    
    if frame_array.shape[2] == 4:  # RGBA
        dark_mask = (head_region[:, :, 0] < 100) & (head_region[:, :, 3] > 200)
    else:
        dark_mask = head_region[:, :, 0] < 100
    
    if not dark_mask.any():
        if frame_array.shape[2] == 4:
            dark_mask = head_region[:, :, 3] > 200
        else:
            return None
    
    y_coords, x_coords = np.where(dark_mask)
    if len(x_coords) == 0:
        return None
    
    center_x = int(np.mean(x_coords))
    return center_x

# Create new image with same size
new_img_array = np.zeros_like(img_array)

print("\nRe-centering frames based on glasses position...")

for row in range(4):
    for col in range(4):
        # Extract original frame
        y_start = region_y + row * cell_height
        x_start = region_x + col * cell_width
        
        frame = img_array[y_start:y_start+cell_height, x_start:x_start+cell_width]
        
        # Find glasses position
        glasses_x = find_glasses_center(frame)
        
        if glasses_x is not None:
            # Calculate offset needed
            offset = target_glasses_x - glasses_x
            
            # Create new frame with shifted content
            new_frame = np.zeros_like(frame)
            
            if offset > 0:
                # Shift right
                new_frame[:, offset:] = frame[:, :cell_width-offset]
            elif offset < 0:
                # Shift left
                new_frame[:, :cell_width+offset] = frame[:, -offset:]
            else:
                # No shift needed
                new_frame = frame
            
            # Place corrected frame in new image
            new_img_array[y_start:y_start+cell_height, x_start:x_start+cell_width] = new_frame
            
            print(f"Frame ({row},{col}): Shifted by {offset} pixels")
        else:
            # Keep original if can't detect glasses
            new_img_array[y_start:y_start+cell_height, x_start:x_start+cell_width] = frame
            print(f"Frame ({row},{col}): Kept original (no glasses detected)")

# Save the corrected sprite sheet
new_img = Image.fromarray(new_img_array)
output_path = r"f:\pawn's-journey\Assets\Sprites\Characters\max_spritesheet_centered.png"
new_img.save(output_path)

print(f"\nCorrected sprite sheet saved to: {output_path}")
print("All frames are now aligned based on glasses position!")
