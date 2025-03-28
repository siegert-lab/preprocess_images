"""
Script to convert all ND2 files in a folder to BDV/XML+N5 format.
This script also extracts metadata from ND2 filenames following the pattern slide_Pxx_S_i00j.nd2.
asas means Age Sex Animal Side
"""
import os
import argparse
from process_nd2 import convert_nd2_to_bdv_asas

# Default paths
DEFAULT_INPUT_PATH = "/mnt/gdrive/ThNe/_Bioimaging/development_retina"
DEFAULT_OUTPUT_PATH = "/mnt/gdrive/ThNe/development_retina/raw_images_n5"

def main():
    parser = argparse.ArgumentParser(description="Convert ND2 files to BDV/XML+N5 format")
    parser.add_argument("--input_folderpath", "-ifp", type=str, 
                        default=DEFAULT_INPUT_PATH,
                        help=f"Path to the folder containing ND2 files (default: {DEFAULT_INPUT_PATH})")
    parser.add_argument("--output_folderpath", "-ofp", type=str, 
                        default=DEFAULT_OUTPUT_PATH,
                        help=f"Path to the folder where N5 files will be saved (default: {DEFAULT_OUTPUT_PATH})")
    parser.add_argument("--is_parallel", "-par", action="store_true", 
                        help="Run conversion in parallel mode (default: False)")
    
    args = parser.parse_args()
    
    print(f"\nInput folder: {args.input_folderpath}\n")
    print(f"\nOutput folder: {args.output_folderpath}\n")
    print(f"\nParallel processing: {args.is_parallel}\n")
    
    # Ensure output directory exists
    os.makedirs(args.output_folderpath, exist_ok=True)
    
    # Convert files and get the final state of the output folder
    output_files = convert_nd2_to_bdv_asas(args.input_folderpath, args.output_folderpath, is_parallel=args.is_parallel)
    
    print("\nProcess completed!\n")
    # Print the infoframe result
    print(output_files.to_string())

    # Save results to CSV
    results_path = os.path.join(args.output_folderpath, 'n5_files_inventory.csv')
    output_files.to_csv(results_path, index=False)
    print(f"\nOutput files inventory saved to {results_path}")

if __name__ == "__main__":
    main()
