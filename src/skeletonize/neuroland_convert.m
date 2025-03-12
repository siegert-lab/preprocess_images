swc_files = dir('D:\Ryan\Retina_traces\*\*\*\*\*\*\*.swc');

for i=1:length(swc_files)
    swc_fn = swc_files(i).name;
    swc_dir = swc_files(i).folder;
    swc_full_fn = [swc_dir '\' swc_fn];

    if ~contains(swc_full_fn, 'nl_corrected')
        if isfile([swc_full_fn(1:end-4), '_nl_corrected.swc"'])
            disp([swc_full_fn(1:end-4), '_nl_corrected.swc"'], ' is already there... Skipping...')
        else
            neuroland_args = ['"', swc_full_fn, '" --export "', swc_full_fn(1:end-4), '_nl_corrected.swc"', ' swc'];
            %neuroland_command = [neuroland_conerter_exe, ' ', neuroland_args];
            neuroland_command = ['NLMorphologyConverter', ' ', neuroland_args];
            disp(['  ...converting ' swc_full_fn ' with neuroland']);
            ec = system(neuroland_command);
            if ec > 0
                disp(' Neuroland conversion failed')
            end
        end
    end
end
    