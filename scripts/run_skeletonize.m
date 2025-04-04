function run_skeletonize(input_folder_path, output_folder_path)
    % Check if the required arguments are provided
    if nargin < 2
        error("Usage: run_skeletonize(input_folder_path, output_folder_path)");
    end
    addpath('../src/skeletonize/ImarisReader-master/');
    addpath('../src/skeletonize/');
    
    % For archive trial
    % fkbp5ko 
    % female
    %input_folder_path = '\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (female)\BRAIN\KXA\FKBP5\FKBP5KO';
    % per layer female
    %input_folder_path = '\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (female)\BRAIN\KXA\FKBP5\FKBP5KO\ALL CORTICAL LAYERS';
    
    %output_folder_path = '\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (female)\BRAIN\KXA\FKBP5\FKBP5KO\SWC';
    
    % male
    %input_folder_path = '\\fs.ista.ac.at\drives\aventuri\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (male)\BRAIN\KXA\FKBP5\FKBP5KO';
    %per layer male
    %input_folder_path = '\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (male)\BRAIN\KXA\FKBP5\FKBP5KO\ALL CORTICAL LAYERS';
    
    %output_folder_path = '\\fs.ista.ac.at\group\siegegrp\AlVe\_Bioimaging\Alessandro\Anesthetics (male)\BRAIN\KXA\FKBP5\FKBP5KO\SWC';
    % List all files in the folder (including subfolders)
    folder_contents = dir(input_folder_path);
    
    % Filter for only '.ims' files (case-insensitive)
    %ims_files = dir(fullfile(input_folder, '*.ims'));
    ims_files = folder_contents(~[folder_contents.isdir] & endsWith({folder_contents.name}, '.ims', 'IgnoreCase', true));
    
    did_not_pass = {};
    
    for i=1:length(ims_files)
        ims_fn = ims_files(i).name;
        ims_dir = ims_files(i).folder;
        % Use fullfile to join the directory and filename, which ensures correct path separators
        ims_full_fn = fullfile(ims_dir, ims_fn);
        % Display message indicating the file being processed
        disp(['Extracting fillaments from ' ims_full_fn]);
        %extract_filaments_from_imaris(ims_full_fn);
        try
            % Pass the input file and output folder to the function
            extract_filaments_from_imaris(ims_full_fn, output_folder_path);
        catch
            disp(['Did not succeed for ' ims_full_fn]);
            did_not_pass{end+1} = ims_full_fn;
        end
       
    end
    
    % Define the path for the failed conversions log file
    failed_log_path = fullfile(output_folder_path, 'failed_conversions.txt');
    
    % Open the file in write mode
    fid = fopen(failed_log_path, 'wt');
    
    % Write the failed file names to the log file
    for ii = 1:length(did_not_pass)
        fprintf(fid, '%s\n', did_not_pass{ii});
    end
    
    % Close the file
    fclose(fid);
    
    % Indicate script completion
    disp("Processing completed.");
end
