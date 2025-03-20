#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script converts all ND2 files in a folder to BDV/XML+N5 format.
Usage: python process_nd2.py --input_folderpath /path/to/nd2/files --output_folderpath /path/to/output
"""

import os
import glob
from pathlib import Path
from tqdm import tqdm
from bdv_toolz.cli import nd2_to_bdv

def convert_nd2_to_bdv(input_folderpath, output_folderpath):
    """
    Convert all ND2 files in input_folderpath to BDV/XML+N5 format and save them in output_folderpath.
    
    Parameters
    ----------
    input_folderpath : str
        Path to the folder containing ND2 files
    output_folderpath : str
        Path to the folder where N5 files will be saved
    """
    # Ensure output directory exists
    os.makedirs(output_folderpath, exist_ok=True)
    
    # Find all ND2 files in the input folder
    nd2_files = glob.glob(os.path.join(input_folderpath, "*.nd2"))
    
    if not nd2_files:
        print(f"No ND2 files found in {input_folderpath}")
        return
    
    print(f"Found {len(nd2_files)} ND2 files in {input_folderpath}")
    
    # Process each ND2 file
    for nd2_file in tqdm(nd2_files, desc="Converting ND2 files"):
        basename = os.path.basename(nd2_file)
        name_without_ext = os.path.splitext(basename)[0]
        output_file = os.path.join(output_folderpath, f"{name_without_ext}.n5")
        
        print(f"Converting {nd2_file} to {output_file}")
        try:
            # Use the CLI function with command-line arguments
            sys_argv = [nd2_file, output_file]
            nd2_to_bdv(sys_argv)
            print(f"Successfully converted {basename} to BDV/XML+N5 format")
        except Exception as e:
            print(f"Error converting {basename}: {str(e)}")
