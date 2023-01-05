# import mantid algorithms
from mantid.simpleapi import *
from mantid import *
from mantid.api import *
import csv, os
import BilbyCustomFunctions_Reduction

#============================================================================================================================================#

# USER input start

# NOTE output files will be created in the same folder where "subtraction_list" sits
# Folder containing "subtraction_list" file must be on Mantid path, set in  "File-> Manage User Directories"
# IF subtracted data file exists, it will be re-written
subtraction_list = FileFinder.getFullPath('list_subtr_9997.csv') # main list of files to be scaled and subtracted; folder must be on Mantid path
index_files_to_subtract = "31, 33,35"                                                        # index(es) of pair to subtract

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
    ws_sample = LoadNXcanSAS(sample_file)                                 # load sample data
    number_of_bins_sample = ws_sample.blocksize()
    number_of_spectra_sample =  ws_sample.getNumberHistograms()
      
    name_suffix = str(current_file["suffix"]).strip()                      # name of the output file name
    
    if len(name_suffix) > 1:
        name_suffix = "_" + name_suffix
    else:
        name_suffix = ""                                                               # just add _sub to the sample files name to construct the output name       

    replaced_name = str(current_file["output_file_name"]).strip()   # name of the output file name
    if len(replaced_name) == 0:
        replaced_name = ""                                                               # just add _sub to the sample files name to construct the output name       
   
    background_file = current_file["background"]    
      
    ws_bcgd = LoadNXcanSAS(background_file)                                 # load background data    

# subtracting data
    subtracted_data = Minus(ws_sample, ws_bcgd, AllowDifferentNumberSpectra = False)        
 
# set-up the name of output file; name is created from a name of the original SAMPLE file if "output_file_name" is empty
# otherwise it is taking output_file_name as a name for the output file, adding ".dat" at the end
   
    if len(replaced_name) > 0:
       sub_file_output_short = replaced_name + name_suffix + ".h5"
    elif len(name_suffix) > 0:
        sub_file_output_short = sample_file[0:(len(sample_file.strip())-4)] + name_suffix + ".h5"
    else:
        sub_file_output_short = sample_file[0:(len(sample_file.strip())-4)] + name_suffix + "_sub.h5"
        #print name_suffix.strip()
    sub_file_output = os.path.join(os.path.dirname(subtraction_list), sub_file_output_short) # path for the output file, based on location of the initial list

# creating new file, where X, Y, ErrY are taken from scaled/subtracted data, but the Xerror - i.e. sigmaQ - are copied from the original sample data
    
    print ("sub_file_output", sub_file_output)
    SaveNXcanSAS(subtracted_data, sub_file_output)
    #print ("File saved", FileFinder.getFullPath(sub_file_output))
    print ('2D h5 file exists: ', os.path.exists(sub_file_output))
