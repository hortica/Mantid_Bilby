# 26 February 2016
# 4 April 2017
import math
import numpy as np
from mantid.api import *
import os, csv
from mantid.kernel import Logger

import BilbyCustomFunctions_Reduction

# Functions set
############################################
############################################

def ratio_calculation(n, ws1, ws2,  ws_samMsk, ws_tranMsk, scale):
    ratio_values = []

    ws1_scattering = CloneWorkspace(ws1)
    MaskDetectors(ws1_scattering, MaskedWorkspace=ws_samMsk) 
    ws1_transmission = CloneWorkspace(ws1)
    MaskDetectors(ws1_transmission, MaskedWorkspace=ws_tranMsk) 
    if ws2 != None:
        ws2_scattering = CloneWorkspace(ws2)
        MaskDetectors(ws2_scattering, MaskedWorkspace=ws_samMsk) 
        ws2_transmission = CloneWorkspace(ws2)
        MaskDetectors(ws2_transmission, MaskedWorkspace=ws_tranMsk) 

    for j in range(n):
        sum_scattering_ws1 = 0     
        sum_transmission_ws1 = 0     
        sum_scattering_ws2 = 0     
        sum_transmission_ws2 = 0             
        
        for i in range (40960, 61439):     #only rear detector      #for i in range (40960, ws_scattering.getNumberHistograms()):    
            sum_scattering_ws1  = sum_scattering_ws1 + ws1_scattering.readY(i)[j]
            sum_transmission_ws1  = sum_transmission_ws1 + ws1_transmission.readY(i)[j]
            if ws2 != None:
                sum_scattering_ws2  = sum_scattering_ws2 + ws2_scattering.readY(i)[j]
                sum_transmission_ws2  = sum_transmission_ws2 + ws2_transmission.readY(i)[j]
        #print 'sum_transmission_ws1, sum_transmission_ws2', sum_transmission_ws1, sum_transmission_ws2
        #print 'sum_scattering_ws1, sum_scattering_ws2', sum_scattering_ws1, sum_scattering_ws2
        if ws2 != None:
            sum_scattering = sum_scattering_ws1 - sum_scattering_ws2 * scale
            sum_transmission = sum_transmission_ws1 - sum_transmission_ws2 * scale
        else:           
            sum_scattering = sum_scattering_ws1 #* scale
            sum_transmission = sum_transmission_ws1 #* scale
        
        #print 'sum_transmission, sum_scattering', sum_transmission, sum_scattering
        ratio = sum_scattering / (sum_scattering+sum_transmission) 
        ratio *=100    # convert to %

        ratio_values.append(ratio)

    return ratio_values
    
############################################
############################################
# USER input files and parameters ===========================================

csv_file_name = FileFinder.getFullPath('input_csv_5789.csv')

index_files_to_reduce = '7,12,11'  # as per csv_files_to_reduce_list file

# wavelength settings
wav1 = 2.0                         # min wavelength in total range
wav2 = 18.0                       # max wavelength in total range
wav_delta = 1.0                 # wavelength step

#If subtract BlockedBeam
BlockedBeam_subtract = False # False

# END of USER input section ===============================================
############################################

if not os.path.exists(csv_file_name): 
    print ('Input csv list is not found')
    sys.exit()
    
csv_file_output = csv_file_name[0:(len(csv_file_name)-4)] + '_mult.csv' ## check how to name without extension + think about name! 

############################################
# Create output file, if does not exist

filename = csv_file_output            

if not os.path.exists(filename):     # check if it does exist; create if not
    file = open(filename, 'w')                     
    file.close()     
 
############################################
 # Calling function to read given csv file   

parameters = BilbyCustomFunctions_Reduction.FilesListReduce(csv_file_name)
files_to_reduce = BilbyCustomFunctions_Reduction.FilesToReduce(parameters, index_files_to_reduce)

############################################
# Check of input wavelength range

if  (wav1 + wav_delta) > wav2:
    print ('wav_delta is too large for the upper range of wavelength')
    sys.exit()

############################################
#calculate number of steps n =============================================

if  math.fmod((wav2 - wav1), wav_delta) == 0.0:  # if reminder is 0
   n = (wav2 - wav1)/wav_delta   
else:                                                                          # if reminder is greater than 0, to trancate the maximum wavelength in the range
   n = math.floor((wav2 - wav1)/wav_delta)
   max_wave_length = wav1 + n*wav_delta           
   print ('\n WARNING: because of your set-up, maximum wavelength to consider is only %4.2f \n' %max_wave_length)
   
n = int(n) # number of wavelength intervals
for current_file in files_to_reduce:                                   

    file_name = current_file['T_Sample']+'.tar'                          # transmission sample
    blocked_beam_name = current_file['T_BlockedBeam']+'.tar'  # blocked beam
    ws_tranMsk = current_file['mask_transmission_estimate_multiple']+'.xml'      # transmission mask
    ws_tranMsk_name = current_file['mask_transmission_estimate_multiple']+'.xml'
    ws_tranMsk = LoadMask('Bilby', ws_tranMsk)                     # loading tranmission mask
    ws_samMsk = InvertMask(InputWorkspace=ws_tranMsk)       # create scattering mask as an inverted one to transmission    
    suffix = current_file['suffix']                                                # suffix to record in output file
                                                              
# load files and convert units ===========================================
    
    ws_input_sample_transm = LoadBBY(file_name)
    ws_wave_sample_transm=ConvertUnits(ws_input_sample_transm, 'Wavelength')

    ws_input_blocked = LoadBBY(blocked_beam_name)
    ws_wave_blocked=ConvertUnits(ws_input_blocked, 'Wavelength')

# rebin of initial workspace  ===========================================

    wave_range=str(wav1)+','+str(wav_delta)+','+str(wav2)

    ws_wave_sample_transm = Rebin(ws_wave_sample_transm, Params = wave_range, PreserveEvents = False)  # interesting how Rebin works if the reminder from the division is greater than 0 ???
    ws_wave_blocked = Rebin(ws_wave_blocked, Params = wave_range, PreserveEvents = False)

############################################
    
    ws1 = ws_wave_sample_transm
    if BlockedBeam_subtract:
        ws2 = ws_wave_blocked
    else:
        ws2 = None

    # separating cases when BlockedBeam is in use from the case where only unsubtracted file is analysed    
    if ws2 == None:
        print (suffix, 'sample transmission', file_name, 'without blocked beam subtraction is analysed')
        # array of input names        
        analysed_data = [(suffix, file_name, 'no_blocked_beam_subtracted', ws_tranMsk_name)]
        # no need to scale
        scale_transm_blocked = 1.0
    else:
        # length of measurements - scaling
        scale_transm_blocked = float(ws_wave_sample_transm.run().getProperty('frame_count').value) / float(ws_wave_blocked.run().getProperty('frame_count').value)
        # array of input names
        analysed_data = [(suffix, file_name, blocked_beam_name, ws_tranMsk_name)]        
    
    # record list of files into out file    
    with open(filename, 'a') as f_out:
        wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
        wr.writerow(analysed_data)    # will write everything in one row

############################################
# Main part: calculations

    ratio_values_sample_minus_blocked = ratio_calculation(n, ws1, ws2, ws_samMsk, ws_tranMsk, scale_transm_blocked) # calculate array of values

    for j in range (n): # n is a number of wavelength intervals
        if (ratio_values_sample_minus_blocked[j] >= 10.0):
            note = 'Careful, > 10%'
        elif (ratio_values_sample_minus_blocked[j] <= 0.0):
            note = 'Not distinguishable from background'
        elif ((ratio_values_sample_minus_blocked[j]  > 0) &  (ratio_values_sample_minus_blocked[j] < 10.0)):
            note = 'OK'

        analysed_data_wav = [ws1.readX(0)[j], ws1.readX(0)[j+1], '%4.3f' % ratio_values_sample_minus_blocked[j], note]
        print (analysed_data_wav)
        with open(filename, 'ab') as f_out:
            wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
            wr.writerow(analysed_data_wav)
LoadDialog()