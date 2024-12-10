import aicspylibczi
import tifffile
import numpy as np
import os
# import xml.etree.ElementTree as ET
import math
from utils import divide_image_into_mesh, generate_mesh_coordinates

def get_channel_info(czi_file):
    if isinstance(czi_file, str):
        czi_file = aicspylibczi.CziFile(czi_file)
    # Pretty print metadata
    metadata = czi_file.meta
    # ET.dump(metadata)
    # Find the <DisplaySetting> tag
    display_setting = metadata.find(".//DisplaySetting")

    if display_setting is not None:
        # Find the <Channels> tag inside <DisplaySetting>
        channels = display_setting.find("Channels")
        
        if channels is not None:
            # Iterate over each <Channel> tag
            for channel in channels.findall("Channel"):
                channel_id = channel.get("Id")  # Get the channel ID attribute
                channel_name = channel.get("Name")  # Get the channel Name attribute
                
                # Extract additional details
                dye_name = channel.findtext("DyeName")
                emission = channel.findtext("DyeMaxEmission")
                excitation = channel.findtext("DyeMaxExcitation")
                color = channel.findtext("Color")
                
                print(f"Channel ID: {channel_id}")
                print(f"Name: {channel_name}")
                print(f"Dye: {dye_name}")
                print(f"Emission: {emission}")
                print(f"Excitation: {excitation}")
                print(f"Color: {color}")
                print("-" * 30)
        else:
            print("<Channels> tag not found inside <DisplaySetting>.")
    else:
        print("<DisplaySetting> tag not found in metadata.")
    return 


def get_czi_info(czi_file):
    if isinstance(czi_file, str):
        # Size
        file_size = os.path.getsize(czi_file)
        print(f"File size: {file_size / (1024 **3):.2f} GB")  
        czi_file = aicspylibczi.CziFile(czi_file)  
    # Content
    dims = czi_file.get_dims_shape()
    print("Number of sequences:", len(dims))
    for dim in dims:
        for i, key in enumerate(dim.keys()):
            print(f"Seq {i}, {key} size:", dims[0][key][1]-dims[0][key][0])
        print('')
    return

        
def get_chunk_bbox(czi_file, max_size_chunk_gb=30):
    max_size_chunk = max_size_chunk_gb * 1024**3
    if isinstance(czi_file, str):
        czi_file = aicspylibczi.CziFile(czi_file)  
    bbox = czi_file.get_all_scene_bounding_boxes()
    dims = czi_file.get_dims_shape()
    pixel_type = czi_file.pixel_type
    if '16' in pixel_type:
        bytes_per_pix = 2
    else:
        # if uint8
        bytes_per_pix = 1
    nb_seq = len(bbox)
    chunk_idx_list = []
    for s in range(nb_seq):
        z = dims[s]['Z'][1] - dims[s]['Z'][0]  # Depth (Z-axis)
        x_min, y_max, w, h = bbox[s].x, bbox[s].y, bbox[s].w, bbox[s].h  # Bounding box details
        nb_pix_chunk = int(max_size_chunk / bytes_per_pix)
        nb_pix_chunk_xy = int(nb_pix_chunk / z)
        nb_pix_chunk_l = int(math.sqrt(nb_pix_chunk_xy))
        nb_chunks_x, nb_chunks_y = divide_image_into_mesh(w, h, square_size=nb_pix_chunk_l)
        chunk_idx = [x_min, nb_chunks_x, y_max, nb_chunks_y, nb_pix_chunk_l, z]
        chunk_idx_list.append(chunk_idx)
    return chunk_idx_list
        

def chunk_and_save_czi(czi_file, save_folderpath, max_size_chunk_gb = 30, channel_name = 'EGFP'):
    # If czi_file is a string it may be the filepath.
    # Else the file was already readen.
    if isinstance(czi_file, str):
        czi_file = aicspylibczi.CziFile(czi_file)

    # Take the correct chanel that contains the microglia
    metadata = czi_file.meta
    display_setting = metadata.find(".//DisplaySetting")
    channels = display_setting.find("Channels")
    channel_names = [channel.get("Name") for channel in channels.findall("Channel")]
    correct_channel_idx = channel_names.index(channel_name)
    
    # Get the number of bytes per pixel depending on the dtype of pixels
    pixel_type = czi_file.pixel_type
    if '16' in pixel_type:
        pixel_type = np.uint16
    else:
        # if uint8
        pixel_type = np.uint8

    # Create the folder were files are stored if doesn't exist.
    os.makedirs(save_folderpath, exist_ok=True)

    # Iterate through sequences i.e. slices of brain on one slide
    sequences = czi_file.get_dims_shape()
    bbox_list = get_chunk_bbox(czi_file, max_size_chunk_gb)
    for s, seq in enumerate(sequences):
        if seq['S'][1]-seq['S'][0] == 1:
            x_min, nb_chunks_x, y_max, nb_chunks_y, l, z_len = bbox_list[s]
            xy_coordinates = generate_mesh_coordinates(num_squares_x=nb_chunks_x, 
                                           num_squares_y=nb_chunks_y, 
                                           square_size=l, 
                                           x0=x_min, y0=y_max)
            for xy in xy_coordinates:
                z_stack_list = [czi_file.read_mosaic(region = (xy[0], xy[1], l, l), 
                                             scale_factor=1.0, 
                                             C=correct_channel_idx, 
                                             Z=z,
                                            dtype = pixel_type,
                                            )[0][0] # The function returns an array (1,1,y,x)
                                    for z in range(z_len)]
                chunk_image = np.stack(z_stack_list, axis=0)
                print(chunk_image.shape)
                save_filepath = os.path.join(save_folderpath, f"seq_{s}_chunk_{xy}.tiff")
                # Save the chunk as a TIFF file
                tifffile.imsave(save_filepath, chunk_image)
