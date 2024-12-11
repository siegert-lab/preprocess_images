from process_czi import get_czi_info, chunk_and_save_czi
from process_ims import get_ims_info, chunk_and_save_ims 

from io_images import get_images_infoframe

# Parameters
folderpath = "data"
conditions = []
extension = '.czi'
result_folderpath = 'results'
chunk_size = 3
channel_name = 'EGFP'
infoframe = get_images_infoframe(folderpath, conditions=conditions, extension=extension)

for i, row in infoframe.iterrows():
    file_name = row['file_name']
    save_foldername = file_name[:-4]
    save_folderpath = result_folderpath + "/" + save_foldername

    extension = file_name[-4:]

    file_path = row['file_path']
    if 'czi' in extension:
        get_czi_info(file_path)
        chunk_and_save_czi(file_path, save_folderpath, 
                           max_size_chunk_gb = chunk_size, channel_name = channel_name)
    elif 'ims' in extension:
        get_ims_info(file_path)
        chunk_and_save_ims(file_path, save_folderpath, 
                           max_size_chunk_gb = chunk_size, channel_idx = 1)
    else:
        print("No function to chunk this file format.")