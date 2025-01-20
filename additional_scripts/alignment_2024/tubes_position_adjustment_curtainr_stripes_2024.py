# import mantid algorithms, numpy and matplotlib
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np

from mantid.api import *
import os, csv

import BilbyCustomFunctions_memory
#reload (BilbyCustomFunctions_memory)

#######################################################################################
####################################################################################### 

def GetPixelSize():     # reads current IDF and get pixelsize from there
    from mantid.api import ExperimentInfo
    import xml.etree.ElementTree as ET

    currentIDF = ExperimentInfo.getInstrumentFilename("Bilby")
    print (currentIDF)
    tree = ET.parse(currentIDF)
    for node in tree.iter():
        if node.tag=="{http://www.mantidproject.org/IDF/1.0}height":
            name = node.attrib.get('val')
    pixelsize = float(name)
  
    return pixelsize

#######################################################################################
#######################################################################################
def Create_WS(x, y): # use instead of normal CrearWS, to avoid DataAnalysisService

    # Essentially I'm calling the function without going through mantid.simpleapi, so it doesn't go into the AnalysisDataService
    create_algorithm = AlgorithmManager.create('CreateWorkspace')
    create_algorithm.setChild(True) # Setting this to true keeps everything outside the AnalysisDataService
    create_algorithm.initialize()
    create_algorithm.setProperty('DataX', x)
    create_algorithm.setProperty('DataY', y)
    create_algorithm.setProperty('OutputWorkspace', 'dummy_value')# We have to provide this but we never use it.
    create_algorithm.execute()
    ws = create_algorithm.getProperty('OutputWorkspace').value
    return ws

##################################################################################

def OnePanelShiftValuesRearR_2024_test(ws_corr, start_tube_number, current_tube_min_pixel_left, current_tube_min_pixel_right, tubes_list, sigma, height):# calculates shift for each tube for a stripe of given location
# sutable for BorAl diagonal mask on the rear right panel
# Most advanced (i.e. flexible) one
# input: ws, tube to start with, range of pixels to look for a peak (in a range from 1 to 256), list of tubes to consider, estimated sigma and height for Gaussian peak
# Tubes out of consideration marked as -1 - in the main script. Custom made stuff.
# output: list of positions of minimum, list of average_position for a peak on each tube and diff_position_of_minimum, difference between initial position and average

    #print ('current_tube_min_pixel_left ', current_tube_min_pixel_left)
    x_left = current_tube_min_pixel_left # depends on panel - but can be calculated from previous; x - is not an important information for users
    #print('x_left ', x_left)
    
    #print('current_tube_min_pixel_right ', current_tube_min_pixel_right)
    x_right = current_tube_min_pixel_right # depends on panel  # range of pixels the minimum sits in 41130-256*160 = 170
    #print('x_right ', x_right)

    position_of_minimum = []
    sum_position_of_minimum = 0.0
    
    sigma_values = []

    i = -1 # index count
    Ind_minus1 = 0 # count of -1 tubes
    
    for tube_number in tubes_list:    # one panel is always 40 tubes and 256 pixels; -1 means tube is not considering
        i = i + 1
        if not (tube_number == -1):
            x1 = [n for n in range(x_left, x_right+1)]
            current_tube_min_pixel = current_tube_min_pixel_left + 256 * int(tube_number)          
            #print(current_tube_min_pixel)
            current_tube_max_pixel = current_tube_min_pixel_right + 256 * int(tube_number)
            #print(current_tube_max_pixel)
                        
            y1 = [ws_corr.readY(n)[0] for n in range(current_tube_min_pixel, current_tube_max_pixel+1)]
            current_tube_ws = Create_WS(x1, y1)  #create ws for each tube; needed because Mantid fit works only with ws
            name_current_tube = 'ws_tube' + str(start_tube_number + tube_number)   
            AnalysisDataService.addOrReplace(name_current_tube, current_tube_ws) # Only now can I see it print mtd.getObjectNames()

            startX = x_left
            endX = x_right
            #print('startX, endX ', startX, endX)
            
            tryCentre = str((x_left + x_right)/2) #'190'   # A start guess on peak centre
            #print(tryCentre)
            myFunc = 'name=FlatBackground, A0=10.0; name=Gaussian, Height=' + height + ', PeakCentre=' + tryCentre + ', Sigma=' + sigma

            #fitStatus, chiSq, covarianceTable, paramTable, fitWorkspace = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX = endX, Output='fit', Function=myFunc)
            #2024
            fit_output = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX = endX, Output='fit', Function=myFunc)

            #2024 add
            paramTable = fit_output.OutputParameters  # table containing the optimal fit parameters
            #fitWorkspace = fit_output.OutputWorkspace # 2024: not really needed to save
            # ========================================            

            #calc_position_of_gauss = paramTable.column(1)[2]
            #print("Fitted centre value is: {:.2f}".format(paramTable.column(1)[1]))
            #2024
            calc_position_of_gauss = paramTable.column(1)[2]
            #print('calc_position_of_gauss, in pixels ', calc_position_of_gauss)
            #print calc_position_of_gauss "%4.3f" %
            calc_sigma = paramTable.column(1)[3]
            sigma_values.append(calc_sigma)
            
            position_of_minimum.append(calc_position_of_gauss)
            sum_position_of_minimum += float(position_of_minimum[i])
            
        else:
            calc_position_of_gauss = 0.0
            position_of_minimum.append(calc_position_of_gauss)
            sum_position_of_minimum += float(position_of_minimum[i])
            Ind_minus1 += 1
            
    # Calculate averaged position
    average_position = sum_position_of_minimum/(40 - Ind_minus1) # real number of tubes  #position_of_minimum[5] 
    # Create array of differences, relative shift in pixels
    diff_position_of_minimum = []

    for pos_of_min in position_of_minimum: 
        if pos_of_min == 0.0:
            pos_of_min = average_position # to avoid shift of tubes which are out of consideration
        diff_position_of_minimum.append("%4.3f" % float(pos_of_min - average_position))
    #print('diff_position_of_minimum ', diff_position_of_minimum)
    #DeleteWorkspace(name_current_tube)# - sort out how to get back to these WS
    #print name_current_tube, "deleted" #

    return position_of_minimum, average_position, diff_position_of_minimum, sigma_values

#######################################################################################
def OutputFileFormatRecord_2024(diff_position_of_minimum, out_filename, format): #input is a list, path and filename and format "rows" or "columns"
    #print('inside ', out_filename)
    #filename = os.path.join(path,out_filename) # make an input parameter - or make it an input for the writing function

    if not os.path.exists(out_filename):                                   # Nice one but written not by me, though after me spending ages learning about lists, columns, izip etc
        file = open(out_filename, 'w+')                                      # Used here after it got understood...  tempfile, None and "*" are new things here for me
        print ('no file')
        file.close()                                                                

    if format == "rows":
        # If output wants to be rows - simple and logical
        with open(out_filename, 'a') as f_ini:                 # 2024: ab does not work, it wants binary!!! Old thing, trapped again
            wr = csv.writer(f_ini, delimiter=',', lineterminator='\n')
            wr.writerow(diff_position_of_minimum)    # will write everything in one row
            
    elif format == "columns":
        print (format)
        tmpfile = tempfile.TemporaryFile('r+')                        # If output wants to be columns
        with open(filename) as csvfile:
            nrOfCols = rowCnt = 0
            #print (csvfile)
            r = csv.reader(csvfile)
            wr = csv.writer(tmpfile, lineterminator='\n')
            for row in r:
                nrOfCols = max(nrOfCols, len(row)) # Counting number of values in a row to properly add new rows if needed. The number of values in each row should be constant, but let's use max() on each iteration anyway.
                 # If 'values' has less values than the original spreadsheet has rows, then add an empty cell.
                value = diff_position_of_minimum[rowCnt] if len(diff_position_of_minimum) > rowCnt else None  # write till take all of diff_position_of_minimum; when running out, add 0 if there are still rows in original file
                wr.writerow(row + [value])
                rowCnt += 1 # counting how many rows have been written

        # If `values` has more values than the original spreadsheet has rows, then add new rows.
        if rowCnt < len(diff_position_of_minimum):  # in other words, here we are running out of available rows in initial file
            row = [None] * nrOfCols # prepend the row with `nrOfCols` empty cells; "list * int" means just repeating given list int times; 'row' here is a new variable, of course!
            for value in diff_position_of_minimum[rowCnt:]:
                wr.writerow(row + [value])
        with open(filename, 'w') as csvfile:
            tmpfile.seek(0)
            shutil.copyfileobj(tmpfile, csvfile)
    else:
        print ("Wrong input format. Please check and correct.")
        sys.exit()

####################################################################################### 

############ INPUT 1(3) ############
# Cd lines file
Cd_test_file = 'BBY0073253_H2O_Cd_masks_open_curtains.tar' #'BBY0001429.tar' # Cd_test_file = '297_Cd_lines_setup2.tar' #296_Cd_lines_setup1 

# Path and file name and the format of csv where shifst will be recorded
path = "W:/data/proposal/00113/2024-09-30_Sokolova_re_commissioning/AgBeh_paper_water_tests/stretch_test" # define before the function call
os.chdir(path)
print(os. getcwd())
out_filename = "shift_in_pixels_curtainright_Jan25_test.csv"  # CHECK IF FILE ALREADY EXIST AND IF YES, CHECK ITS FORMAT; file appends, but mess with columns and rows is not a good thing to get
out_filename_maximums = "maximum_positions_curtainright_Jan25_test.csv"  # CHECK IF FILE ALREADY EXIST AND IF YES, CHECK ITS FORMAT; file appends, but mess with columns and rows is not a good thing to get
out_sigma_values = "sigma_values_curtainright_Jan25_test.csv"
format = "rows" # format values: "columns" or "rows"

############ END OF INPUT 1 ############

pixelsize = GetPixelSize()
#pixelsize = 0.003
print (pixelsize) 

# Load data
ws_sam = LoadBBY(Cd_test_file)
ws_corr = CloneWorkspace(ws_sam)         # Copy of the input workspace, to be shifted; created to be able to compare with the original one

period = float(ws_corr.run().getProperty("period").value) # Get T0 chopper period value
binning_time = [0.0, period, period]
ws_corr = Rebin(ws_corr, Params = binning_time, PreserveEvents = False) # Wavelength binning is not needed; it takes too long to convert the file

###############################################
# CurtainRight - only
############ INPUT 2(3) ############ Create a list of tubes to consider for each stripe
start_tube_number = 41 # because it is right panel
twoD_array_points = []

for line_number in range (1, 10): # It is known there are nine stripes
    #current_tube_min_pixel_left = 10259 + (line_number-1) * 24         # starting from 5th tube #51218
    current_tube_min_pixel_left = 10259 + (line_number-1) * 22          # 2024: it all shrunk now
    #print('current_tube_min_pixel_left ', current_tube_min_pixel_left)
    current_tube_min_pixel_right = current_tube_min_pixel_left + 18 + line_number        #18    
    #print(current_tube_min_pixel_right)
    sigma = '4.0'          # A start guess on peak width CAREFUL!!! A LOT OF TROUBLES  === the limits shall be wide, to cover a shifter slop of the most remote peak; otherwise the fit will be over
    height = '500'         # A start guess on peak height CAREFUL!!! A LOT OF TROUBLES    

#average_position_curtainl, diff_position_of_minimum_curtainl = BilbyCustomFunctions.OnePanelShiftValues(ws_corr, start_tube_number, current_tube_min_pixel_left, current_tube_min_pixel_right, sigma, height)
    if line_number == 1: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]

    if line_number == 2: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]

    if line_number == 3: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]
        
    if line_number == 4: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]

    if line_number == 5: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]

    if line_number == 6: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]
        
    if line_number == 7: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]

    if line_number == 8: # from the top
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]

    if line_number == 9: # from the top - very bad, weak tube
        tubes_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, -1]

############ END OF INPUT 2 ############
# Create 2D array of values for each stripe
# Record files    
    position_of_minimum_rearr, average_position_rearr, diff_position_of_minimum_rearr, sigma_values = OnePanelShiftValuesRearR_2024_test(ws_corr, start_tube_number, current_tube_min_pixel_left, current_tube_min_pixel_right, tubes_list, sigma, height)
    twoD_array_points.append(diff_position_of_minimum_rearr)
    #print(twoD_array_points)

    #BilbyCustomFunctions_memory.OutputFileFormatRecord(diff_position_of_minimum_rearr, path, out_filename, format)
    #BilbyCustomFunctions_memory.OutputFileFormatRecord(position_of_minimum_rearr, path, out_filename_minima, format) 
    OutputFileFormatRecord_2024(diff_position_of_minimum_rearr, out_filename, format)
    OutputFileFormatRecord_2024(position_of_minimum_rearr, out_filename_maximums, format)
    OutputFileFormatRecord_2024(sigma_values, out_sigma_values, format)  
#print(position_of_minimum_rearr) 

# Move rear right
############ INPUT 3(3) ############
stripe_to_align_to = 'average' # counting start from bottom, nine stripes in common  # 'average' is possible as well
# Fun starts here. It is upside down for the rear panel
############ END OF INPUT 3 ############

shifts_array = BilbyCustomFunctions_memory.CalculateShiftsArray(stripe_to_align_to, twoD_array_points)
BilbyCustomFunctions_memory.CorrectElementOneStripeRearRight('CurtainRight', pixelsize, shifts_array, ws_corr)


