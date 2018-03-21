## SECOND ONE

from mantid.api import *
import csv
import BilbyCustomFunctions_Reduction
reload (BilbyCustomFunctions_Reduction)

#============================================================================================================================================#

# USER input start

# NOTE output files will be created in the same folder where "subtraction_list" sits
# Folder containing "subtraction_list" file must be on Mantid path, set in  "File-> Manage User Directories"
# IF subtracted data file exists, it will be re-written
subtraction_list = FileFinder.getFullPath('list_example.csv') # main list of files to be scaled and subtracted; folder must be on Mantid path
index_files_to_subtract = "1,2"                                                        # index(es) of pair to subtract

# USER input end

# =====================================================================================================
# creating array of data from the input list
parameters = BilbyCustomFunctions_Reduction.FilesListReduce(subtraction_list)
files_to_subtract = BilbyCustomFunctions_Reduction.FilesToReduce(parameters, index_files_to_subtract)
#mtd.clear()

# reduce requested files one by one
for current_file in files_to_subtract:                              

# loading current sample + background pair
    sample_file = current_file["sample"]
    ws_sample_ini = LoadAscii(sample_file)                                 # load sample data
    
    background_file = current_file["background"]    
    ws_bcgd_ini = LoadAscii(background_file)                                # load background data

# check if the input files have the same number of points and contain only one spectrum
    number_of_bins_sample = ws_sample_ini.blocksize()
    number_of_spectra_sample =  ws_sample_ini.getNumberHistograms()
    number_of_bins_bcgd = ws_bcgd_ini.blocksize()    
    number_of_spectra_bcgd =  ws_bcgd_ini.getNumberHistograms()
    if (number_of_spectra_sample > 1 or number_of_spectra_bcgd > 1):
        raise ValueError("each data set must contain only one spectrum")    
# end of check
        
    try:
        scale_subtr_ini = float(current_file["scale_subtr"])             # const to subtract from the sample data
        scale_subtr = scale_subtr_ini*(-1)                                          # needed because "Scale" knows only how to add        
    except:
        scale_subtr_ini = 0.0                                                         # ini value is needed only for the logging into the result file, avoiding stuff like "-0"
        scale_subtr = 0.0                                                              # if there is no value in the input file, default value is 0
    try:
        scale_mult = float(current_file["scale_mult"])                # const to multiply background
    except:
        scale_mult = 1.0                                                               # if there is no value in the input file, default value is 1

    name_suffix = str(current_file["suffix"])                           # name of the output file name
    if len(name_suffix) > 1:
        name_suffix = "_" + name_suffix
    else:
        name_suffix = ""                                                               # just add _sub to the sample files name to construct the output name       

    replaced_name = str(current_file["output_file_name"])         # name of the output file name
    if len(replaced_name) == 0:
        replaced_name = ""                                                               # just add _sub to the sample files name to construct the output name       

    ws_sample_const_sub = Scale(ws_sample_ini, scale_subtr, "Add")     # subtract const from the SAMPLE
    ws_bcgd_scaled = Scale(ws_bcgd_ini, scale_mult, "Multiply") # multiply BACKGROUND data by const
    subtracted_data = Minus(ws_sample_const_sub, ws_bcgd_scaled, AllowDifferentNumberSpectra = True)
    
# set-up the name of output file; name is created from a name of the original SAMPLE file if "output_file_name" is empty
# otherwise it is taking output_file_name as a name for the output file, adding ".dat" at the end
   
    if len(replaced_name) > 0:
       sub_file_output_short = replaced_name + name_suffix + ".dat"
    else:
        sub_file_output_short = sample_file[0:(len(sample_file)-4)] + name_suffix + "_sub.dat"

    sub_file_output = os.path.join(os.path.dirname(subtraction_list), sub_file_output_short) # path for the output file, based on location of the initial list
    
    if os.path.exists(sub_file_output):            # check if it does exist; delete if yes - no avoid appending 
       os.remove(sub_file_output)                  # ??? to check how does it know the path here ???
    if not os.path.exists(sub_file_output):     # check if it does exist; create if not - to prepare for data recording
        file = open(sub_file_output, 'w+')                     
        file.close()     

# creating header from input data
    header_line = []
    header_line.append(['Sample file name: ' + sample_file])
    header_line.append(['Background file name: ' + background_file])
    header_line.append(['Constant to subtract from sample scattering = ' + str(scale_subtr_ini)])
    header_line.append(['Background multiplier = ' + str(scale_mult)])
# writing header in the file
    for line in header_line:
        with open(sub_file_output, 'ab') as f_out:
            wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
            wr.writerow(line)

# creating new file, where X, Y, ErrY are taken from scaled/subtracted data, but the Xerror - i.e. sigmaQ - are copied from the original sample data
    line_new_file = []
    for i in range(number_of_bins_sample):
        s = str(subtracted_data.readY(0)[i])
        if s.find("nan") == -1:  # skip lines with nan; need proper testing
            line_new_file = ["%8.5f" %subtracted_data.readX(0)[i],   "%8.5f" %subtracted_data.readY(0)[i], \
                                     "%8.5f" % subtracted_data.readE(0)[i], "%8.5f" %ws_sample_ini.readDx(0)[i]]
            with open(sub_file_output, 'ab') as f_out:
                wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
                wr.writerow(line_new_file)
        #else:
            #print "s nan" # temporary measure to see if some nan were found; to be deleted later

# Just subtracted data are loaded back to Mantid
# It is still a question if to keep it here
# For good practice, make a function out of this script and make this parameter a user' choice
    LoadAscii(sub_file_output, Unit = "MomentumTransfer", OutputWorkspace = sub_file_output_short)


#============================================================================================================================================#
#============================================================================================================================================#



