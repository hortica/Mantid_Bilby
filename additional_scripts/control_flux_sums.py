#6 April 2018

import numpy as np
from mantid.api import *
import os, csv
import BilbyCustomFunctions_Reduction

############################################

def count(ws1, ws2, ws_tranMsk, scale_transm_blocked): # calculate array of values
    count = []
    MaskDetectors(ws1, MaskedWorkspace=ws_tranMsk) 
    if ws2 != None:
        MaskDetectors(ws2, MaskedWorkspace=ws_tranMsk) 

    sum_transmission_ws1 = 0.0
    sum_transmission_ws2 = 0.0 
    final_sum = []
        
    for i in range (40960, 61439):     #only rear detector      #for i in range (40960, ws_scattering.getNumberHistograms()):    #can be replaced by SumSpectra
        sum_transmission_ws1  = sum_transmission_ws1 + ws1.readY(i)
        final_sum = sum_transmission_ws1
        if ws2 != None:
            sum_transmission_ws2  = sum_transmission_ws2 + ws2.readY(i)
            final_sum = sum_transmission_ws1 - sum_transmission_ws2 * scale_transm_blocked            

    count_value = final_sum         
    return count_value
    
# USER input files and parameters ===========================================

csv_files_to_reduce_list = FileFinder.getFullPath('control_flux_files.csv')

index_files_to_reduce = '97-102'  # as per csv_files_to_reduce_list file '21-39, 41-

wav1 = 2.0                          # min wavelength in total range
wav2 = 18.0                        # max wavelength in total range
wav_delta = wav2 - wav1    # wavelength step

#If subtract BlockedBeam
BlockedBeam_subtract = False

# END of USER input section ===============================================

csv_file_output = csv_files_to_reduce_list[0:(len(csv_files_to_reduce_list)-4)] + '_0counts.csv' ## check how to name without extension + think about name! 
if not os.path.exists(csv_file_output):     # check if it does exist; create if not
    file = open(csv_file_output, 'w+')                     
    file.close()     
   
parameters = BilbyCustomFunctions_Reduction.FilesListReduce(csv_files_to_reduce_list)
files_to_reduce = BilbyCustomFunctions_Reduction.FilesToReduce(parameters, index_files_to_reduce)

if  (wav1 + wav_delta) > wav2:
    raise ValueError('wav_delta is too large for the upper range of wavelength')    

for current_file in files_to_reduce:                                   
    file_name = current_file['T_Sample']+'.tar'                        
    ws_tranMsk = current_file['mask_transmission']+'.xml'
    ws_tranMsk = LoadMask('Bilby', ws_tranMsk)                     
                                                              
# load files ===================================================================================
   
    ws_input_sample_transm = LoadBBY(file_name)
    ws_wave_sample_transm=ConvertUnits(ws_input_sample_transm, 'Wavelength')
    wave_range=str(wav1) + ',' + str(wav_delta) + ',' + str(wav2)
    ws_wave_sample_transm = Rebin(ws_wave_sample_transm, Params = wave_range, PreserveEvents = False)  # interesting how Rebin works if the reminder from the division is greater than 0 ???

    ws1 = ws_wave_sample_transm
    if BlockedBeam_subtract:
        blocked_beam_name = current_file['BlockedBeamTransmission']+'.tar'         
        ws_input_blocked = LoadBBY(blocked_beam_name)
        ws_wave_blocked=ConvertUnits(ws_input_blocked, 'Wavelength')
        ws_wave_blocked = Rebin(ws_wave_blocked, Params = wave_range, PreserveEvents = False)        
        ws2 = ws_wave_blocked        
    else:
        ws2 = None

# separating cases when BlockedBeam is in use from the case where only unsubtracted file is analysed    ===
    
    if ws2 == None:
        print ('sample transmission'), file_name, ('without blocked beam subtraction is analysed')
        scale_transm_blocked = 1.0
    else:
        scale_transm_blocked = float(ws_wave_sample_transm.run().getProperty('frame_count').value) / float(ws_wave_blocked.run().getProperty('frame_count').value)
    
# Main part: calculations =========================================================================

    transmission_count = count(ws1, ws2, ws_tranMsk, scale_transm_blocked)
    transmission_countrate = transmission_count/float(ws_wave_sample_transm.run().getProperty('bm_counts').value)
    att_pos = float(ws_wave_sample_transm.run().getProperty('att_pos').value)
    data_before_May_2016 = False # Attenuators changed
    scale = BilbyCustomFunctions_Reduction.AttenuationCorrection(att_pos, data_before_May_2016)
    analysed_data_wav = [file_name, '%14.3f' % transmission_count, '%14.3f' % transmission_countrate, '%6.5f' % scale]
    #print analysed_data_wav
    with open(csv_file_output, 'ab') as f_out:
        wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
        wr.writerow(analysed_data_wav)
