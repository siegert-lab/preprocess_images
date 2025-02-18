# chunk_image


CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip   /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/glass_slide/tif_filename -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia -mp ./ -spsl ./ -nw 1 -bsp ./


Updated command:

CUDA_VISIBLE_DEVICES=0 trAIce img2swc -ip /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/chunk_images/age/sex/animal/slide/microglia_Age_age_Sex_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -wss "(128, 128, 16)" -wsb "(128, 128, 16)" -tp "(0.3, 0.3, 1.0)" -spd /mnt/archive/archive/siegegrp/AlVe/MORPHOMICS2.0_MICROGLIA_BRAIN_ATLAS/traced_microglia/animal/sex/animal/slide/microglia_Age_age_sex_animal_slide_seq_3_chunk_1_over_5_x__-37461_-27220__y__25669_35929__.tif -mp ./ -spsl ./ -nw 1 -bsp ./