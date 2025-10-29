from mantid.simpleapi import *
 
from mantid import *
import numpy as np
import os, csv, math
import matplotlib.pylab as plt
from mantid.kernel import Logger

import BilbyCustomFunctions_Reduction
#ansto_logger = Logger('AnstoDataReduction')

# separate function to check elements ===============================================================

# check if a given line contains only real numbers (integers or floats) =============================

def contains_only_real_numbers(line):  

    elements = line.strip().split()  # Split by whitespace and remove leading/trailing whitespace
    if not elements:  # handle empty lines
        return False
    for element in elements:
        try:
            float(element)  # attempt to convert to a float
        except ValueError:
            return False    # if conversion fails, it's not a real number
    return True  # all elements were successfully converted, line can be considered as data line

# ===================================================================================================

# user input ========================================================================================
# ===================================================================================================

file_list_to_rebin = FileFinder.getFullPath ('files_to_rebin_list.txt') # plain text file, one name on a line; remove last empty line - no checks for now
params_q_binning = [0.0001, -0.1, 0.7] # q-binning range; there is a check if values are out of range

# ===================================================================================================

# open list of files to rebin; just plain text file, reads the whole thing ==========================

with open(file_list_to_rebin, 'r') as f_list:
    for file_name in f_list:
        # for later: add check for empty lines - usually there is on at the end by default
        ws_name_out = file_name[0:(len(file_name)-5)] + '_rebin.dat' # to set before the full path will be added
        filename = FileFinder.getFullPath(file_name)

        # open each file and read only lines with numbers; ignore 4th column for now, to add later
        with open(filename, 'r') as f:
            x, y, dx, dy, elements = [], [], [], [], []
            #i = 0 # eventually will be needed for the header and smart stuff
            for line in f:
                if (contains_only_real_numbers(line)):
                    elements = (line.strip().split())         
                    x.append(float(elements[0]))
                    y.append(float(elements[1]))
                    if (float(elements[2]) == 0):  # extrapolated regions do not have errors; adding sqrt from intensity here
                        dy.append(np.sqrt(float(elements[1])))
                    else:
                        dy.append(float(elements[2]))
                   #i += 1
        f.close()

        # check if available q-range is not smaller than requested binning ==============================    
        # ========== to add later somethign smart if one file by chance is too short and several has been converted before    
        if (params_q_binning[0] < np.min(x)) or (params_q_binning[2] > np.max(x)):
            print ('available qmin, qmax, requested binning for qmin, qmax', np.min(x), np.max(x), params_q_binning[0], params_q_binning[2])
            raise ValueError('Binning range is wider that available q-range ')    
        # end of check ==================================================================================

        # create workspace with loaded data X, Y, dY ====================================================
        ws_intermediate = CreateWorkspace(DataX = x, DataY = y, DataE = dy, UnitX = 'MomentumTransfer') #Dx=dx

        # articifical convert to histogram and assigning true Distribution so Rebin can work properly
        ws_name_out_hist = ConvertToHistogram(ws_intermediate)
        ws_name_out_hist.setDistribution(True)
        ws_sam_rebin = Rebin(ws_name_out_hist, params_q_binning, PreserveEvents=False) # rebin as per input values

        # save rebin file, no X-error for now ============================================================
        #print(os.path.expanduser(filename))
        savefile = os.path.join(os.path.dirname(filename), ws_name_out) 
        SaveAscii(InputWorkspace = ws_sam_rebin, Filename = savefile, WriteXError = False, WriteSpectrumID = False, Separator = 'CSV', AppendToFile = False) #saving file

        # check the file is good, loading it back - total overkill =======================================
        LoadAscii(savefile, Unit = "MomentumTransfer", OutputWorkspace = ws_name_out[0:(len(ws_name_out.strip())-4)] + '_loaded_back')
        print ("File saved", FileFinder.getFullPath(ws_name_out))


f_list.close()