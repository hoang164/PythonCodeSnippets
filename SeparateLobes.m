% %% Find peak values of side lobes and mid lobe
% % load data
% run=1;
% i=1;
% %posNum=[1864,1496,1128,760,392,24,1841,1473,1105,737,369,1];
% %posNum=[1933,1565,1197,829,461,93,1887,1519,1151,783,415,47];
% %posNum=[2025,1657,1289,921,553,185,1979,1611,1243,875,507,139];
% posNum=[1];
% while run== 1
%     filename= strcat('Pos_', string(posNum(i)), '_GE_PGE2A616.mat');
%     i=i+1;
%     load(filename);
%     [pk, ploc]= findpeaks(chA,'MinPeakProminence',400,'MinPeakDistance',1000000);
%     figure('name', filename);
%     plot(chA)
%     hold on;
%     plot( ploc, pk, 'o')
%     [npk, nploc]= findpeaks(-chA,'MinPeakProminence',400,'MinPeakDistance',1000000);
%     hold on
%     plot( nploc, -npk, 'o')
%     try
%         title(string(pk+npk))
%     catch
%         disp(filename);
%     end
%     if i==length(posNum)+1
%         run=0;
%     end
% end

%% Loop through and Load data 
US_machine= 'Toshiba';
needleID= 'PGE2A1234';
%posNum= [369,374,379,384,389,737,742,747,752,757,1105,1110,1115,1120,1125,1473,1478,1483,1493,1841,1846,1851,1856,1861];
posNum= [1,6,11,16,21,369,374,379,384,389,737,742,747,752,757,1105,1110,1115,1120,1125,1473,1478,1483,1493,1841,1846,1851,1856,1861];

%[1,6,11,16,21]; % axis0=10, axis1=0, axis2= 0.02,5,10,15,20;
% [369,374,379,384,389]; % axis0=20, axis1=0, axis2= 0.02,5,10,15,20;
% [737,742,747,752,757]; % axis0=30, axis1=0, axis2= 0.02,5,10,15,20;
% [1105,1110,1115,1120,1125]; % axis0=40, axis1=0, axis2= 0.02,5,10,15,20;
% [1473,1478,1483,1493]; % axis0=50, axis1=0, axis2= 0.02,5,10,15,20;
% [1841,1846,1851,1856,1861]; % axis0=60, axis1=0, axis2= 0.02,5,10,15,20;

%[93,461,829,1197,1565,1933,139,507,875,1243,1611,1979,185,553,921,1289,1657,2025];

%[139,507,875,1243,1611,1979,185,553,921,1289,1657,2025];
%[93,461,829,1197,1565,1933];
%[47,415,783,1151,1519,1887];
%[1,369, 737,1105,1473,1841];

savedir= 'C:\Users\F53992\Documents\Bosheng_AutomationCodes\GitCommit\AutoTest\AutoTestStepbyStep\DataAnalysis\LobeProfile\';
for pos = posNum
    filename= strcat('Y:\Beacon_Datalibrary\RX_3D_WaterTank\3D_Toshiba_PGE2A1234_200ms\','Pos_', string(pos), '_', string(US_machine),'_', string(needleID), '.mat');    
    [filepath, name, ext]= fileparts(filename);
    save_name= strcat(savedir, name, '_extract_lobes.mat');
    if exist(save_name,'file') %skip if already there
        disp(strcat(string(pos), ' already exist'));
        continue
    end
    load(filename);
    if max(chA) < 33
        disp(filename);
        disp('noisy signal, skipped');
        continue
    end
    try
        if strcmp(US_machine,'eZono')
            get_lobes_eZono(chA, filename);
        else
            get_lobes(chA, filename);
        end  
    catch
        disp(pos) 
    end
end
disp('done!')

function get_lobes(chA, filename)

% Get signal in 1 period
period_length= 12000000;
en_chA= envelope(chA, 120000, 'peak');
max_point = find(en_chA==max(en_chA));
if length(max_point)>1
    max_point= max_point(1);
end
if (max_point+period_length/2)> length(en_chA) % partial right
    disp('max point is to the right')
    % look to the left:
    max_temp = find(en_chA==max(en_chA(1:(max_point-period_length/2))));
    if (max_temp-period_length/2)>=1
        crop_chA = chA(max_temp-period_length/2:max_temp+period_length/2);
    else
        crop_chA = chA(1:max_temp+period_length/2);
    end
elseif (max_point-period_length/2)<1
    disp('max point is to the left')
    max_temp = find(en_chA==max(en_chA((max_point+period_length/2):end)));
    % look to the right:
    if (max_temp+ period_length/2)<=length(chA)
        crop_chA = chA(max_temp-period_length/2:max_temp+period_length/2);
    else
        crop_chA = chA(max_temp-period_length/2:end);
    end
else
    disp('max point is in the middle')
    crop_chA= chA(max_point-period_length/2: max_point+period_length/2);
end

figure('name',filename); plot(crop_chA)
[yupper,ylower] = envelope(crop_chA,120000,'peak');
hold on; plot(yupper)

tag=1;

min_peak_prominence= round(max(chA)*2/5);
while tag==1
 [pk, ploc]= findpeaks(yupper,'MinPeakProminence',min_peak_prominence,'MinPeakDistance',1000000);
 if length(ploc) >=3
     tag=0;
 else
     min_peak_prominence= min_peak_prominence*4/5;
 end
end
hold on; plot(ploc, pk, 'o');
% Extract each lobe in GE machine
sub_window= 1500000;

%% Separating each lobe, lobes can have different lengths

if (ploc(1)-(sub_window/2))<1
    left_lobe= crop_chA(1:ploc(1)+(sub_window/2));
else
    left_lobe= crop_chA(ploc(1)-(sub_window/2):ploc(1)+(sub_window/2));
end
mid_lobe= crop_chA(ploc(2)-sub_window/2:ploc(2)+sub_window/2);
if (ploc(3)+(sub_window/2))>length(crop_chA)
    right_lobe= crop_chA(ploc(3)-(sub_window*1/2):end);
else
    right_lobe= crop_chA(ploc(3)-(sub_window*1/2):ploc(3)+(sub_window/2));
end

% Normalize and plot
norm_left= normalize(left_lobe, 'range', [-1 1]);
norm_mid= normalize(mid_lobe, 'range', [-1 1]);
norm_right= normalize(right_lobe, 'range', [-1 1]);
figure('name', filename)
set(gcf, 'Position',  [10, 10, 750, 600])
subplot 231
plot(norm_left); xlim([0 length(mid_lobe)]);
title('Left Lobe'); xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 232
plot(norm_mid); xlim([0 length(mid_lobe)]);
title('Mid Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 233
plot(norm_right); xlim([0 length(mid_lobe)]);
title('Right Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');

% plot the outline/envelope
[left_upper, left_lower]= envelope(norm_left,90000,'peak');
[mid_upper, mid_lower]= envelope(norm_mid,90000,'peak');
[right_upper, right_lower]= envelope(norm_right,90000,'peak');
subplot 234
plot(left_upper); xlim([0 length(mid_lobe)]);ylim([-1 1]);
hold on; plot(left_lower); 
title('Left Lobe'); xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 235
plot(mid_upper); xlim([0 length(mid_lobe)]);ylim([-1 1]);
hold on; plot(mid_lower);
title('Mid Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 236
plot(right_upper); xlim([0 length(mid_lobe)]);ylim([-1 1]);
hold on; plot(right_lower);
title('Right Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');

%save raw signal 
save_name= strcat(extractBefore(filename,'.mat'), '_extract_lobes.mat');
save(save_name, 'left_lobe', 'mid_lobe', 'right_lobe');

% save figure
save_fig_name= strcat(extractBefore(filename,'.mat'),'_extract_lobes.png');
saveas(gcf,save_fig_name)

end

%%
function get_lobes_eZono(chA, filename)
% Get signal in 1 period
period_length= 8000000;
midtoside_length= 2700000;
en_chA= envelope(chA, 120000, 'peak');
tag = 1;
min_peak_prominence= round(max(chA)*2/5);
while tag<5 % run max 10 times
[pk, ploc]= findpeaks(en_chA,'MinPeakDistance',1800000,...
    'MinPeakProminence',min_peak_prominence);
if length(pk)<6
    tag = tag+1;
    min_peak_prominence= min_peak_prominence*2/3;
    if min_peak_prominence < 10
        tag = 10;
    end
else
    tag = 10;
end
end
    
pk_distance= diff(ploc);
midtoside= find(pk_distance>midtoside_length); % find peaks that are more than 2700000 apart
mid_p= midtoside(diff(midtoside)==1) +1; %consecutive peaks that meet the requirement
if length(mid_p)>1
    mid_p= mid_p(1);
end
crop_chA= chA(ploc(mid_p)-period_length/2: ploc(mid_p)+period_length/2);
en_crop_chA= en_chA(ploc(mid_p)-period_length/2: ploc(mid_p)+period_length/2);

% find peaks inside the period

[pk, ploc]= findpeaks(en_crop_chA,'MinPeakDistance',2200000,...
    'MinPeakProminence',min_peak_prominence);

% Extract each lobe
sub_window= 1500000;
left_lobe= crop_chA(1:ploc(1)+(sub_window/2));
mid_lobe= crop_chA(ploc(2)-sub_window/2:ploc(2)+sub_window/2);
right_lobe= crop_chA(ploc(3)-(sub_window*1/2):end);

% Normalize and plot
norm_left= normalize(left_lobe, 'range', [-1 1]);
norm_mid= normalize(mid_lobe, 'range', [-1 1]);
norm_right= normalize(right_lobe, 'range', [-1 1]);
figure('name', filename)
set(gcf, 'Position',  [10, 10, 750, 600])
subplot 231
plot(norm_left); xlim([0 length(mid_lobe)]);
title('Left Lobe'); xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 232
plot(norm_mid); xlim([0 length(mid_lobe)]);
title('Mid Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 233
plot(norm_right); xlim([0 length(mid_lobe)]);
title('Right Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');

% plot the outline/envelope
[left_upper, left_lower]= envelope(norm_left,90000,'peak');
[mid_upper, mid_lower]= envelope(norm_mid,90000,'peak');
[right_upper, right_lower]= envelope(norm_right,90000,'peak');
subplot 234
plot(left_upper); xlim([0 length(mid_lobe)]);ylim([-1 1]);
hold on; plot(left_lower); 
title('Left Lobe'); xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 235
plot(mid_upper); xlim([0 length(mid_lobe)]);ylim([-1 1]);
hold on; plot(mid_lower);
title('Mid Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');
subplot 236
plot(right_upper); xlim([0 length(mid_lobe)]);ylim([-1 1]);
hold on; plot(right_lower);
title('Right Lobe');xlabel('Sample Number'); ylabel('Normalized Voltage');

savedir= 'C:\Users\F53992\Documents\Bosheng_AutomationCodes\GitCommit\AutoTest\AutoTestStepbyStep\DataAnalysis\LobeProfile\';

%save raw signal 
[filepath, name, ext]= fileparts(filename);
save_name= strcat(savedir, name, '_extract_lobes.mat');
save(save_name, 'left_lobe', 'mid_lobe', 'right_lobe');

% save figure
save_fig_name= strcat(savedir, name,'_extract_lobes.png');
saveas(gcf,save_fig_name)
end