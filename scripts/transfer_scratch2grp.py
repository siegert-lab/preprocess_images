import os
import shutil
import time
import subprocess

# Source and destination directories
source_dir = "/run/user/1001/gvfs/smb-share:server=scratch4.ista.ac.at,share=scratch/siegegrp/_ImageDrop/NIKON-W1-03/Thomas/nd_seq/"
destination_dir = "/mnt/gdrive/ThNe/_Bioimaging/development_retina/"

# List of files to transfer (Modify this list with the exact filenames)
files_to_transfer = [    
    "slide_P07_M_001.nd2",
    "slide_P07_M_002.nd2",
    "slide_P07_M_003.nd2",
    "slide_P07_M_004.nd2",

    "slide_P21_M_001.nd2",
    "slide_P21_M_002.nd2",
    "slide_P21_M_003.nd2",
    "slide_P21_M_004.nd2",

]

def transfer_file(src, dst):
    """Attempts to transfer a file and retries if it fails."""
    max_retries = 5  # Maximum number of retries
    retry_delay = 10  # Seconds to wait before retrying

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Transferring: {src} -> {dst} (Attempt {attempt})")
            
            # Use rsync for efficient transfer
            subprocess.run(["rsync", "-av", "--progress", "--partial", "--append-verify", src, dst], check=True)
            
            # Verify if file exists at destination
            if os.path.exists(dst):
                print(f"✅ Successfully transferred {src}")
                return True
            else:
                print(f"⚠️ Transfer failed, file not found at destination")

        except subprocess.CalledProcessError as e:
            print(f"⚠️ Transfer failed: {e}")
        
        if attempt < max_retries:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    print(f"❌ Failed to transfer {src} after {max_retries} attempts")
    return False


def main():
    """Main function to transfer selected files one by one."""
    for file in files_to_transfer:
        source_file = os.path.join(source_dir, file)
        destination_file = os.path.join(destination_dir, file)

        if os.path.exists(source_file):
            transfer_file(source_file, destination_file)
        else:
            print(f"⚠️ File not found: {source_file}")


if __name__ == "__main__":
    main()
