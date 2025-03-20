"""
Script to convert all ND2 files in a folder to BDV/XML+N5 format.
"""
import argparse
from process_nd2 import convert_nd2_to_bdv

def main():
    parser = argparse.ArgumentParser(description="Convert ND2 files to BDV/XML+N5 format")
    parser.add_argument("--input_folderpath", "-ifp", type=str, required=True,
                        help="Path to the folder containing ND2 files")
    parser.add_argument("--output_folderpath", "-ofp", type=str, required=True,
                        help="Path to the folder where N5 files will be saved")
    
    args = parser.parse_args()
    
    print(f"Input folder: {args.input_folderpath}")
    print(f"Output folder: {args.output_folderpath}")
    
    # Call the convert function
    convert_nd2_to_bdv(args.input_folderpath, args.output_folderpath)
    
    print("Conversion process completed!")

if __name__ == "__main__":
    main() 