import aicspylibczi
import tifffile
import numpy as np
import os
# import xml.etree.ElementTree as ET
import math

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

# def calculate_chunks(seq_dim, max_size_gb, bytes_per_pixel=2):
#     max_bytes = max_size_gb * 1024**3
#     pixels_per_chunk = max_bytes // bytes_per_pixel  # Max pixels per chunk
    
#     # Calculate total pixels in the dataset
#     total_pixels = 1
#     for axis, (start, end) in seq_dim.items():
#         total_pixels *= (end - start)
    
#     # Chunking along the first expandable axis (e.g., 'M')
#     for axis in ['M', 'Z']:  # Order of priority
#         dim_size = seq_dim[axis][1] - seq_dim[axis][0]
#         pixels_per_other_dims = total_pixels // dim_size
#         if pixels_per_other_dims < pixels_per_chunk:
#             chunks = math.ceil(dim_size / (pixels_per_chunk / pixels_per_other_dims))
#             chunk_ranges = [
#                 (
#                     seq_dim[axis][0] + i * (dim_size // chunks),
#                     seq_dim[axis][0] + (i + 1) * (dim_size // chunks)
#                 )
#                 for i in range(chunks)
#             ]
#             return chunk_ranges, axis  # Return the chunks and axis used
        
def get_chunk_bbox(czi_file, max_size_chunk_gb, pixel_type):
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
        nb_pix_seq = w * h * z  # Total number of pixels in the sequence
        size_seq = nb_pix_seq * bytes_per_pix  # Total size in bytes
        nb_chunk = math.ceil(size_seq / max_size_chunk)  # Number of chunks (rounded up)
        nb_pix_chunk = math.ceil(nb_pix_seq / nb_chunk)  # Pixels per chunk (rounded up)
        nb_pix_xy = nb_pix_chunk / z  # Pixels per slice (XY-plane)
        l = math.ceil(np.sqrt(nb_pix_xy))  # Length of chunk side (rounded up)
        chunk_idx = [x_min, y_max, l, nb_chunk, z]
        chunk_idx_list.append(chunk_idx)

        

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
    bbox_list = get_chunk_bbox(czi_file, max_size_chunk_gb, pixel_type)
    for s, seq in enumerate(sequences):
        if seq['S'][1]-seq['S'][0] == 1:
            x_min, y_max, l, nb_chunks = bbox_list[s]
            for i in range(nb_chunks):
                d = i*l
                x0 = x_min + d
                y0 = y_max - d
                z_stack_list = [czi_file.read_mosaic(region = (x0, y0, l, l), 
                                             scale_factor=1.0, 
                                             C=correct_channel_idx, 
                                             Z=z,
                                                    dtype = pixel_type,
                                                )[0][0]
                                    for z in z_stacks]

            save_filepath = os.path.join(save_folderpath, f"seq_{i}_mosaic_{chunk_range}.tiff")
            # Save the chunk as a TIFF file
            tifffile.imsave(save_filepath, image)


# # Print information about the subblock
# print(f"  Coordinates: {subblock.dimension_entries}")
# print(f"  File Offset: {subblock.file_position}")
# print(f"  Compressed Size: {subblock.compressed_size}")
# print(f"  Uncompressed Size: {subblock.stored_size}")

# # Access the raw data for this subblock
# print(f"  Raw Data Length: {len(chunk_data)} bytes")


# def chunk_and_save_czi(czi_file, save_folderpath, chunk_size = 30, channel_name = 'EGFP'):
#     # If czi_file is a string it may be the filepath.
#     # Else the file was already readen.
#     if isinstance(czi_file, str):
#         czi_file = aicspylibczi.CziFile(czi_file)

#     # Take the correct chanel that contains the microglia
#     metadata = czi_file.meta
#     display_setting = metadata.find(".//DisplaySetting")
#     channels = display_setting.find("Channels")
#     channel_names = [channel.get("Name") for channel in channels.findall("Channel")]
#     correct_channel_idx = channel_names.index(channel_name)
    
#     # Get the number of bytes per pixel depending on the dtype of pixels
#     pixel_type = czi_file.pixel_type
#     if '16' in pixel_type:
#         bytes_per_pixel = 2
#         pixel_type = np.uint16

#     else:
#         # if uint8
#         bytes_per_pixel = 1
#         pixel_type = np.uint8

#     # Create the folder were files are stored if doesn't exist.
#     os.makedirs(save_folderpath, exist_ok=True)

#     # Iterate through sequences i.e. slices of brain on one slide
#     sequences = czi_file.get_dims_shape()
#     for i, seq in enumerate(sequences):
#         if seq['S'][1]-seq['S'][0] == 1:
#             chunk_range_list, ax = calculate_chunks(seq, chunk_size, bytes_per_pixel = bytes_per_pixel)
#         #TO DO in case the tile is to big 
#         # if ax == 'Z':
#         #     for m in range(seq['M'][0], seq['M'][1]):
#         #         for chunk_range in chunk_range_list:
#         #             kwargs = {'M': m, ax: chunk_range}
#         #             image_data = czi_file.read_image(C = correct_channel_idx, 
#         #                                             S = i,
#         #                                             dtype = pixel_type
#         #                                             **kwargs)
#         # else:
#         for chunk_range in chunk_range_list:
#             tile_dict = {}
#             for m in range(chunk_range[0], chunk_range[1]):
#                 image_data = czi_file.read_image(C = correct_channel_idx, 
#                                                 S = i,
#                                                 M = m,
#                                                 dtype = pixel_type,
#                                                 )

#                 image = image_data[0]
#                 axis = np.array(image_data[1])

#                 # 1) Reduce the image to the axis that matter
#                 axis_idx_map = {item[0]: index for index, item in enumerate(axis)}
#                 axis_to_keep = ['M', 'X', 'Y', 'Z']
#                 axis_idx_to_keep = [axis_idx_map[key] for key in axis_to_keep]
#                 new_axis = tuple(slice(None) if i in axis_idx_to_keep else 0 for i in range(len(axis)))
#                 # Reduced image and axis
#                 image = image[new_axis]
#                 axis = axis[np.sort(axis_idx_to_keep)]

#                 # 2) Sort the axis following axis_to_keep order
#                 # Step 1: Create a mapping of axis labels to their current positions
#                 current_axis_order = [ax[0] for ax in axis]  # Extract the axis labels
#                 reorder_indices = [current_axis_order.index(label) for label in axis_to_keep]
#                 # Step 2: Use NumPy's transpose to reorder the dimensions of the image
#                 image = np.transpose(image, axes=reorder_indices)
#                 # # Step 3: Reorder the axis to match `axis_to_keep`
#                 # axis = axis[np.argsort(reorder_indices)]  # Sort according to the new order
#                 tile_dict[m] = image 
#             save_filepath = os.path.join(save_folderpath, f"seq_{i}_mosaic_{chunk_range}.tiff")
#             # Save the chunk as a TIFF file
#             tifffile.imsave(save_filepath, image)