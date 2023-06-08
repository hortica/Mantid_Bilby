# 22 July 2021: plots update
# 30 June 2021
# PlotSpectrum works, MergePlots - not anymore
# Line 308: there were wrong brackets there, therefore it was not printing

# import mantid algorithms
from mantid.simpleapi import *
 
from mantid import *
import numpy as np
import os, csv, math
import matplotlib.pylab as plt
from mantid.kernel import Logger

import BilbyCustomFunctions_Reduction
ansto_logger = Logger('AnstoDataReduction')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# INPUT - mandatory from a USER - START##############################################
red_settings = FileFinder.getFullPath('mantid_reduction_settings_example.csv')

# INPUT - index of a line with reduction parameters
index_reduction_settings = ['0'] # INDEX OF THE LINE WITH REDUCTION SETTINGS
    
if len(index_reduction_settings) > 1: # must be single choice
    raise ValueError('Please check your choice of reduction settigns; only single value is allowed')

# ID to evaluate - INPUT, in any combination of 'a-b' or ',c', or empty line; empty line means evaluate all files listed in csv

index_files_to_reduce = '0'  # as per csv_files_to_reduce_list file - LINES' INDEXES FOR FILES TO BE REDUCED

#Data file with numbers
path_tube_shift_correction = FileFinder.getFullPath('shift_assembled.csv')

###########################################################################################
# INPUT - mandatory from a USER - END
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

###########################################################################################
# settings - what to do - applied for all loaded files - not to be changed by a user

correct_tubes_shift = True
data_before_2016 = False # curtains moved/ aligned /extra shift applied
data_before_May_2016 = False # Attenuators changed
account_for_gravity = True #False
solid_angle_weighting = True #False
wide_angle_correction = False
blocked_beam = True #False

if wide_angle_correction is True:
    print ('WARNING: wide_angle_correction is set to', wide_angle_correction, 'which will lead to the wrong calculations of error bars.')
    print ('WARNING: highly recommended to change the wide_angle_correction value to FALSE.')

###########################################################################################
###########################################################################################
# Reading parameters from the reduction settings file
reduction_settings_list = BilbyCustomFunctions_Reduction.files_list_reduce(red_settings) # read entire file
current_reduction_settings = BilbyCustomFunctions_Reduction.files_to_reduce(reduction_settings_list, index_reduction_settings[0]) # take only one line, # index_reduction_settings
# Read input csv file and define / create a folder for the output data

csv_files_to_reduce_list = FileFinder.getFullPath(current_reduction_settings[0]['csv_file_name'])

reduced_files_path_folder = os.path.dirname(csv_files_to_reduce_list)

reduced_files_path = reduced_files_path_folder + '\\' + current_reduction_settings[0]['reduced_files_folder'] # construct a path to a folder for reduced files 
# If folder does not exist, make it
if not os.path.exists(reduced_files_path):
    os.makedirs(reduced_files_path)

# Wavelength binning
try:
    binning_wavelength_ini_str = current_reduction_settings[0]['binning_wavelength_ini']
except:
    raise ValueError('binning_wavelength_ini cannot be empty')

binning_wavelength_ini = BilbyCustomFunctions_Reduction.read_convert_to_float(binning_wavelength_ini_str)  
binning_wavelength_ini_original = binning_wavelength_ini

#WAVELENGTH RANGE FOR TRANSMISSION: the aim is to fit transmission on the whole range, and take only part for the data reduction
# must  be equal or longer than binning_wavelength_ini
binning_wavelength_transmission_str = current_reduction_settings[0]['binning_wavelength_transmission']
binning_wavelength_transmission = BilbyCustomFunctions_Reduction.read_convert_to_float(binning_wavelength_transmission_str) 
binning_wavelength_transmission_original = binning_wavelength_transmission

# Check of wavelength range: transmission range must be equal or longer than the wavelength binning range for data reduction
if (binning_wavelength_ini[0] < binning_wavelength_transmission[0]) or (binning_wavelength_ini[2] > binning_wavelength_transmission[2]):
    raise ValueError('Range for transmission binning shall be equal or wider than the range for the sample wavelength binning (refer to line 94)')    

# Binning for Q
binning_q_str = current_reduction_settings[0]['binning_q']
binning_q = BilbyCustomFunctions_Reduction.read_convert_to_float(binning_q_str)  

# Put more explanation here what it is and what is going on
try:
    RadiusCut = current_reduction_settings[0]['RadiusCut']
except:
    RadiusCut = 0.0 # in case of data before February 2017 or in case the value is forgotten in the input file

try:
    WaveCut = current_reduction_settings[0]['WaveCut']
except:
    WaveCut = 0.0 # in case of data before February 2017 or in case the value is forgotten in the input file

# Transmission fit parameters
transmission_fit_ini = current_reduction_settings[0]['transmission_fit']
if (transmission_fit_ini != 'Linear')  and (transmission_fit_ini != 'Log') and (transmission_fit_ini != 'Polynomial'):
    raise ValueError('Check value of transmission_fit; it can be only \'Linear\', \'Log\' or \'Polynomial\', first letter is mandatory capital')    

PolynomialOrder = current_reduction_settings[0]['PolynomialOrder']

# Wavelength interval: if reduction on wavelength intervals is needed
wavelength_interval_input = current_reduction_settings[0]['wavelength_intervals'].lower()
wavelength_intervals = BilbyCustomFunctions_Reduction.string_boolean(wavelength_interval_input)
wavelength_intervals_original = wavelength_intervals
wav_delta = 0.0 # set the value, needed for the 'wavelengh_slices' function

# If needed to reduce 2D - this option is a defining one for the overall reduction
reduce_2D_input = current_reduction_settings[0]['reduce_2D'].lower()
reduce_2D = BilbyCustomFunctions_Reduction.string_boolean(reduce_2D_input)
if reduce_2D:
    print ('2D reduction is performing. Q interval and number of points are taking into account; Q-binning intervals are ignored.')
    try:
        number_data_points_2D = float(current_reduction_settings[0]['2D_number_data_points']) # for 2D Q-binning is not intuitive, hence only number of points is needed
    except:
        raise ValueError('Number of points shall be given')

    plot_2D = current_reduction_settings[0]['plot_2D'].lower()
    plot_2D = BilbyCustomFunctions_Reduction.string_boolean(plot_2D)
    binning_q[1] = (binning_q[2] - binning_q[0]) / number_data_points_2D # To replace deltaQ from the input file

###########################################################################################
 # Calling function to read given csv file
parameters = BilbyCustomFunctions_Reduction.files_list_reduce(csv_files_to_reduce_list)

files_to_reduce = BilbyCustomFunctions_Reduction.files_to_reduce(parameters, index_files_to_reduce)

if len(files_to_reduce) == 0:
    raise ValueError('Please check index_files_to_reduce; chosen one does not exist')

# reduce requested files one by one
for current_file in files_to_reduce:
    sam_file = current_file['Sample']+'.tar'
    StartTime = current_file['StartTime']
    EndTime = current_file['EndTime']
#Errors: if trying to reduce time slice larger than the total time of the measurement:
#Errors: if trying to reduce time slice larger than the total time of the measurement:
#Error message & Stop - to addBBY0050276_6.0_empty_cell_long

    if ((not StartTime) and (EndTime)) or ((StartTime) and (not EndTime)):
        raise ValueError('Check StartTime and EndTime values; either both or none shall be intered.')

    if (not StartTime) and (not EndTime):
        ws_sam = LoadBBY(sam_file)
        time_range = ''
    elif (float(StartTime)) > (float(EndTime)):
        raise ValueError('Check StartTime and EndTime values; EndTime cannot be smaller than StartTime.')        
    else:
        ws_sam = LoadBBY(sam_file)     # test loader: to check if given StartTime and EndTime are reasonable
        Real_EndTime_max = float(ws_sam.run().getProperty('bm_counts').value)
        if ( float(EndTime) > Real_EndTime_max  * 1.1 ):
            raise ValueError('EndTime value is wrong, it is more than 10%% larger than the data collection time: %7.2f' %Real_EndTime_max)
        ws_sam = LoadBBY(sam_file, FilterByTimeStart = StartTime, FilterByTimeStop = EndTime)    # now to load file within requested time slice if values are feasible
        time_range = '_' + StartTime + '_' + EndTime

    # To read the mode value: True - ToBBY0050431_2.0_20.0_CS_60C_30B_2MLF; False - NVS; this will define some steps inside SANSDataProcessor
    try:
        external_mode = (ws_sam.run().getProperty('is_tof').value)
    except:
        external_mode = True #This is needed for old files, where the ToF/mono mode value has not been recorded

    if (not external_mode): # Internal frame source has been used during data collection; it is not always NVS only, one can have both, NVS and choppers running for this mode
        print ('Internal frame source. Binning range is taken from the sample scattering data.')
        # issue found: transmission fit works on one data point and on three data points, but do not work on 2
        binning_wavelength_ini = ( ws_sam.readX(0)[0],
                                  (ws_sam.readX(0)[ws_sam.blocksize()] - ws_sam.readX(0)[0]), ws_sam.readX(0)[ws_sam.blocksize()])
        mean_wavelength = round((ws_sam.readX(0)[0] + ws_sam.readX(0)[ws_sam.blocksize()])/2, 1) # for output file name
        binning_wavelength_transmission = binning_wavelength_ini
        if wavelength_intervals:
            wavelength_intervals = False
            print ('NVS: monochromatic mode')
            print ('There is no sense to reduce monochromatic data on multiple wavelength; \'wavelength_intervals\' value changed to False.')
    else: # important for the case when NVS data is being analysed first, ie to be able to come back to the whole range & wavelength slices, if needed
            binning_wavelength_ini = binning_wavelength_ini_original
            binning_wavelength_transmission = binning_wavelength_transmission_original
            wavelength_intervals = wavelength_intervals_original    
            if wavelength_intervals:
                wav_delta = float(current_reduction_settings[0]['wav_delta']) # no need to read if the previous is false
    
    # empty beam scattering in transmission mode
    ws_emp_file = current_file['T_EmptyBeam']+'.tar'
    ws_emp = LoadBBY(ws_emp_file)    # Note that this is of course a transmission measurement - shall be long

    # transmission workspaces and masks
    transm_file = current_file['T_Sample']+'.tar'
    ws_tranSam = LoadBBY(transm_file)
    ws_tranEmp = LoadBBY(ws_emp_file) # empty beam for transmission
    transm_mask = current_file['mask_transmission']+'.xml'
    ws_tranMsk = LoadMask('Bilby', transm_mask)

    # Moving detectors manually, to be sure beam quoters & six panels overlaps matches
    
    #move_rearl =    [ -3.5,  2.0, 0.0] # in mm
    #move_rearr =    [ -3.5,  2.0, 0.0] # in mm

    #MoveInstrumentComponent(ws_sam, "BackDetectorLeft",       X=move_rearl[0]/1000,          Y=move_rearl[1]/1000,        Z=move_rearl[2]/1000) 
    #MoveInstrumentComponent(ws_sam, "BackDetectorRight",      X=move_rearr[0]/1000,          Y=move_rearr[1]/1000,        Z=move_rearr[2]/1000) 

    #MoveInstrumentComponent(ws_sam, 'CurtainLeft',          X= -7.2/1000,    Y=  3.7/1000,     Z=  36.5/1000)
    #MoveInstrumentComponent(ws_sam, 'CurtainRight',         X=  4.9/1000,    Y=  4.4/1000,     Z=  41.1/1000)
    #MoveInstrumentComponent(ws_sam, 'CurtainTop',           X= -2.7/1000,    Y= -2.1/1000,     Z=  34.6/1000)
    #MoveInstrumentComponent(ws_sam, 'CurtainBottom',        X= -3.8/1000,    Y=  8.6/1000,     Z=  32.3/1000)
    #MoveInstrumentComponent(ws_sam, 'BackDetectorRight',    X= -2.0/1000,    Y=  0.0/1000,     Z=  45.8/1000) 
    #MoveInstrumentComponent(ws_sam, 'BackDetectorLeft',     X= -2.0/1000,    Y=  0.0/1000,     Z=  45.8/1000)
    
    # scaling: attenuation
    att_pos = float(ws_tranSam.run().getProperty('att_pos').value)
    nguide_empty_beam = float(ws_tranEmp.run().getProperty('nguide').value)
    
    scale = BilbyCustomFunctions_Reduction.attenuation_correction(att_pos, nguide_empty_beam, data_before_May_2016)
    print ('scale, aka attenuation factor', scale) 

    thickness = current_file['thickness [cm]']

    # Cd / Al masks shift   
    if correct_tubes_shift:
        BilbyCustomFunctions_Reduction.correction_tubes_shift(ws_sam, path_tube_shift_correction)    

    if data_before_2016:
        BilbyCustomFunctions_Reduction.det_shift_before_2016(ws_sam)    

    #Blocked beam
    ws_blocked_beam = 'No blocked beam used'  # default value for the blocked beam; used for the header file
    if blocked_beam:
        ws_blocked_beam = current_file['BlockedBeam']+'.tar'
        ws_blk = LoadBBY(ws_blocked_beam)
        if correct_tubes_shift:
            BilbyCustomFunctions_Reduction.correction_tubes_shift(ws_blk, path_tube_shift_correction)            
    else:
         ws_blk = None

    # Detector sensitivity
    ws_sen = None

    # empty beam normalisation
    ws_emp = MaskDetectors('ws_emp', MaskedWorkspace=ws_tranMsk) # does not have to be ws_tranMsk, can be a specific mask
    ws_emp = ConvertUnits('ws_emp', Target='Wavelength')

    # wavelenth intervals: building  binning_wavelength list 
    binning_wavelength, n = BilbyCustomFunctions_Reduction.wavelengh_slices(wavelength_intervals, binning_wavelength_ini, wav_delta)

###########################################################################################
# By now we know how many wavelengths bins we have, so shall run Q1D n times
    # -- Processing --
    suffix = current_file['suffix'].strip()
    if suffix != '':
        suffix = '_' + current_file['suffix'].strip() # is the same for all wavelength intervals
    suffix_2 = current_file['additional_description'].strip()
    if suffix_2 != '':
        suffix += '_' + suffix_2

# Prepare figure formatting for 1D case; needed here, otherwise it will be a figure per wavelength slice
    fig, data_1D = plt.subplots(subplot_kw={'projection': 'mantid'})
    plt.tick_params(axis='x', direction='in'), plt.tick_params(axis='y', direction='in')
    data_1D.set_xscale('log'), data_1D.set_yscale('log')
    data_1D.set_xlabel('q ($\\AA^{-1}$)'), data_1D.set_ylabel('1/cm')
# End plot formatting section

###########################################################################################
### masking circle

    ws_sam_ini = CloneWorkspace(ws_sam) # To be sure masking is not going in circles
    sam_mask_file = current_file['mask']+'.xml' # load mask from the original input file
    ws_samMsk = LoadMask('Bilby', sam_mask_file) 
    
    standard_mask = current_reduction_settings[0]['standard_mask'] # read if do complex masking
    index_mask = 0
    suffix_ini = suffix

    if int(standard_mask) != 1 and int(standard_mask) != 4 and int(standard_mask) != 6:
        standard_mask = 1
        print ('==============================================================================')
        print ('Warning!!! The input for extra masking is wrong, only the main mask is applied')
        print ('==============================================================================')
        
    if int(standard_mask) != 1: # if extra masking needed
        masks_array = [] 
        name_array = []
        if int(standard_mask) == 4:
            masks_array = ['mask_scattering_l_d.xml', 'mask_scattering_l_u.xml', 'mask_scattering_r_d.xml', 'mask_scattering_r_u.xml']
            name_array = ['l_down', 'l_up', 'r_down', 'r_up']
        if int(standard_mask) == 6:
            masks_array = ['mask_scattering_r_left.xml', 'mask_scattering_r_right.xml', 'mask_scattering_top.xml', 'mask_scattering_bottom.xml', 'mask_scattering_left.xml', 'mask_scattering_right.xml']
            name_array = ['r_left', 'r_right', 'top', 'bottom', 'left', 'right']            
    else:
        masks_array = [sam_mask_file]
        
    for mask in masks_array:
        if int(standard_mask) != 1:
            ws_sam = CloneWorkspace(ws_sam_ini) # To be sure masking is not going in circles
            ws_samMsk_extra = LoadMask('Bilby', mask)       
            MaskDetectors('ws_sam', MaskedWorkspace = ws_samMsk_extra)
            suffix = suffix_ini + '_' + name_array[index_mask] # Adding extra to the file name
            index_mask += 1

###########################################################################################
### Wavelength slices

        for i in range (n):
            ws_emp_partial = Rebin('ws_emp', Params=binning_wavelength[i])
            ws_emp_partial = SumSpectra(ws_emp_partial, IncludeMonitors=False)           

            if reduce_2D:
               base_output_name = sam_file[0:10]+'_2D_'+ str(round(binning_wavelength[i][0], 1)) +'_'+ str(round(binning_wavelength[i][2],1)) + time_range + suffix  #A core of output name; made from the name of the input sample        
            else:
                if external_mode:
                   base_output_name = sam_file[0:10]+'_'+ str(round(binning_wavelength[i][0], 1)) +'_'+ str(round(binning_wavelength[i][2],1)) + time_range + suffix  #A core of output name; made from the name of the input sample            
                else:
                   #base_output_name = sam_file[0:10] + '_' + str(mean_wavelength) + time_range + suffix  #A core of output name; made from the name of the input sample             
                   base_output_name = sam_file[0:10] + time_range + suffix  #A core of output name; made from the name of the input sample                            

            transmission_fit = transmission_fit_ini # needed here, otherwise SANSDataProcessor replaced it with 'transmission_fit' string

            output_workspace, transmission_fit = BilbySANSDataProcessor(InputWorkspace=ws_sam, InputMaskingWorkspace=ws_samMsk,
                                  BlockedBeamWorkspace=ws_blk, EmptyBeamSpectrumShapeWorkspace=ws_emp_partial, SensitivityCorrectionMatrix=ws_sen,
                                  TransmissionWorkspace=ws_tranSam, TransmissionEmptyBeamWorkspace=ws_tranEmp, TransmissionMaskingWorkspace=ws_tranMsk,
                                  ScalingFactor=scale, SampleThickness=thickness,
                                  FitMethod=transmission_fit, PolynomialOrder=PolynomialOrder,
                                  BinningWavelength=binning_wavelength[i], BinningWavelengthTransm=binning_wavelength_transmission, BinningQ=binning_q,
                                  TimeMode = external_mode, AccountForGravity=account_for_gravity, SolidAngleWeighting=solid_angle_weighting,
                                  RadiusCut = RadiusCut, WaveCut = WaveCut,
                                  WideAngleCorrection=wide_angle_correction,
                                  Reduce2D = reduce_2D,
                                  OutputWorkspace = base_output_name)
        #print mtd.getObjectNames()
        #print transmission_fit.getHistory()
            out = CloneWorkspace(output_workspace)

###########################################################################################
### Data ploting and saving
            if reduce_2D:        
                fig, data_2D = plt.subplots(subplot_kw={'projection': 'mantid'})
                from mantid.api import AnalysisDataService as ADS
                data_to_plot = ADS.retrieve(base_output_name)            
  
                c = data_2D.pcolormesh(data_to_plot)
                data_2D.set_title(base_output_name)
                fig.colorbar(c) # shows the color bar
                fig.set_label('Intensity (1/cm)"')

            # Saving plots
                n_2D_png = output_workspace.name() + '.png'
                n_2D_png_path = os.path.join(os.path.expanduser(reduced_files_path), n_2D_png)
                fig.savefig(n_2D_png_path)
                n_2D_pdf = output_workspace.name() + '.pdf'
                n_2D_pdf_path = os.path.join(os.path.expanduser(reduced_files_path), n_2D_pdf)
                fig.savefig(n_2D_pdf_path)
     
                if (plot_2D): fig.show()
            
            # 2D data saving in two formats
                SaveNxs = os.path.join(os.path.expanduser(reduced_files_path), output_workspace.name() + '.nxs')
                SaveNISTDAT(output_workspace.name(), SaveNxs)
                print ('2D nxs file exists: ', os.path.exists(SaveNxs))
                SaveH5 = os.path.join(os.path.expanduser(reduced_files_path), output_workspace.name() + '.h5')
                SaveNXcanSAS(output_workspace.name(), SaveH5)
                print ('2D h5 file exists: ', os.path.exists(SaveH5))
            
            else: # 1D reduction          
                from mantid.api import AnalysisDataService as ADS
                data_to_plot = ADS.retrieve(base_output_name)
                data_1D.errorbar(data_to_plot, label = data_to_plot)
                plt.legend()
                try:
                   fig.show()
                except: # Mitigating the case when the plot is closed during creation; it is not good to close the plot before all wavelenght slices are complete.
                   fig, data_1D = plt.subplots(subplot_kw={'projection': 'mantid'})
                   data_1D.errorbar(data_to_plot, label = data_to_plot) # The first plot will be done on default settings, which is not pretty but clear to show that something went wrong
                   data_1D.set_xscale('log'), data_1D.set_yscale('log')
                   fig.show()
               
            # 1D file saving
                BilbyCustomFunctions_Reduction.strip_NaNs(output_workspace, base_output_name)               
                n_1D = base_output_name +'.dat'       # 1D output file; name based on 'base_output_name' construct
                savefile = os.path.join(os.path.expanduser(reduced_files_path), n_1D)          # setting up full path

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
#something new 26 March 2019
            #add parameters into the file header
                header = BilbyCustomFunctions_Reduction.output_header(external_mode, binning_wavelength[i], ws_sam, thickness, transm_file, ws_emp_file, ws_blocked_beam, sam_mask_file, transm_mask)
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

                f = open(savefile, 'w') # open file re-wring existing one
                for line in header: # write the rest of the header in the file      
                   with open(savefile, 'a') as f_out:
                      f_out.write(line+'\n')
                f.close()                
           #to sort out the list & define what is in for ToF

                SaveAscii(InputWorkspace = base_output_name, Filename = savefile, WriteXError = True, WriteSpectrumID = False, Separator = 'CSV', AppendToFile = True) #saving file
                print (savefile)
                print ('1D File Exists:' , os.path.exists(savefile))

###########################################################################################
# - add subtraction of the background -- later