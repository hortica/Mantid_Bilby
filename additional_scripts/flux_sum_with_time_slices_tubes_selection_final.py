# March 2023 - rear detector only
# March 2025 - typo in detectors' pixels corrected; cycle over time intervals added
# Added options for masking and recording counts on each tube
# May 2025 - added wavelength range into output file
# May 2025 - added User' input checklist
# Need to add blocked beam subtraction
# Need to bring open_csv outside

from mantid.simpleapi import *
import numpy as np
from mantid.api import *
import os, csv, math
import BilbyCustomFunctions_Reduction

#################################################################################################
#################################################################################################
# main function used in the script below

def count(ws1, measured_time, tubes_range): # calculate array of values
    count_value_tube_whole_array = []

    if ((tubes_range[0] < 1) or (tubes_range[1] > 240) or (tubes_range[1] < tubes_range[0])):
        raise ValueError('Check tubes_range, shall be from 1 to 240 inclusive, second value larger or equal to the first.')
      
    for tube_number in range (tubes_range[0], tubes_range[1]+1):
        # build array of pixels considering weird sequence of pixel numbers
        # Left: 1, 40; Right: 41, 80; Top: 81, 120; Bottom: 121, 160; Rear: 161, 240.
        # left curtain 0 - 10239
        # right curtain 10240 - 20479
        # top curtain 20480 - 30719
        # bottom curtain 30720 - 40959
        pixel1 = (256 * (tube_number - 1)) 
        pixel2 = (256 * tube_number - 1)
        #print ("tube_number, pixel1, pixel2 ", tube_number, pixel1, pixel2)

        # sum counting
        sum_counts_ws1 = 0.0
        for i in range (pixel1, pixel2):
            sum_counts_ws1  = sum_counts_ws1 + ws1.readY(i)
            final_sum = sum_counts_ws1
            final_sum_rate = final_sum / measured_time

        count_value_tube = (tube_number, final_sum[0], final_sum_rate[0])
        #print ('count_value_tube ', count_value_tube)
        count_value_tube_whole_array.append (count_value_tube)
        
    return count_value_tube_whole_array
    
#################################################################################################
#################################################################################################

#################################################################################################
# USER input files and parameters =========================================
# =========================================================================
# User' input checklist:
# == Name of input file
# == Write the name of the column the data will be read in
# == Say if mask to be applied
# == Choose range of indexes of lines with files to analyse
# == Select wavelength range
# == Select number of time-steps
# == Select tubes range
# == Define the full output filename
# == Say if you want counts per each tube to be recorded into the output file

# Name of the input list with file names and masks
csv_files_to_reduce_list = FileFinder.getFullPath('input_17941.csv')

# column name with data files to be processed
column_name = 'Sample'                     

# If files to be masked
apply_mask = False
if (apply_mask): mask_column_name = 'mask' # column name to take the mask from

# Index of the lines in the input csv files to be processed
index_files_to_analyse = '11'         

# Wavelength range to use for all files in the list - use any wide range for NVS
wav1 = 2.0                                 # min wavelength in total range
wav2 = 18.0                                # max wavelength in total range

# Number of time intervals, applicable for all files in the list
number_time_steps = 1 # 300 sec for 7200

if (type(number_time_steps)) != int: 
    raise ValueError('number of intervals must be integer')  
    
# Input: number of tubes.
# Left: 1, 40; Right: 41, 80; Top: 81, 120; Bottom: 121, 160; Rear: 161, 240.
# in principle, any interval can be taken, but only one
tubes_range = [201, 240]

# Output file name - adding a bit to the input file (ASCII: csv, txt, dat)
# !!! The file will be created in the same folder as the input one
csv_file_output = os.path.dirname(csv_files_to_reduce_list) + '/tubes_counts_test.csv'
#csv_file_output = csv_files_to_reduce_list[0:(len(csv_files_to_reduce_list) - 4)] + '_time_slices_NVS_transm_BBY0078329_small_bins.csv' ## check how to name without extension + think about name! 
#print(csv_file_output)
# If record counts per tube - makes more sense for a single time interval
record_each_tube_counts = False

# END of USER input section ===============================================
# =========================================================================
#################################################################################################
#################################################################################################

# Check if output file does exist; create if not 
if not os.path.exists(csv_file_output):
    file = open(csv_file_output, 'w+')                     
    file.close()    

# Retrieve list of the file names from the list
parameters = BilbyCustomFunctions_Reduction.files_list_reduce(csv_files_to_reduce_list)
files_to_analyse = BilbyCustomFunctions_Reduction.files_to_reduce(parameters, index_files_to_analyse)

# Set-up wavelength range
wav_delta = wav2 - wav1
if  (wav1 + wav_delta) > wav2:
    raise ValueError('wav_delta is too large for the upper range of wavelength')    

# Start main cycle for each file in the list
for current_file in files_to_analyse:                                   
    file_name = current_file[column_name] + '.tar'
    if (apply_mask):
        ws_tranMsk = current_file[mask_column_name] + '.xml' 
        ws_tranMsk = LoadMask('Bilby', ws_tranMsk)
    
# Load file ====================================================================================

    StartTime = 0.0
    EndTime = 0.0
    ws_input_file = LoadBBY(file_name)

    Real_EndTime_max = float(ws_input_file.run().getProperty('bm_counts').value)
    print('Real_EndTime_max ', Real_EndTime_max)
    interval_length = (Real_EndTime_max/number_time_steps) # no need to round, can be anything
    print ("how long is one interval ", interval_length)
 
    for i in range (number_time_steps):
        StartTime = interval_length * i 
        EndTime = StartTime + interval_length
        # print ('StartTime, EndTime ', StartTime, EndTime)
        ws_input_file = LoadBBY(file_name, FilterByTimeStart = StartTime, FilterByTimeStop = EndTime)
        if (apply_mask):
            MaskDetectors(ws_input_file, MaskedWorkspace = ws_tranMsk)     
        
        ws_input_file = ConvertUnits(ws_input_file, 'Wavelength')
        wave_range = str(wav1) + ',' + str(wav_delta) + ',' + str(wav2)
        ws_input_file = Rebin(ws_input_file, Params = wave_range, PreserveEvents = False)  # interesting how Rebin works if the reminder from the division is greater than 0 ???
        ws1 = ws_input_file
        #measured_time = float(ws_input_file.run().getProperty('bm_counts').value)
        measured_time = interval_length # now the interval is firmly defined        
   
# Main part: calculations =========================================================================

        count_value_tube_whole_array = count(ws1, measured_time, tubes_range)
  
        # Calculate total number of events on all tubes in the given range
        total_count_all_tubes = 0.0
        for single_tube in count_value_tube_whole_array:
            total_count_all_tubes += single_tube[1]
        header_1 = [file_name, 'tubes_range', tubes_range[0], tubes_range[1], 'measured_time', measured_time, 'wavelength range', (wav1, wav2), 'total_count_all_tubes', total_count_all_tubes, 'StartTime', StartTime, 'EndTime', EndTime]
        #print ('header_1 ', header_1)  
        with open(csv_file_output, 'a') as f_out:
            wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
            wr.writerow(header_1)

        # An option to record counts per each tube
        if (record_each_tube_counts):
            with open(csv_file_output, 'a') as f_out:
                wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
                for tube_c in count_value_tube_whole_array:
                    wr.writerow(tube_c)
        
    f_out.close()        