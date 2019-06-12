%% Date 6/3/2019 - Author: Thuy Hoang
% data visualizaiton for peak to peaks of 3D data collected in the water
% tank with different ultrasound machines
%
%% import data from LobePeakData.xlsx
% each sheet contain p-p information of 1 US machine

eZono = readtable('LobePeakData.xlsx', 'Sheet', 'eZono');
GE = readtable('LobePeakData.xlsx', 'Sheet','GE');
Toshiba = readtable('LobePeakData.xlsx', 'Sheet','Toshiba');
SonoSite = readtable('LobePeakData.xlsx', 'Sheet','SonoSite');

% separate data acoording to needle length
rows_600 = eZono.Needle == 600;
rows_1200 = eZono.Needle == 1200;
eZono_600 = eZono(rows_600,:);
eZono_1200 = eZono(rows_1200,:);
GE_600 = GE(rows_600,:);
GE_1200 = GE(rows_1200,:);
Toshiba_600 = Toshiba(rows_600,:);
Toshiba_1200 = Toshiba(rows_1200,:);
SonoSite_600 = SonoSite(rows_600,:);
SonoSite_1200 = SonoSite(rows_1200,:);

%% plotting Lobes comparison
US_machine= 'eZono 1200um';
data= eZono_1200; %this should match with US_machine
figure('name', US_machine);
i= 1;
a1= [0,1,2,4,6,8];
while i<=length(a1)
    axis1= a1(i);
    midlobe= data{data.Axis1 == axis1, {'MidLobe'}};
    leftlobe= data{data.Axis1 == axis1, {'LeftLobe'}};
    rightlobe= data{data.Axis1 == axis1, {'RightLobe'}};
    subplot(6,1,i)
    plot(midlobe); hold on
    plot(leftlobe); hold on
    plot(rightlobe); hold on
    legend('mid lobe','left lobe', 'right lobe');
    xlabel('Depth (cm'); ylabel('PP voltage (mV)');
    titlestr = strcat('Axis 1= ', string(axis1));
    title(titlestr);
    i=i+1;
end

%% plotting 1.2mm vs 0.6mm comparison at each depth
US_machine= 'eZono 600 vs 1200 PZT';
data1= eZono_600; %this should match with US_machine
data2= eZono_1200;
figure('name', US_machine);set(gcf, 'Position',  [10, 10, 600, 1000]);
i= 1;
a1= [0,1,2,4,6,8];
a0=[10,20,30,40,50,60];
while i<=length(a1)
    axis0= a0(i);
    mid_600= data1{data1.Axis0 == axis0, {'MidLobe'}};
    mid_1200= data2{data2.Axis0 == axis0, {'MidLobe'}}; 
    subplot(6,1,i)
    plot(a1,mid_600); hold on
    plot(a1, mid_1200); hold on
    legend('600um PZT', '1200um PZT');
    xlabel('Axis 1 (mm)'); ylabel('PP voltage (mV)');
    titlestr = strcat('Axis 0= ', string(axis0), 'mm');
    title(titlestr);
    i=i+1;
end

save_dir= 'C:\Users\F53992\Documents\Bosheng_AutomationCodes\GitCommit\AutoTest\AutoTestStepbyStep\DataAnalysis\LobePeaks\';
save_fig= strcat(save_dir, US_machine,'.fig');
save_png= strcat(save_dir, US_machine,'.png');
saveas(gcf, save_fig);
saveas(gcf, save_png);

%% plotting axis 2? 