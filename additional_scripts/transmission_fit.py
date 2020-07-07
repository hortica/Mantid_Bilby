import numpy as np
import mantid.simpleapi
from mantid.api import *

#input parameters  ==============================================================================================
#sample transmission, empty beam transmission, mask to select area to calculate transmissions
transm_sam = "BBY0014167.tar"
empty_beam = "BBY0014172.tar"
mask_transm = "transmission_mask_6286.xml"

#binning
binning_wavelength = [3.0,8.5, 20.0]

#load data  ======================================================================================================
ws_sam_transm = LoadBBY(transm_sam)
ws_mask_transm = LoadMask('Bilby', mask_transm) 
ws_empty = LoadBBY(empty_beam)


time_empty = float(ws_empty.run().getProperty("frame_count").value)                    # ratio is enough
time_transm_sample = float(ws_sam_transm.run().getProperty("frame_count").value)      # ratio is enough

#masking
MaskDetectors(ws_sam_transm, MaskedWorkspace=ws_mask_transm) 
MaskDetectors(ws_empty, MaskedWorkspace=ws_mask_transm) 

#convert to wavelength, bin and sum ================================================================================
#sample transmission
ws_sam_wave=ConvertUnits(ws_sam_transm, 'Wavelength')
ws_sam_transm_wave = Rebin(ws_sam_wave, Params=binning_wavelength, PreserveEvents=False)
#ws_sam_transm_wave = SumSpectra(ws_sam_transm_wave)

#scale to take into account data collection time
scale_factor = time_empty/time_transm_sample
ws_sam_transm_wave = Scale(ws_sam_transm_wave, scale_factor)

#empty beam
ws_empty_wave=ConvertUnits(ws_empty, 'Wavelength')
ws_empty_wave = Rebin(ws_empty_wave, Params=binning_wavelength, PreserveEvents=False)
#ws_empty_wave = SumSpectra(ws_empty_wave)

    
#Transmission  ===================================================================================================
#Define set of ID of masked detectors - needed as input for CalculateTransmission
InvertMask(InputWorkspace=ws_mask_transm, OutputWorkspace = "_ws")
ws_tranMskInv = AnalysisDataService.retrieve("_ws")
DetectorList = ExtractMask(InputWorkspace = ws_tranMskInv, OutputWorkspace = 'test')
ws_tranROI = DetectorList[1]
#Just to check
size = DetectorList[1].size
print (size)
DeleteWorkspace('_ws')
DeleteWorkspace('test')

#Calculating transmission
transm_S1_PS_PEO_IrCl3_formic_1 = CalculateTransmission(ws_sam_transm_wave, ws_empty_wave, TransmissionROI = ws_tranROI, FitMethod = 'Linear', PolynomialOrder = '3', OutputUnfittedData = True)
#FitMethod = 'Polynomial', PolynomialOrder = '2'
#FitMethod = 'Log' 'Linear'