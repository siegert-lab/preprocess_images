import os
import argparse
from process_czi import chunk_and_save_czi_files

# Check if we are on Windows
windows = "nt" in os.name

def format_path(path):
    """Adjust the path format depending on the operating system."""
    if not windows:
        # Replace backslashes with forward slashes on non-Windows systems
        path = path.replace("\\", "/")
    return path

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Chunk CZI files and store as TIF.")
    
    # Add arguments with default values, long and short argument names
    parser.add_argument(
        "-ifp", "--input_folderpath", 
        help="Path to the folder project, should contain a folder raw_images with tree structure organisation Age/Sex/Animal", 
        default="archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS", 
        nargs='?'
    )
    parser.add_argument(
        "-rn", "--register_name", 
        help="Name of the Excel register file containing metadata", 
        default='slide_register_JoNa.xlsx', 
        nargs='?'
    )
    parser.add_argument(
        "-cs", "--chunk_size", 
        help="size of the chunk (TIF file) in GB", 
        default=10, 
        nargs='?'
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Path to the register folder (you can adjust this if needed)
    register_folder_path = args.input_folderpath

    # Format the paths based on the operating system
    input_folderpath = format_path(args.input_folderpath)
    register_path = os.path.join(register_folder_path, args.register_name)
    register_path = format_path(register_path)  # Format register_path if necessary

    # Call the function to chunk and save the CZI files
    chunk_and_save_czi_files(input_folderpath,
                             register_path,
                             chunk_size=args.chunk_size,
                             conditions=['Age', 'Sex', 'Animal'])

    # Print the infoframe result
    print('CZI files were chunked and stored')

if __name__ == "__main__":
    main()
