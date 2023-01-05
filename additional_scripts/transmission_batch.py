# import mantid algorithms
from mantid.simpleapi import *

import numpy as np
import mantid.simpleapi
from mantid.api import *
import BilbyCustomFunctions_Reduction

#============================================================================================================================================#
# USER input start

folder_name = "transmission_fits"

transmission_list = FileFinder.getFullPath('input_csv_example.csv') # main list of files to be scaled and subtracted; folder must be on Mantid path
index_files_to_transmission = "0"                                                       # index(es) of pair to subtract

#binning
binning_wavelength = [2.0, 0.5, 20.0]

# USER input end
# =====================================================================================================

# creating folder for output files
savefolder = os.path.join(os.path.dirname(transmission_list), folder_name)          # setting up full path
if not os.path.exists(savefolder):
    os.makedirs(savefolder)
print(savefolder)

# creating array of data from the input list
parameters = BilbyCustomFunctions_Reduction.files_list_reduce(transmission_list)
files_transmission = BilbyCustomFunctions_Reduction.files_to_reduce(parameters, index_files_to_transmission)

if len(files_transmission) == 0:
    raise ValueError('Please check index_files_transmission; chosen one does not exist')    

# transmission files one by one
for current_file in files_transmission:                              

# loading current sample + background pair + transmission
    empty_beam = current_file['T_EmptyBeam'] + '.tar'
    ws_empty = LoadBBY(empty_beam)

    sample_transmission = current_file['T_Sample'] + '.tar'
    ws_sam_transm = LoadBBY(sample_transmission)    
 
    transm_mask_load = current_file['mask_transmission']+'.xml'
    mask_transm = LoadMask('Bilby', transm_mask_load) 

#masking
    MaskDetectors(mask_transm, MaskedWorkspace=mask_transm) 
    MaskDetectors(ws_empty, MaskedWorkspace=mask_transm) 

#convert units and rebin
    ws_sam_wave=ConvertUnits(ws_sam_transm, 'Wavelength')
    ws_sam_transm_wave = Rebin(ws_sam_wave, Params=binning_wavelength, PreserveEvents=False)

#time for each, as a scaling factor
#scale to take into account data collection time
    time_empty = float(ws_empty.run().getProperty("frame_count").value)                    # ratio is enough 
    time_transm_sample = float(ws_sam_transm.run().getProperty("frame_count").value)      # ratio is enough
    scale_factor = time_empty/time_transm_sample
    ws_sam_transm_wave = Scale(ws_sam_transm_wave, scale_factor)

#empty beam
    ws_empty_wave=ConvertUnits(ws_empty, 'Wavelength')
    ws_empty_wave = Rebin(ws_empty_wave, Params=binning_wavelength, PreserveEvents=False)
#ws_empty_wave = SumSpectra(ws_empty_wave)
    
#Transmission  ===================================================================================================
#Define set of ID of masked detectors - needed as input for CalculateTransmission
    InvertMask(InputWorkspace=mask_transm, OutputWorkspace = "_ws")
    ws_tranMskInv = AnalysisDataService.retrieve("_ws")
    DetectorList = ExtractMask(InputWorkspace = ws_tranMskInv, OutputWorkspace = 'test')
    ws_tranROI = DetectorList[1]

#build file name
    suffix = current_file['suffix'].strip()
    additional_description = current_file['additional_description'].strip()
    if len(additional_description) > 0:
        suffix = suffix + '_' + additional_description

    #output_name = sample_transmission[0:(len(sample_transmission.strip()))] + '_' + suffix + '_transm_fit'
    output_name = sample_transmission[0:10] + '_' + suffix + '_transm_fit'    
    print (output_name)
    
#Calculating transmission
    output_ws = CalculateTransmission(ws_sam_transm_wave, ws_empty_wave, TransmissionROI = ws_tranROI, FitMethod = 'Polynomial', PolynomialOrder = '3', OutputUnfittedData = True, OutputWorkspace = output_name)
#FitMethod = 'Polynomial', PolynomialOrder = '2'
#FitMethod = 'Log' 'Linear'

# saving two files, fitted and raw transmittion as ASCII files
    savefile_fit = []
    savefile_row = []
    savefile_fit = os.path.join(savefolder, output_name +'.dat')          # setting up full path
    print (savefile_fit)
    SaveAscii(InputWorkspace = output_ws[0], Filename = savefile_fit, WriteXError = True, WriteSpectrumID = False, Separator = 'CSV', AppendToFile = True) #saving file
    savefile_row = os.path.join(savefolder, output_name +'_unfitted.dat')          # setting up full path
    print (savefile_row)
    SaveAscii(InputWorkspace = output_ws[1], Filename = savefile_row, WriteXError = True, WriteSpectrumID = False, Separator = 'CSV', AppendToFile = True) #saving file

    print ('Fitted T file exists:' , os.path.exists(savefile_fit))
    print ('Unfitted T file exists:' , os.path.exists(savefile_row))
                