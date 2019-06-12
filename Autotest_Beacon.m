function Autotest_Beacon(filename,Parameters,entry,model_name,Log_foldername,rawdata_folder,model_path,init_name,Row_number)
% April 10th 2019
% 

  
    bdclose all;
    % verify rawdata model and init file
    datafile = fullfile(rawdata_folder,filename);
    modelfile = fullfile(model_path,model_name);
    initfile = fullfile(model_path,init_name);
    
    if ~isfile(datafile)
        sprintf('Data file %s is not found under folder %s.',filename, rawdata_folder);
        return;
    end
    
    if ~isfile(modelfile)
        sprintf('model file %s is not found under folder %s.',model_name, model_path);
        return;
    end
    
    if ~isfile(initfile)
        sprintf('model init file %s is not found under folder %s.',init_name, model_path);
        return;
    end

    


tic 
%%% simulation running procedure:
%%% -> initializa the parameters value for simulink model 
%%% -> create a temp folder for saving all value and structure for simulink
%%% -> run the simulation and create log.mat file for saving result.

Param_map=Seperate_and_struct(Parameters);
eval(extractBefore(init_name,'.m')); % call initial .m of the model
    
%% Generate temp directory 
cwd=pwd;
temp_output_dir=char(Log_foldername);
if 7~=exist(temp_output_dir,'dir')
    mkdir(temp_output_dir);
end

tempdir = strcat([cwd,'/',[extractBefore(model_name,'.slx'),'_',num2str(entry)]]);
mkdir(tempdir);
cd(tempdir);


%% start simulaton
options=simset('Srcworkspace','current');
disp(['Start Simulation ...']);
load_system(modelfile);
sim(modelfile,[],options);
disp(['Simulation ended...']);
disp(strcat(['Simulation for Rawdata ',filename,'is completed']));
%% generate temp dir to store log file
thisLogFile=strcat(cwd,'/',char(Log_foldername),'/',extractBefore(model_name,'.slx'),'_Case',...
    num2str(Row_number),'_ParamRow_',num2str(str2num(entry)+1),'.mat');
movefile('thisLogFile.mat',thisLogFile);
close_system(modelfile,0);
cd(cwd);
rmdir(tempdir,'s');


    
toc
clear;
exit();


end