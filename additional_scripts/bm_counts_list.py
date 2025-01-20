# March 2023 - rear detector only

from mantid.simpleapi import *
import numpy as np
from mantid.api import *
import os, csv
import BilbyCustomFunctions_Reduction



# USER input files and parameters ===========================================
# =========================================================================

csv_files_to_reduce_list = FileFinder.getFullPath('input_19162.csv')


column_name = 'T_Sample' # column name with data files
index_files_to_analyse = '200-372'  # as per csv_files_to_reduce_list file '21-39, 41-

# Outful file name - add extension to the input file (ASCII: csv, txt, dat)
# !!! The file will be created in the same folder as the input one
csv_file_output = csv_files_to_reduce_list[0:(len(csv_files_to_reduce_list) - 4)] + '_real_time_6_7Dec.csv' ## check how to name without extension + think about name! 

# END of USER input section ===============================================
# =========================================================================

# Check if output file does exist; create if not 
if not os.path.exists(csv_file_output):
    file = open(csv_file_output, 'w+')                     
    file.close()    

header = ['file_name', 'period', 'number_of_frames', 'measurement_time', 'detector_time']
with open(csv_file_output, 'a') as f_out:
    wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
    wr.writerow(header)

# Retrieve list of the file names from the list
parameters = BilbyCustomFunctions_Reduction.files_list_reduce(csv_files_to_reduce_list)
files_to_analyse = BilbyCustomFunctions_Reduction.files_to_reduce(parameters, index_files_to_analyse)

# Start main cycle for each file in the list
for current_file in files_to_analyse:                          

    file_name = current_file[column_name] + '.tar'
    ws_input_file = LoadBBY(file_name)
    measured_time = float(ws_input_file.run().getProperty('bm_counts').value)
    period = float(ws_input_file.run().getProperty('period').value)
    number_frames = float(ws_input_file.run().getProperty('frame_count').value)    
    detector_time = float(ws_input_file.run().getProperty('detector_time').value)        
    #print('measured_time ', measured_time)


    with open(csv_file_output, 'a') as f_out:
        wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
        time_data = [file_name, period, number_frames, measured_time, detector_time]
        wr.writerow(time_data)
        
#analysed_data_wav = [file_name, '%14.3f' % count_on_tubes, '%14.3f' % count_on_tubes_rate]
        
       
        