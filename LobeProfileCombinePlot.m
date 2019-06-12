%% Plot all images on 1 figure in respect to position on US screen
% Ultrasound machine: Axis 1= horizontal, Axis 0 = verticle (depth)

%posNum=[1,47,93,139,185,369,415,461,507,553,737,783,829,875,921,1105,1151,1197,1243,1289,1473, 1519,1565,1611,1657,1841,1887,1933,1979,2025];
% posNum=[1 47 93	139	185 369	415	461	507	553 737	783	829	875	921 ...
% 1105	1151	1197	1243	1289 1473	1519	1565	1611	1657 ...
% 1841	1887	1933	1979	2025];
posNum= [1,6,11,16,21,369,374,379,384,389,737,742,747,752,757,1105,1110,1115,1120,1125,1473,1478,1483,1493,1841,1846,1851,1856,1861];
needleID= 'PGE2A1234';
US_machine= 'Toshiba';
needleLength= '1.2mm';
 %% Load, crop images, and assign new name (might not need)
% 
rootdir='C:\Users\F53992\Documents\Bosheng_AutomationCodes\GitCommit\AutoTest\AutoTestStepbyStep\DataAnalysis\AnalysisData\';
figure;
for pos= posNum
    try
        filename= strcat(rootdir,'Pos_', string(pos), '_', string(US_machine),'_', string(needleID), '_extract_lobes.png');
        I= imread(filename);
        I2 = I(1:938/2+10, 1:1172, :);
        imshow(I2);
        savename= strcat(rootdir,'Pos_', string(pos), '_', string(US_machine),'_', string(needleID), '_extract_lobes2.png');
        saveas(gcf, savename)
    catch
        continue
    end
end

%% Create plot

figure;
set(gcf, 'Position',  [10, 10, 800, 650]);
set(gcf, 'color', 'w');
axis2=[0.02,5,10,15,20];
loc=0.02;
depth=0;
plotNum=1;
i=1;
% create a 6 by 5 figure
for pos= posNum
    filename= strcat(rootdir,'Pos_', string(pos), '_', string(US_machine),'_', string(needleID), '_extract_lobes2.png');
    loc= axis2(i);
    i=i+1;
    if mod(plotNum-1,5)==0
        depth= depth+1;
        i=1;
    end
    titlestr= strcat(  string(depth),"cm Depth, ", string(loc), 'mm Loc');
    try
        I= imread(filename);
        hAxis(plotNum)= subplot(6,5,plotNum);
        imshow(I);
        title(titlestr);
        plotNum=plotNum+1;
    catch
        disp(pos)
        plotNum=plotNum+1;
    end
end

% reset plot size
for i=linspace(1,length(posNum), length(posNum))
    try
        position= get(hAxis(i), 'Position'); 
        position(1)= position(1)-0.05; %shift left
 %       position(2)= position(2)+0.02; %shift up
        position(3)= position(3)*1.6; %larger width
        position(4)= position(4)*1.5; %larger height
        set( hAxis(i), 'Position', position);
    catch
        disp(i)
        continue
    end
end

savedir= 'C:\Users\F53992\Documents\Bosheng_AutomationCodes\GitCommit\AutoTest\AutoTestStepbyStep\DataAnalysis\LobeProfile\';
savefig= strcat(savedir, US_machine,'_LobeProfile_',needleLength,'Axis0Axis2.fig');
savepng= strcat(savedir, US_machine,'_LobeProfile_',needleLength,'Axis0Axis2.png');
saveas(gcf, savepng);
saveas(gcf, savefig);
    