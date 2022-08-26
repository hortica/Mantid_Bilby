# import mantid algorithms
from mantid.simpleapi import *
from mantid.api import *

import numpy as np
import os, csv

# standard Bilby reduction functions
import BilbyCustomFunctions_Reduction

# ==========================================================================================
# ==========================================================================================
# This script is extracting wavelength distribution from the list of Bilby data files.
# The script is useful when analysing spectra at different instrument configurations.
# ==========================================================================================
# This script reads .csv file which must contain at least three columns, 'index', 'T_Sample' and 'mask_transmission'.
# Only these two columns matter, all the rest will be ignored.
# The script needs several inputs:
# The csv file name; number of lines to be processed; wavelength range and the interval.
# Output files will be stored in the same folder as the original .csv file, named "Bilby_data_file" + "spectrum.dat"
# NOTE: The output spectra are normalised to the measurement time and after, to the Y-maximum value, so all max is equal to 1.
# Made so for easier comparison.
# ==========================================================================================
# ==========================================================================================

# Start USER input files and parameters ===========================================
csv_files_to_analyse_list = FileFinder.getFullPath('control_flux_files_restarted_8July2020.csv')

index_files_to_analyse = '272-276'  # as per csv_files_to_analyse_list file

parameters = BilbyCustomFunctions_Reduction.files_list_reduce(csv_files_to_analyse_list)
files_to_analyse = BilbyCustomFunctions_Reduction.files_to_reduce(parameters, index_files_to_analyse)

wav1 = 2.0                          # min wavelength in total range
wav2 = 18.0                         # max wavelength in total range
wav_delta = (wav2 - wav1)/100       # wavelength step

# End USER input files and parameters ===========================================

Params = [wav1, wav_delta, wav2]

for current_file in files_to_analyse:

    file_name = current_file['T_Sample']+'.tar'  # get file name
    ws_sam = LoadBBY(file_name) # load file
       
    running_time = float(ws_sam.run().getProperty('bm_counts').value) # length of the measurement, for scaling
    base_output_name = file_name[0:10] + '_' + 'spectrum' + '.dat' # constract output name

    ws_tranMsk = current_file['mask_transmission']+'.xml' # get mask name
    ws_tranMsk = LoadMask('Bilby', ws_tranMsk)  # load mask         
    MaskDetectors(ws_sam, MaskedWorkspace=ws_tranMsk) # apply mask

    ws_sam = ConvertUnits(ws_sam, 'Wavelength') # convert to lambda
    ws_sam = Rebin(ws_sam, Params, PreserveEvents=False) # rebin as per input values
    ws_sam_spectrum = SumSpectra(ws_sam) # sum to 1D spectra
    ws_sam_spectrum = Scale(ws_sam_spectrum, 1/running_time, 'Multiply') # normalise to the measurement time
    #ws_sam_spectrum = Scale(ws_sam_spectrum, 1/np.max(ws_sam_spectrum.readY(0)), 'Multiply') # normalise to max Y
    print ('np.max(ws_sam_spectrum.readY(0)) ', np.max(ws_sam_spectrum.readY(0)))
    ws_sam_spectrum = Scale(ws_sam_spectrum, 1/np.max(ws_sam_spectrum.readY(0)), 'Multiply', OutputWorkspace = base_output_name) # normalise to max Y and create ws in Mantid
  
    reduced_files_path_folder = os.path.dirname(csv_files_to_analyse_list) # create path for the output data file
    savefile = os.path.join(os.path.expanduser(reduced_files_path_folder), base_output_name) # setting up full path, including file name
    SaveAscii(InputWorkspace = ws_sam_spectrum, Filename = savefile, WriteXError = False, WriteSpectrumID = False, Separator = 'CSV', AppendToFile = False) #saving file
    print (savefile)
    #print ('1D File Exists: ', os.path.exists(savefile))
    
    
    
    