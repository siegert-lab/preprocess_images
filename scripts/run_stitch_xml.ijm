// read dataset path, number of tiles as commandline arguments
args = getArgument()
args = split(args, " ");

basePath = args[0];
if (!endsWith(basePath, File.separator))
{
    basePath = basePath + File.separator;
}
tilesX = args[1];
tilesY = args[2];

// define dataset
run("Define dataset ...",
    "define_dataset=[Automatic Loader (Bioformats based)]" +
    " project_filename=dataset.xml path=" + basePath + "C*-7*.tif exclude=10" +
    " pattern_0=Channels pattern_1=Tiles modify_voxel_size? voxel_size_x=1.0000" +
    " voxel_size_y=1.0000 voxel_size_z=2 voxel_size_unit=pixels " +
    "move_tiles_to_grid_(per_angle)?=[Move Tile to Grid (Macro-scriptable)] grid_type=[Snake: Right & Down      ]" +
    " tiles_x="+tilesX+" tiles_y="+tilesY+" tiles_z=1 overlap_x_(%)=10 overlap_y_(%)=10 overlap_z_(%)=10" +
    " keep_metadata_rotation how_to_load_images=[Re-save as multiresolution HDF5] " +
    "dataset_save_path=/Volumes/davidh-ssd/bigstitcher-example-data/grid-3d check_stack_sizes " +
    "subsampling_factors=[{ {1,1,1}, {2,2,2} }] hdf5_chunk_sizes=[{ {16,16,16}, {16,16,16} }] " +
    "timepoints_per_partition=1 setups_per_partition=0 use_deflate_compression " +
    "export_path=" + basePath + "dataset");

// calculate pairwise shifts
run("Calculate pairwise shifts ...",
    "select="+basePath+"dataset.xml process_angle=[All angles] process_channel=[All channels]" +
    " process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints]" +
    " method=[Phase Correlation] channels=[Average Channels] downsample_in_x=2 downsample_in_y=2 downsample_in_z=2");

// filter shifts with 0.7 corr. threshold
run("Filter pairwise shifts ...",
    "select="+basePath+"dataset.xml filter_by_link_quality min_r=0.7 max_r=1 " +
    "max_shift_in_x=0 max_shift_in_y=0 max_shift_in_z=0 max_displacement=0");

// do global optimization
run("Optimize globally and apply shifts ...",
    "select="+basePath+"dataset.xml process_angle=[All angles] process_channel=[All channels] " +
    "process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints]" +
    " relative=2.500 absolute=3.500 global_optimization_strategy=" +
    "[Two-Round using Metadata to align unconnected Tiles] fix_group_0-0,");

// fuse dataset, save as TIFF
run("Fuse dataset ...",
    "select="+basePath+"dataset.xml process_angle=[All angles] process_channel=[All channels] " +
    "process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints]" + 
    " bounding_box=[All Views] downsampling=1 pixel_type=[16-bit unsigned integer] interpolation=[Linear Interpolation]" +
    " image=[Precompute Image] blend produce=[Each timepoint & channel] fused_image=[Save as (compressed) TIFF stacks] " +
    "output_file_directory=" + basePath);

// quit after we are finished
eval("script", "System.exit(0);");