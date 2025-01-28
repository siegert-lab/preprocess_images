

command = 'CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/glass_slide/tif_filename -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia -mp ./ -spsl ./ -nw 1 -bsp ./'

import subprocess

# Define the command as a list of arguments
command = ["ls", "-l", "/path/to/directory"]

try:
    # Run the command
    result = subprocess.run(command, check=True, text=True, capture_output=True)

    # Print the output
    print("Command Output:\n", result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error: {e.stderr}")
