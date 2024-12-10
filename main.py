from process_czi import get_czi_info, chunk_and_save_czi
from io_images import get_images_infoframe

folderpath = "data"
conditions = ['Animal']
infoframe = get_images_infoframe(folderpath, conditions=['Animal'])

result_folderpath = 'results'
for i, row in infoframe.iterrows():
    save_folderpath = result_folderpath + "/" + row['file_name'][:-4]
    chunk_and_save_czi(row['file_path'], save_folderpath, chunk_size = 30, channel_name = 'EGFP')