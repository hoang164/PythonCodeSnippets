%%%%%%%%%%%%%%%%%%%% parameters for the model%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%% only part need to change in each function%%%%%
Raw_data = load(datafile); % load raw .mat data
FchA = ceil(2.048*Raw_data.chA+2048);
thisSignal = [Raw_data.timeMs FchA]; 
end_time = thisSignal(end,1);
SAMPLE_TIME_MS = Param_map.SAMPLE_TIME; %% FPGA
SLIDING_WINDOW_MS = Param_map.WINDOW; %% Bosheng modify

BIT_SHIFT = ceil(log2(SLIDING_WINDOW_MS/SAMPLE_TIME_MS));
WINDOW_LENGTH = pow2(BIT_SHIFT); %FPGA 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%     

