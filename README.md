# Rename and Store the czi files
When you receive the czi files from the iof you can rename and store them automatically.
The storing is automatized so that the files are well organized in a tree structure "Age/Sex/Animal/
Each file is renamed following this pattern: raw_image_Age_xm_Sex_y_Animal_z_Slide_i.czi
Where x is the age in months, y is M or F, z is the index of the animal starting from 1 and i is the index of the slide starting from 0.
This standardization of the file names facilitate the net processing step such as chunking and traicing.

Warning: It is necessary that the register Excel file is updated. The column Age should contains integers, the column Sex should contains capital letters, the column Animal should contains integers and THE MOST IMPORTANT is the column Slide_no, it should contain an integer that is UNIQUE for each row. If two rows have the same number in the column Slide_no it can mix them.

How to rename and store using the windows computer of the lab:
1) The register excel file containing the metadata of the slides should be closed.

2) Open a terminal

3) Activate the environment containing the necessary python packages, to do so write in the terminal:
    conda activate preprocess_img

4) Go to the directory containing the code of interest, to do so write in the terminal:
    cd C:\Users\siege\Desktop\preprocess_images\scripts

5) Now you have to check 3 parameters:
    The first parameter is the path to the folder containing the new czi files.
    By default: \\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\7568_siegegrp_AlVe
    The second parameter is the path to the folder of the project. this folder should contains a folder raw_images and a register excel file.
    By default: \\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS
    The third parameter is the name of the register excel file that should be in the folder of the project.
    By default: slide_register_JoNa.xlsx

6) If the default parameters are correct you can run the code, to do so write in the terminal:
    python run_a_store_czi.py 

   Else if the default parameters are not good you can run the code with your parameters, to do so write in the terminal:
    python run_a_store_czi.py --input_folderpath a --output_folderpath b --register_name c
    with a being a path like \\scratch4.ista.ac.at\scratch\siegegrp\_ImageDrop\Zeiss-AxioScan-Z1\7568_siegegrp_AlVe
    with b being a path like \\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS
    and with c being a name of file like slide_register_JoNa.xlsx

    Of course if some parameters are already by default correct don't rewrite them, example if the project folder has a new name you can write:
    python run_a_store_czi.py --output_folderpath \\fs.ista.ac.at\drives\aventuri\archive\siegegrp\AlVe\new_name

Bonus: instead of 
            run_a_store_czi.py --input_folderpath a --output_folderpath b --register_name c
        you can write 
            run_a_store_czi.py -ifp a -ofp b -rn c


# chunk_image


CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip   /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/glass_slide/tif_filename -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia -mp ./ -spsl ./ -nw 1 -bsp ./


Updated command:

CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/age/sex/animal/slide/microglia_Age_age_Sex_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -tp "(0.3, 0.3, 1.0)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia/animal/sex/animal/slide/microglia_Age_age_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -mp ./ -spsl ./ -nw 1 -bsp ./