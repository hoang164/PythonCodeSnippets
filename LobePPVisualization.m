US_MACHINES= ["eZono", "eZono","GE", "GE","Toshiba", "Toshiba"];
NEEDLE_ID= ["PGE2A1234", "PGe2A616", "PGE2A1234", "PGe2A616","PGE2A1234", "PGe2A616"] ;
DATA_LENGTHS= ["300ms", "300ms","400ms", "400ms","200ms", "200ms"] ;
axis1= [0,2,4,6,8];
posNum= [1,47,93,139,185;
        369,415,461,507,553;
        737,783,829,875,921;
        1105,1151,1197,1243,1289;
        1473,1519,1565,1611,1657;
        1841,1887,1933,1979,2025]; 
% mid lobe depths of all US machines in the order according to US_MACHINES
USmachines_depth10 = NaN(6, 5);
USmachines_depth20 = NaN(6, 5);
USmachines_depth30 = NaN(6, 5);
USmachines_depth40 = NaN(6, 5);
USmachines_depth50 = NaN(6, 5);
USmachines_depth60 = NaN(6, 5);

%%    
for i= 1:length(US_MACHINES)
    US_machine= US_MACHINES(i);
    needleID= NEEDLE_ID(i);
    dataLength= DATA_LENGTHS(i);
    fileroot= strcat('Y:\Beacon_Datalibrary\RX_3D_WaterTank\3D_', string(US_machine),'_', string(needleID), '_', string(dataLength),'\');
    disp(fileroot)
    [right_pp, mid_pp, left_pp]= runIt(fileroot, US_machine, needleID, axis1, posNum);
    USmachines_depth10_midlobe(i, :) = mid_pp(1, :);
    USmachines_depth20_midlobe(i, :) = mid_pp(2, :);
    USmachines_depth30_midlobe(i, :) = mid_pp(3, :);
    USmachines_depth40_midlobe(i, :) = mid_pp(4, :);
    USmachines_depth50_midlobe(i, :) = mid_pp(5, :);
    USmachines_depth60_midlobe(i, :) = mid_pp(6, :);
    
    USmachines_depth10_leftlobe(i, :) = left_pp(1, :);
    USmachines_depth20_leftlobe(i, :) = left_pp(2, :);
    USmachines_depth30_leftlobe(i, :) = left_pp(3, :);
    USmachines_depth40_leftlobe(i, :) = left_pp(4, :);
    USmachines_depth50_leftlobe(i, :) = left_pp(5, :);
    USmachines_depth60_leftlobe(i, :) = left_pp(6, :);
    
    USmachines_depth10_rightlobe(i, :) = right_pp(1, :);
    USmachines_depth20_rightlobe(i, :) = right_pp(2, :);
    USmachines_depth30_rightlobe(i, :) = right_pp(3, :);
    USmachines_depth40_rightlobe(i, :) = right_pp(4, :);
    USmachines_depth50_rightlobe(i, :) = right_pp(5, :);
    USmachines_depth60_rightlobe(i, :) = right_pp(6, :);
       
end


%%
function [right_pp, mid_pp, left_pp]= runIt(fileroot, US_machine, needleID, axis1, posNum)
% caculate pp data
mid_pp= NaN(size(posNum));
right_pp= NaN(size(posNum));
left_pp= NaN(size(posNum));
for col = 1:size(posNum, 2)
    for row= 1:size(posNum,1)
        try
            pos= posNum(row, col);
            filename= strcat(fileroot,'Pos_', string(pos), '_', string(US_machine),'_', string(needleID), '_extract_lobes.mat');
            load(filename);
            right_pp(row, col)= max(right_lobe)- min(right_lobe);
            mid_pp(row, col)= max(mid_lobe)- min(mid_lobe);
            left_pp(row, col)= max(left_lobe)- min(left_lobe);
        catch
            disp(posNum(row,col));
            continue
        end
    end
end
mid_pp= [2558 2840 2520 1387 840 600;
1281 1499 2443 1375 907 705;
477 666 570 756 700 600;
135 147 536 290 236 191;
NaN 170 226 169 176 172;
NaN 100 138 169 102 118];

%% plotting - trend of lobe pp changes with depth
figure('name',fileroot);
set(gcf, 'Position',  [10, 10, 900, 900]);
subplot(3,1,1)
bar(mid_pp, 'group');
ylim([0, 4000]);
legend('Axis 1= 0mm', 'Axis 1= 2mm', 'Axis 1= 4mm', 'Axis 1= 6mm', 'Axis 1= 8mm');
title('Middle Lobe');
xlabel('Axis 0 - Depth (cm)'); ylabel('PP voltage (mV)');

subplot(3,1,2)
bar(left_pp, 'group');
ylim([0, 4000]);
legend('Axis 1= 0mm', 'Axis 1= 2mm', 'Axis 1= 4mm', 'Axis 1= 6mm', 'Axis 1= 8mm');
title('Left Lobe');
xlabel('Axis 0 - Depth (cm)'); ylabel('PP voltage (mV)');

subplot(3,1,3)
bar(right_pp, 'group');
ylim([0, 4000]);
legend('Axis 1= 0mm', 'Axis 1= 2mm', 'Axis 1= 4mm', 'Axis 1= 6mm', 'Axis 1= 8mm');
title('Right Lobe');
xlabel('Axis 0 - Depth (cm)'); ylabel('PP voltage (mV)');

% % save
% savepng= strcat(fileroot, '_LobePP_vs_Depth.png');
% savefig= strcat(fileroot, '_LobePP_vs_Depth.fig');
% saveas(gcf, savepng);
% saveas(gcf, savefig);
% 

%% plotting trend to compare pp of lobes for different axis 1
% figure('name',fileroot);set(gcf, 'Position',  [10, 10, 900, 900]);
% depth_10= [left_pp(1,:); mid_pp(1,:); right_pp(1,:)];
% depth_20= [left_pp(2,:); mid_pp(2,:); right_pp(2,:)];
% depth_30= [left_pp(3,:); mid_pp(3,:); right_pp(3,:)];
% depth_40= [left_pp(4,:); mid_pp(4,:); right_pp(4,:)];
% depth_50= [left_pp(5,:); mid_pp(5,:); right_pp(5,:)];
% depth_60= [left_pp(6,:); mid_pp(6,:); right_pp(6,:)];
% subplot(321)
% plot(axis1, depth_10,'LineWidth',2); 
% xlim([0 8]); ylim([0 4000]);title('Depth = 10cm');ylabel('PP (mV)'); xlabel('Axis 1 (mm)');
% legend('Left Lobe', 'Mid Lobe', 'Right Lobe');
% subplot(323)
% plot(axis1, depth_20,'LineWidth',2); 
% xlim([0 8]); ylim([0 4000]);title('Depth = 20cm');ylabel('PP (mV)'); xlabel('Axis 1 (mm)');
% legend('Left Lobe', 'Mid Lobe', 'Right Lobe');
% subplot(325)
% plot(axis1, depth_30,'LineWidth',2); 
% xlim([0 8]); ylim([0 4000]);title('Depth = 30cm');ylabel('PP (mV)'); xlabel('Axis 1 (mm)');
% legend('Left Lobe', 'Mid Lobe', 'Right Lobe');
% subplot(322)
% plot(axis1, depth_40,'LineWidth',2); 
% xlim([0 8]); ylim([0 4000]);title('Depth = 40cm');ylabel('PP (mV)'); xlabel('Axis 1 (mm)');
% legend('Left Lobe', 'Mid Lobe', 'Right Lobe');
% subplot(324)
% plot(axis1, depth_50,'LineWidth',2); 
% xlim([0 8]); ylim([0 4000]);title('Depth = 50cm');ylabel('PP (mV)'); xlabel('Axis 1 (mm)');
% legend('Left Lobe', 'Mid Lobe', 'Right Lobe');
% subplot(326)
% plot(axis1, depth_60,'LineWidth',2); 
% xlim([0 8]); ylim([0 4000]);title('Depth = 60cm');ylabel('PP (mV)'); xlabel('Axis 1 (mm)');
% legend('Left Lobe', 'Mid Lobe', 'Right Lobe');
% savepng= strcat(fileroot, '_LobePP_vs_Axis1.png');
% savefig= strcat(fileroot, '_LobePP_vs_Axis1.fig');
% saveas(gcf, savepng);
% saveas(gcf, savefig);

end