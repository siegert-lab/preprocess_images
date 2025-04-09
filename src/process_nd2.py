#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script converts all ND2 files in a folder to BDV/XML+N5 format.
Usage: python process_nd2.py --input_folderpath /path/to/nd2/files --output_folderpath /path/to/output
"""

import os
import re
from tqdm import tqdm
import multiprocessing

from bdv_toolz.cli import nd2_to_bdv
import sys

from bdv_toolz.bdv_creation import create_bdv_n5_multi_tile

from io_images import get_images_infoframe

def extract_animal_from_filename(filename):
    """
    Extract Animal ID from a filename.
    
    Parameters
    ----------
    filename : str
        The filename to extract animal id from
        
    Returns
    -------
    str or None
        Extracted animal ID or None if not found
    """
    animal_match = re.search(r'Animal_(\d+)', filename)
    if animal_match:
        return animal_match.group(1)
    return None

def set_animal_column_from_dataframe(dataframe):
    """
    Extract Animal IDs from filenames in the dataframe.
    
    Parameters
    ----------
    dataframe : pd.DataFrame
        DataFrame containing a 'file_name' column with filenames
        
    Returns
    -------
    pd.DataFrame
        Updated DataFrame with 'Animal' column added
    """
    # Create Animal column if it doesn't exist
    if 'Animal' not in dataframe.columns:
        dataframe['Animal'] = None
    
    # Extract Animal IDs from filenames
    for idx, row in dataframe.iterrows():
        if 'file_name' in row:
            animal_id = extract_animal_from_filename(row['file_name'])
            if animal_id is not None:
                dataframe.loc[idx, 'Animal'] = animal_id
    
    return dataframe

def get_nd2_infoframe_asas(folderpath):
    """
    Get information from ND2 files in the specified folder.
    Extracts metadata from filenames matching the pattern: slide_Pxx_S_i00j.nd2
    where:
    - xx can be 21, 7, or other digits (Age)
    - S is F or M (Sex)
    - i is a digit (Animal)
    - j is 1 or 2 (Side, 1=L, 2=R)
    
    Parameters
    ----------
    folderpath : str
        Path to the folder containing ND2 files
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing file information and extracted metadata
    """
    # Use the get_images_infoframe function to get info about ND2 files
    info_frame = get_images_infoframe(folderpath, extension=".nd2", conditions=[])
    
    # Regular expression pattern for extracting metadata from filenames
    pattern = r'slide_P(\d+)_([FM])_(\d)00(\d)\.nd2'
    
    # Extract metadata from filenames
    rows_to_drop = []

    for idx, row in info_frame.iterrows():
        basename = row['file_name']
        match = re.match(pattern, basename)

        if match:
            # Extract metadata and add to dataframe
            info_frame.loc[idx, 'Age'] = f"P{match.group(1)}"
            info_frame.loc[idx, 'Sex'] = match.group(2)
            info_frame.loc[idx, 'Animal'] = match.group(3)
            info_frame.loc[idx, 'Side'] = "L" if match.group(4) == "1" else "R"
        else:
            print(f"Warning: File {basename} does not match the expected pattern and will be removed.")
            rows_to_drop.append(idx)

    # Drop rows that didn't match
    info_frame = info_frame.drop(index=rows_to_drop).reset_index(drop=True)

    return info_frame

def set_output_asas(info_frame, output_folderpath):
    for idx, row in info_frame.iterrows():
        if all(col in row for col in ['Age', 'Sex', 'Animal', 'Side']):
            # Create output filename with the format: retina_Age_Pxx_Sex_S_Animal_i_Side_j.n5
            info_frame.loc[idx, 'output_filename'] = f"retina_Age_{row['Age']}_Sex_{row['Sex']}_Side_{row['Side']}_Animal_{row['Animal']}.n5"
            
            # Create subdirectory structure: Age/Sex/Side
            subfolder = os.path.join(
                output_folderpath, 
                row['Age'], 
                row['Sex'], 
                row['Side']
            )
            
            # Create the full output filepath
            info_frame.loc[idx, 'output_filepath'] = os.path.join(subfolder, info_frame.loc[idx, 'output_filename'])
            
            # Create the subfolder immediately
            os.makedirs(subfolder, exist_ok=True)
    return info_frame

def check_already_converted_asas(info_frame, existing_files):
    if not existing_files.empty:
        # Extract Animal information from filenames
        existing_files = set_animal_column_from_dataframe(existing_files)
        
        # Mark files that have already been converted by comparing the columns directly
        for idx, row in info_frame.iterrows():
            for _, exist_row in existing_files.iterrows():
                if (row['Age'] == exist_row['Age'] and 
                    row['Sex'] == exist_row['Sex'] and 
                    row['Side'] == exist_row['Side'] and
                    row['Animal'] == exist_row['Animal']):

                    info_frame.loc[idx, 'conversion_status'] = 'Already converted'
                    print(f"\nFile {row['file_name']} already converted, skipping\n")
                    break
    else:
        print("\nNo existing files found in the output folder.\n")
    return info_frame

def process_nd2_file(row):
    """Process a single ND2 file."""

    nd2_file_path = row['file_path']
    output_file_path = row['output_filepath']
    
    print(f"\nConverting {nd2_file_path} to {output_file_path}\n")
    try:
        create_bdv_n5_multi_tile(
            nd2_file_path, 
            out_n5=output_file_path,
            tiles=None,
            channels=None,
            rounds=None,
            z_slc=None,
            yes=True,
            ca_json=None,
            ff_json=None,
            overwrite='skip',
            downscale_factors=((1, 2, 2), (1, 2, 2)),
            read_tile_positions=True
        )
        print(f"\nSuccessfully converted {row['file_name']} to BDV/XML+N5 format\n")
        return row['file_name'], 'Success'
    except Exception as e:
        print(f"\nError converting {row['file_name']}: {str(e)}\n")
        return row['file_name'], f'Error: {str(e)}'

def parallel_process_nd2(info_frame):
    """Run ND2 file conversion in parallel."""
    # total_cpus = multiprocessing.cpu_count()
    # num_cpus = max(1, int(total_cpus * 0.5))
    num_cpus = 5
    with multiprocessing.Pool(num_cpus) as pool:
        results = list(tqdm(pool.imap(process_nd2_file, [row for _, row in info_frame.iterrows()]), 
                            total=len(info_frame), 
                            desc="Converting ND2 files"))

    # Update dataframe with conversion results
    for file_name, status in results:
        info_frame.loc[info_frame['file_name'] == file_name, 'conversion_status'] = status

    return info_frame

def loop_process_nd2(info_frame):
    """Run ND2 file conversion sequentially."""
    results = []
    for _, row in tqdm(info_frame.iterrows(), total=len(info_frame), desc="Converting ND2 files"):
        result = process_nd2_file(row)
        results.append(result)

    # Update dataframe with conversion results
    for file_name, status in results:
        info_frame.loc[info_frame['file_name'] == file_name, 'conversion_status'] = status

    return info_frame    

def convert_nd2_to_bdv_asas(input_folderpath, output_folderpath, is_parallel):
    """
    Convert ND2 files in the infoframe to BDV/XML+N5 format and save them in output_folderpath.
    
    Parameters
    ----------
    input_folderpath : str
        Path to the folder containing ND2 files
    output_folderpath : str
        Path to the folder where N5 files will be saved
    
    Returns
    -------
    pd.DataFrame
        Updated DataFrame with all files in the output folder after conversion
    """
    # Ensure output directory exists
    os.makedirs(output_folderpath, exist_ok=True)

    info_frame = get_nd2_infoframe_asas(input_folderpath)
    
    if info_frame.empty:
        print("No valid ND2 files found in the infoframe")
        return info_frame
    else:
        print("These files were found")
        print(info_frame.sort_values(by='file_name').to_string(index=False))
        print('')
    
    # Create output filename and filepath columns
    info_frame = set_output_asas(info_frame, output_folderpath=output_folderpath)

    
    # Check for already converted files
    print("\nChecking for already converted files...\n")

    existing_files = get_images_infoframe(output_folderpath, extension=".n5", conditions=['Age', 'Sex', 'Side'])
    
    # Initialize conversion_status column to None
    if 'conversion_status' not in info_frame.columns:
        info_frame['conversion_status'] = None
    
    # Only check for existing files if any were found
    info_frame = check_already_converted_asas(info_frame = info_frame, existing_files= existing_files)

    # Remove already converted files    
    filtered_info_frame = info_frame[info_frame['conversion_status'] != 'Already converted']
    print("These files will be converted")
    print(filtered_info_frame.sort_values(by='file_name').to_string(index=False))
    print('')
    # Process each ND2 file in the dataframe
    if is_parallel:
        filtered_info_frame = parallel_process_nd2(filtered_info_frame)
    else:
        filtered_info_frame = loop_process_nd2(filtered_info_frame)

    # Get updated list of files in the output folder after conversion
    print("\nGetting final state of output folder...\n")
    updated_existing_files = get_images_infoframe(output_folderpath, extension=".n5", conditions=['Age', 'Sex', 'Side'])
    
    # Extract Animal information from filenames
    updated_existing_files = set_animal_column_from_dataframe(updated_existing_files)
    
    return updated_existing_files
