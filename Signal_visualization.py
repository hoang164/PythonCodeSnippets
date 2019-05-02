import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import time

start = time.time()
data_dir = "Z:\Data_Library\LIBRARY_001"  ## input directory of interest
fig_count = 0
mat_count = 0
non_plot_dir = []
join_path = os.path.join
load_mat = sio.loadmat
for root, dir, files in os.walk(data_dir):
    for file in files:
        if '.mat' in file:  # look for .mat file
            title = file.split('.m')[0]
            if '{}.png'.format(title) in files: continue  # skip if there is already a png image
            mat_count = mat_count + 1
            file_dir = join_path(root, file)
            try:
                file_contents = load_mat(file_dir, variable_names=('chA', 'timeMs', 'positioninfo'),
                                         squeeze_me=True, struct_as_record=False)
            except:
                non_plot_dir = non_plot_dir + [root]
                continue
            dataLen = len(file_contents['chA'])
            time_ms = file_contents['timeMs']
            Axis0 = file_contents['positioninfo'].coordinate[0]
            Axis1 = file_contents['positioninfo'].coordinate[1]
            Axis2 = file_contents['positioninfo'].coordinate[2]
            img_title = "".join(
                ["SonoSite ", "Axis0: ", str(Axis0), "mm;Axis1: ", str(Axis1), "mm;Axis2: ", str(Axis2), "mm"])
            # make/save plots:
            fig = plt.figure()
            plt.plot(time_ms, file_contents['chA'])
            plt.ylabel('Voltage (mV)')
            plt.xlabel('Time (ms)')
            plt.title(img_title)
            plt.savefig('{}/{}.png'.format(root, title))
            plt.close()
            fig_count = fig_count + 1

end = time.time()
print('Number of figures generated: ', fig_count)
print('Number of Matlab figures found: ', mat_count)
print('Number of seconds elapsed: ', end - start)