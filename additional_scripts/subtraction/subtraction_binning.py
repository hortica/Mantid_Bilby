# import mantid algorithms
from mantid.simpleapi import *
from mantid.api import *
import csv
import numpy as np
import BilbyCustomFunctions_Reduction

#============================================================================================================================================#

# USER input start

# NOTE output files will be created in the same folder where "subtraction_list" sits
# Folder containing "subtraction_list" file must be on Mantid path, set in  "File-> Manage User Directories"
# IF subtracted data file exists, it will be re-written
subtraction_list = FileFinder.getFullPath('list_7259_BP85_TR_symm_subtract_aug.csv') # main list of files to be scaled and subtracted; folder must be on Mantid path
index_files_to_subtract = '10'                                                       # index(es) of pair to subtract

# USER input end

# =====================================================================================================
# creating array of data from the input list
parameters = BilbyCustomFunctions_Reduction.files_list_reduce(subtraction_list)
files_to_subtract = BilbyCustomFunctions_Reduction.files_to_reduce(parameters, index_files_to_subtract)
#mtd.clear()
if len(files_to_subtract) == 0:
    raise ValueError('Please check index_files_to_subtract; chosen one does not exist')    
        
# reduce requested files one by one
for current_file in files_to_subtract:                              

# loading current sample + background pair
    sample_file = current_file["sample"]
    if sample_file == '':
        raise ValueError('There is no sample name given. Seriously??')    
    ws_sample_ini = LoadAscii(sample_file, Unit = "MomentumTransfer")                                 # load sample data
    number_of_bins_sample = ws_sample_ini.blocksize()
    number_of_spectra_sample =  ws_sample_ini.getNumberHistograms()

    try:
        scale_subtr_ini = float(current_file["scale_subtr"])             # const to subtract from the sample data
        scale_subtr = scale_subtr_ini*(-1)                                       # needed because "Scale" knows only how to add        
    except:
        scale_subtr_ini = 0.0                                                           # ini value is needed only for the logging into the result file, avoiding stuff like "-0"
        scale_subtr = 0.0                                                                # if there is no value in the input file, default value is 0

    name_suffix = str(current_file["suffix"]).strip()                      # name of the output file name
    
    if len(name_suffix) > 1:
        name_suffix = "_" + name_suffix
    else:
        name_suffix = ""                                                               # just add _sub to the sample files name to construct the output name       

    replaced_name = str(current_file["output_file_name"]).strip()   # name of the output file name
    if len(replaced_name) == 0:
        replaced_name = ""                                                               # just add _sub to the sample files name to construct the output name       

    ws_sample_const_sub = Scale(ws_sample_ini, scale_subtr, "Add")     # subtract const from the SAMPLE

    rebinning = False    
    try:     # background file might not be given; if not given, multiplier is not needed; only const will be subtracted from the sample
        background_file = current_file["background"]    
        ws_bcgd_ini = LoadAscii(background_file, Unit = "MomentumTransfer")                                # load background data
        # check if the input files contain only one spectrum
        number_of_bins_bcgd = ws_bcgd_ini.blocksize()         
        number_of_spectra_bcgd =  ws_bcgd_ini.getNumberHistograms()
              
        if (number_of_spectra_sample > 1 or number_of_spectra_bcgd > 1):
            raise ValueError("each data set must contain only one spectrum")    
        # end of check
        try:
            scale_mult = float(current_file["scale_mult"])                   # const to multiply background
        except:
            scale_mult = 1.0                                                               # if there is no value in the input file, default value is 1
            
        ws_bcgd_scaled = Scale(ws_bcgd_ini, scale_mult, "Multiply") # multiply BACKGROUND data by const  
        # check if range is different and rebin if needed ===========================================================
        binning  = []
        if (ws_bcgd_ini.readX(0)[0] != ws_sample_ini.readX(0)[0]) or (ws_bcgd_ini.readX(0)[ws_bcgd_ini.blocksize()-1] != ws_sample_ini.readX(0)[ws_sample_ini.blocksize()-1]):
            print ("WARNING: ranges of the data are NOT the same")
            new_left  = max(ws_bcgd_ini.readX(0)[0], ws_sample_ini.readX(0)[0])
            new_right = min(ws_bcgd_ini.readX(0)[ws_bcgd_ini.blocksize()-1], ws_sample_ini.readX(0)[ws_sample_ini.blocksize()-1])
            if (ws_bcgd_ini.readX(0)[1]-ws_bcgd_ini.readX(0)[0]) == (ws_bcgd_ini.readX(0)[2]-ws_bcgd_ini.readX(0)[1]):
               binning_q = round((ws_bcgd_ini.readX(0)[1]-ws_bcgd_ini.readX(0)[0]), 3)
               print ("linear q binning", binning_q)
            else:
                binning_q = round((-1)*np.log((ws_bcgd_ini.readX(0)[1]/ws_bcgd_ini.readX(0)[0])),3)
                print ("log q binning", binning_q)
            binning = [new_left, binning_q, new_right]
            if (binning_q == 0):
                print ('Binning is too rough, so binning_q worked out to be 0; the script will not be able to rebin hence will ignore the background in this case.')
            ws_sample_const_sub = Rebin(ws_sample_const_sub, binning);
            ws_bcgd_scaled = Rebin(ws_bcgd_scaled, binning);            
            number_of_bins_sample = ws_sample_const_sub.blocksize()
            rebinning = True
        # =====================================================================================================
        subtracted_data = Minus(ws_sample_const_sub, ws_bcgd_scaled, AllowDifferentNumberSpectra = False)
        background = "yes"
    except:
        subtracted_data = ws_sample_const_sub
        background = "none"
        print ("Background file either is not specified or does not exist or there is a bug hiding in this script")      
        
# set-up the name of output file; name is created from a name of the original SAMPLE file if "output_file_name" is empty
# otherwise it is taking output_file_name as a name for the output file, adding ".dat" at the end
   
    if len(replaced_name) > 0:
       sub_file_output_short = replaced_name + name_suffix + ".dat"
    elif len(name_suffix) > 0:
        sub_file_output_short = sample_file[0:(len(sample_file.strip())-4)] + name_suffix + ".dat"
    else:
        sub_file_output_short = sample_file[0:(len(sample_file.strip())-4)] + name_suffix + "_sub.dat"
    sub_file_output = os.path.join(os.path.dirname(subtraction_list), sub_file_output_short) # path for the output file, based on location of the initial list

# creating header from input data
    header_line_first = (['Sample file name: ' + sample_file]) # record first line separately to be sure file is re-written
    with open(sub_file_output, 'w+') as f_out:
        wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
        wr.writerow(header_line_first)

    header_line = [] # add further header lines

    if background != "none":    
        header_line.append(['Background file name: ' + background_file])
        header_line.append(['Background multiplier = ' + str(scale_mult)])
    else:
        raise ValueError("No background file given; please check input csv file; possibly files extensions are missing.")        
        #header_line.append(['No background file given; only const subtracted'])            

    if(rebinning):
        header_line.append(['Data has been rebinned; the new range is '+ str(binning[0]) + ', ' + str(binning[1]) + ', ' + str(binning[2])])
   
    header_line.append(['Constant to subtract from sample scattering = ' + str(scale_subtr_ini)])
    
    for line in header_line: # write the rest of the header in the file
        with open(sub_file_output, 'a') as f_out:
            wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
            wr.writerow(line)

# creating new file, where X, Y, ErrY are taken from scaled/subtracted data, but the Xerror - i.e. sigmaQ - are copied from the original sample data
    line_new_file = []
    #for i in range(number_of_bins_sample):
        #ws_sample_const_sub.blocksize()
    for i in range(subtracted_data.blocksize()):        
        s = str(subtracted_data.readY(0)[i])
        if s.find("nan") == -1:  # skip lines with nan; need proper testing
            line_new_file = ["%8.5f" %subtracted_data.readX(0)[i],   "%8.5f" %subtracted_data.readY(0)[i], \
                                     "%10.8f" %subtracted_data.readE(0)[i],  "%10.8f" %ws_sample_const_sub.readDx(0)[i]]
            with open(sub_file_output, 'a+') as f_out:
                wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
                wr.writerow(line_new_file)

# Just subtracted data are loaded back to Mantid
# It is still a question if to keep it here
# For good practice, make a function out of this script and make this parameter a user' choice
    LoadAscii(sub_file_output, Unit = "MomentumTransfer", OutputWorkspace = sub_file_output_short)
    print ("File saved", FileFinder.getFullPath(sub_file_output_short))

#============================================================================================================================================#
#============================================================================================================================================#