# Rename and Store CZI Files

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

- **Register File Update**: After a CZI file is stored, the register Excel file is updated by adding an "X" in the **renamed/stored** column of the row corresponding to the file that was renamed and stored.

# How to Rename and Store Using the Windows Computer of the Lab

1) The register Excel file containing the metadata of the slides should be closed.

2) Open a terminal.

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