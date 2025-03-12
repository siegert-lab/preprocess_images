%% add ImarisReader class to Matlab search path
addpath(<full-path-to-folder-ImarisReader>)

%% change to directory of the Matlab function 'extract_filaments_from_imaris'
cd <path-to-script>

%% extract filaments of single Imaris (.ims) file
%% results will be exported to the folder '<full-path-to-ims-file>/swc'
extract_filaments_from_imaris(<full-path-to-ims-file>)

%% extract filaments for all Imaris files in folder 'i:\all\BioImaging\ForChristoph_ToConvert' 
ims_files = dir('i:\all\BioImaging\ForChristoph_ToConvert\*.ims')
for i=1:length(ims_files), extract_filaments_from_imaris([ims_files(i).folder ims_files(i).name]); end

==============================================
%example
addpath('\\istsmb3.ist.local\aventuri\Desktop\extract_filaments_from_imaris_v02\ImarisReader')
cd ('\\istsmb3.ist.local\aventuri\Desktop\extract_filaments_from_imaris_v02')
extract_filaments_from_imaris('\\istsmb3.ist.local\aventuri\Desktop\imaris filament\bl6_F_ctrlsal4_iba1_488_cd68_647_dapi_20161005.ims')



