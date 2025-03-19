# Generate SWC from Filaments in IMS files  

## Overview

When you have created filaments in an IMS file, you can convert these filaments into SWC file where each microglia skeleton is stored in a SWC file.

# How to Generate SWC from Filaments in IMS files Using the Windows Computer of the Lab

1) Open a terminal.

2) Go to the directory containing the code of interest. To do so, write in the terminal:  
   `cd C:\Users\siege\Desktop\preprocess_images\scripts`

3) Now you have to check 2 parameters:  
   - The first parameter is the path to the folder containing the new IMS files.  
   - The second parameter is the path to the folder to store the new SWC files.  

4) you can run the code with your parameters. To do so, write in the terminal:  
  `.\run_skeletonize.bat "input_folder_path" "output_folder_path"`
   - `input_folder_path` is a path like `\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (female)\BRAIN\KXA\FKBP5\FKBP5KO`
   - `output_folder_path` is a path like `\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (female)\BRAIN\KXA\FKBP5\FKBP5KO\SWC`
  
  a. Make sure to add "" around the paths.
  b. you can use ctrl c and ctrl v on terminal to copy and paste the paths.

# Rename and Store CZI Files

(preprocess_img) PS C:\Users\siege\Desktop\preprocess_images\scripts> python run_a_store_czi.py --input_folderpath \\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\7568_siegegrp_AlVe
folder_path <class 'str'> \\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\7568_siegegrp_AlVe
Traceback (most recent call last):
  File "C:\Users\siege\Desktop\preprocess_images\scripts\run_a_store_czi.py", line 65, in <module>
    main()
  File "C:\Users\siege\Desktop\preprocess_images\scripts\run_a_store_czi.py", line 52, in main
    infoframe = store_raw_images(input_folderpath=input_folderpath,
  File "c:\users\siege\desktop\preprocess_images\src\io_images.py", line 104, in store_raw_images
    dataframe = get_images_infoframe(input_folderpath,
  File "c:\users\siege\desktop\preprocess_images\src\io_images.py", line 24, in get_images_infoframe
    folder_content = os.listdir(folderpath)
OSError: [WinError 1326] The user name or password is incorrect: '\\\\scratch4.ista.ac.at\\scratch\\siegegrp\\_ImageDrop\\Zeiss-AxioScan-Z1\\7568_siegegrp_AlVe'

## Overview

When you receive the CZI files from the Iof, they can be automatically renamed and stored. The storage process is automated to ensure that the files are well organized in a tree structure as follows: `Age/Sex/Animal/`. 

Each file is renamed according to this pattern: `raw_image_Age_xm_Sex_y_Animal_z_Slide_i.czi`  
Where:  
- `x` is the age in months  
- `y` is either "M" (Male) or "F" (Female)  
- `z` is the index of the animal, starting from 1  
- `i` is the index of the slide, starting from 0  

This standardization of file names helps facilitate the next processing steps, such as chunking and tracking.

## Important Notes

- **Excel Register Update**: Ensure that the register Excel file is up-to-date. Specifically:  
  - The **Age** column should contain integers.  
  - The **Sex** column should use uppercase letters ("M" or "F").  
  - The **Animal** column should contain integers.  
  - The **Slide_no** column must contain a unique integer for each row. If two rows share the same number in the **Slide_no** column, they could be mixed up.

- **Register File Update**: After a CZI file is stored, the register Excel file is updated automatically by adding an "X" in the **renamed/stored** column of the row corresponding to the file that was renamed and stored.

# How to Rename and Store Using the Windows Computer of the Lab

1) The register Excel file containing the metadata of the slides should be closed.

2) Open a terminal as admnistrator, right click run as administrator.

3) Activate the environment containing the necessary Python packages. To do so, write in the terminal:  
   `conda activate preprocess_img`

4) Go to the directory containing the code of interest. To do so, write in the terminal:  
   `cd C:\Users\siege\Desktop\preprocess_images\scripts`

5) Now you have to check 3 parameters:  
   - The first parameter is the path to the folder containing the new CZI files.  
     By default: `\\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\7568_siegegrp_AlVe`  
   - The second parameter is the path to the folder of the project. This folder should contain a folder `raw_images` and a register Excel file.  
     By default: `\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS`  
   - The third parameter is the name of the register Excel file that should be in the folder of the project.  
     By default: `slide_register_JoNa.xlsx`

6) If the default parameters are correct, you can run the code. To do so, write in the terminal:  
   `python run_a_store_czi.py`

   If the default parameters are not correct, you can run the code with your parameters. To do so, write in the terminal:  
   `python run_a_store_czi.py --input_folderpath a --output_folderpath b --register_name c`  
   where:
   - `a` is a path like `\\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\7568_siegegrp_AlVe`
   - `b` is a path like `\\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS`
   - `c` is a name of a file like `slide_register_JoNa.xlsx`

   If some parameters are already correct by default, you do not need to rewrite them. For example, if the project folder has a new name, you can write:  
   `python run_a_store_czi.py --output_folderpath \\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\new_name`

### Bonus:
Instead of writing the full command with the long argument names, you can use the shortened versions:  
Instead of:  
`run_a_store_czi.py --input_folderpath a --output_folderpath b --register_name c`  
You can write:  
`run_a_store_czi.py -ifp a -ofp b -rn c`



# Chunk czi files in tif files

# TrAIce tif files 
CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip   /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/glass_slide/tif_filename -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia -mp ./ -spsl ./ -nw 1 -bsp ./


Updated command:

CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/age/sex/animal/slide/microglia_Age_age_Sex_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -tp "(0.3, 0.3, 1.0)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia/animal/sex/animal/slide/microglia_Age_age_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -mp ./ -spsl ./ -nw 1 -bsp ./