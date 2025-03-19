import os
import argparse
from io_images import store_raw_images

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
    parser = argparse.ArgumentParser(description="Process CZI files and store raw images.")
    
    # Add arguments with default values, long and short argument names
    parser.add_argument(
        "-ifp", "--input_folderpath", 
        help="Path to the folder containing the .czi files", 
        default=r"\\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\Alessandro_20250318", 
        nargs='?'
    )
    parser.add_argument(
        "-ofp", "--output_folderpath", 
        help="Path to the folder where the .czi files will be stored", 
        default=r"\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS", 
        nargs='?'
    )
    parser.add_argument(
        "-rn", "--register_name", 
        help="Name of the Excel register file containing metadata", 
        default='slide_register_JoNa.xlsx', 
        nargs='?'
    )
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Path to the register folder (you can adjust this if needed)
    register_folder_path = args.output_folderpath

    # Format the paths based on the operating system
    input_folderpath = format_path(args.input_folderpath)
    output_folderpath = format_path(args.output_folderpath)
    register_path = os.path.join(register_folder_path, args.register_name)
    register_path = format_path(register_path)  # Format register_path if necessary

    # Call the store_raw_images function with the command-line arguments
    infoframe = store_raw_images(input_folderpath=input_folderpath,
                                 output_folderpath=output_folderpath,
                                 register_path=register_path,
                                 age_values=None,
                                 sex_values=None,
                                 animal_values=None,
                                 extension=".czi")
    
    # Print the infoframe result
    print('czi files were renamed and stored')
    print(infoframe.to_string())

if __name__ == "__main__":
    main()
