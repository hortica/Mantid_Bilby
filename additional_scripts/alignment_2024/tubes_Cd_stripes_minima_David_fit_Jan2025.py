from mantid.simpleapi import *
from mantid.api import *
from mantid.api import ExperimentInfo
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt

import numpy as np
import os, csv

import david3 as david
import BilbyCustomFunctions_memory

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

#######################################################################################
#######################################################################################

def find_peak_david(initial_tube_min_pixel, initial_tube_max_pixel, array_y):

    peak_centre = []

    i = -1 # index count  
    for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels; -1 means tube is not considering
        i = i + 1
        #print('initial_tube_min_pixel, initial_tube_max_pixel ',initial_tube_min_pixel, initial_tube_max_pixel)
        
        startx = initial_tube_min_pixel + 256 * int(tube_number)
        endx = initial_tube_max_pixel + 256 * int(tube_number)           
        #print('startx, endx ', startx, endx )
        x = (range(startx, endx + 1))
        y = [2000 + (-1) * ws_corr.readY(n)[0] for n in range(startx, endx+1)]
       
    # sample
        x_sam = david.linspace(x[0], x[-1], num = 200)
        y_sam = david.sample(x, y, x_sam)
       
        # normalized cross-correlation
        y_cnv = david.normxcorr(y_sam, y_sam)
        x_cnv = david.linspace(x[0], x[-1], num=len(y_cnv))
        
        # maxima              
        maxima = david.localmaxima(x_cnv, y_cnv)
        maxima = [m for m in maxima if m[1] > 0.0]                          # ignore negative matches
        maxima = [m for m in maxima if david.sample(x, y, m[0]) >  30.0]    # only consider high y values
        maxima = sorted(maxima, key=lambda m: m[1], reverse=True)           # best fit first
           
        # get best result
        x_cnv_max, y_cnv_max, i_cnv_max = maxima[0]
        center = david.maximumX(x_cnv, y_cnv, i_cnv_max)
        peak_centre.append(center)

    return peak_centre

#######################################################################################
#######################################################################################
def OutputFileFormatRecord_2024(diff_position_of_minimum, out_filename, format): #input is a list, path and filename and format "rows" or "columns"
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
#######################################################################################
# Set-up files location and output files

# Cd lines file
Cd_test_file = 'BBY0073253_H2O_Cd_masks_open_curtains.tar' # Cd_test_file = '297_Cd_lines_setup2.tar' # BBY0001429_mask.tar

# Path and file name and the format of csv where shifst will be recorded
path = "W:/data/proposal/00113/2024-09-30_Sokolova_re_commissioning/AgBeh_paper_water_tests/stretch_test" # define before the function call
os.chdir(path)
print(os. getcwd())

format = "rows" # format values: "columns" or "rows"

#######################################################################################

# Load data
ws_sam = LoadBBY(Cd_test_file)
ws_corr = CloneWorkspace(ws_sam)         # Copy of the input workspace, to be shifted; created to be able to compare with the original one

period = float(ws_corr.run().getProperty("period").value) # Get T0 chopper period value
#binning_time = [0.0, period, period]
binning_time = [0.0, period, period]
ws_corr = Rebin(ws_corr, Params = binning_time, PreserveEvents = False) # Wavelength binning is not needed; it takes too long to convert the file

#######################################################################################
#######################################################################################

def create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right):
    # Auto correlation peak finding - David M.      
    peak_center = find_peak_david(current_tube_min_pixel_left, current_tube_min_pixel_right, ws_corr)

    relative_shifts_pixels = []
    for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
        relative_shifts_pixels.append (peak_center[tube_number] - 256.0 * tube_number)
        #pixel number for the minima on each tube if the numbering would start from the same value all the time  

    #this is an intermediate check for the tubes for which the minima suddenly went to far for whatever reason
    #this is comparison with the fist tube minima - random choice
    relative_shifts_delta_in_pixels_check_how_far = []
    for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
        relative_shifts_delta_in_pixels_check_how_far.append (relative_shifts_pixels[tube_number] - relative_shifts_pixels[5])   

    # need an average position of the minima to subtract for the relative shifts
    sum = 0.0
    i = 0
    for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels 
        if relative_shifts_delta_in_pixels_check_how_far[tube_number] < 4.0: #to exclude sudden off-sets
            i = i + 1
            sum = sum + relative_shifts_pixels[tube_number]  # average position of the minima
    average_position_minima_right_Cd_top = sum / i   

    relative_shifts_delta_in_pixels = []
    for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
        relative_shifts_delta_in_pixels.append (relative_shifts_pixels[tube_number] - average_position_minima_right_Cd_top)   
    
    return peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels
    
#######################################################################################
# Rear detector
#######################################################################################
# Rear Right panel - top Cd
out_filename_minima = "minima_positions_rear_right_Cd_top_stripe.csv"  #record only minima
current_tube_min_pixel_left = 51225 #41015 # depends on panel
current_tube_min_pixel_right = 51255 # 41045depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_rear_right_top = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_rear_right_top, out_filename_minima, format)

#######################################################################################
# Rear Right panel - bottom Cd
out_filename_minima = "minima_positions_rear_right_Cd_bottom_stripe_with_av.csv"  #record only minima
current_tube_min_pixel_left = 51360 #41015 # depends on panel
current_tube_min_pixel_right = 51385 # 41045depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_rear_right_bottom = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_rear_right_bottom, out_filename_minima, format)

# exotic step for Cd stripes: average top and bottom - rear left
average_rear_right_top_bottom = []
for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
    average_rear_right_top_bottom.append (0.5*(relative_shifts_delta_in_pixels_rear_right_top[tube_number] + relative_shifts_delta_in_pixels_rear_right_bottom[tube_number]))   
 
OutputFileFormatRecord_2024(average_rear_right_top_bottom, out_filename_minima, format)

#######################################################################################
# Rear Left panel - top Cd
out_filename_minima = "minima_positions_rear_left_Cd_top_stripe.csv"  #record only minima
current_tube_min_pixel_left = 41145 #41015 # depends on panel
current_tube_min_pixel_right = 41172 # 41045depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_rear_left_top = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_rear_left_top, out_filename_minima, format)

#######################################################################################
# Rear Left panel - bottom Cd
out_filename_minima = "minima_positions_rear_left_Cd_bottom_stripe_with_av.csv"  #record only minima
current_tube_min_pixel_left = 41015 #41015 # depends on panel
current_tube_min_pixel_right = 41041 # 41045depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_rear_left_bottom = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_rear_left_bottom, out_filename_minima, format)

# exotic step for Cd stripes: average top and bottom - rear left
average_rear_left_top_bottom = []
for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
    average_rear_left_top_bottom.append (0.5*(relative_shifts_delta_in_pixels_rear_left_top[tube_number] + relative_shifts_delta_in_pixels_rear_left_bottom[tube_number]))   
 
OutputFileFormatRecord_2024(average_rear_left_top_bottom, out_filename_minima, format)

#######################################################################################
# Top panel
#######################################################################################

# Top panel - right Cd
out_filename_minima = "minima_positions_top_Cd_right_stripe.csv"  #record only minima
current_tube_min_pixel_left = 20656 #41015 # depends on panel
current_tube_min_pixel_right = 20678 # 41045depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_top_right = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_top_right, out_filename_minima, format)

#######################################################################################

# Top panel - left Cd
out_filename_minima = "minima_positions_top_Cd_left_stripe_with_av.csv"  #record only minima
current_tube_min_pixel_left = 20451 #41015 # depends on panel
current_tube_min_pixel_right = 20520 # 41045depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_top_left = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_top_left, out_filename_minima, format)

# exotic step for Cd stripes: average left & right shifts - top panel
average_top_left_right = []
for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
    average_top_left_right.append (0.5*(relative_shifts_delta_in_pixels_top_right[tube_number] + relative_shifts_delta_in_pixels_top_left[tube_number]))   
 
OutputFileFormatRecord_2024(average_top_left_right, out_filename_minima, format)

#######################################################################################
# Bottom panel
#######################################################################################

# Bottom panel - right Cd
out_filename_minima = "minima_positions_bottom_Cd_right_stripe.csv"  #record only minima
current_tube_min_pixel_left = 30760 #41015 # depends on panel
current_tube_min_pixel_right = 30783 # 41045depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_bottom_right = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_bottom_right, out_filename_minima, format)

#######################################################################################

# Bottom panel - left Cd
out_filename_minima = "minima_positions_bottom_Cd_left_stripe_with_av.csv"  #record only minima
current_tube_min_pixel_left = 30895 # depends on panel
current_tube_min_pixel_right = 30920 # depends on panel

peak_center, relative_shifts_pixels, relative_shifts_delta_in_pixels_bottom_left = create_minima_list(out_filename_minima, current_tube_min_pixel_left, current_tube_min_pixel_right)

# Record file
OutputFileFormatRecord_2024(peak_center, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_pixels, out_filename_minima, format)
OutputFileFormatRecord_2024(relative_shifts_delta_in_pixels_bottom_left, out_filename_minima, format)

# exotic step for Cd stripes: average left & right shifts - bottom panel
average_bottom_left_right = []
for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
    average_bottom_left_right.append (0.5*(relative_shifts_delta_in_pixels_bottom_right[tube_number] + relative_shifts_delta_in_pixels_bottom_left[tube_number]))   
 
OutputFileFormatRecord_2024(average_bottom_left_right, out_filename_minima, format)

#######################################################################################
# End of a massive story #
#######################################################################################
