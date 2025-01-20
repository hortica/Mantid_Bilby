# import mantid algorithms, numpy and matplotlib
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np

from itertools import product
import numpy as np
import matplotlib.pyplot as plt
mtd.importAll() 

####################################################################################### 
# REDUCTION #######################################################################################
####################################################################################### 

#######################################################################################
def FilesListReduce (filename):
    parameters = []            
    with open(filename) as csv_file:
           reader = csv.DictReader(csv_file)
           for row in reader:
              if row['index'] == '':
                 continue 
              if row['index'] == 'END':
                  break
              parameters.append(row) 
    return parameters
    
#######################################################################################
#===============================================================
# Function to extract list of lines in the csv file to be processed; input format is a combination of digits, '-' ,',' or empty space
# returns list of numbers to be processed
def evaluate_files_list(numbers):
    expanded = []
    for number in numbers.split(","):
        if "-" in number:
            start, end = number.split("-")
            nrs = range(int(start), int(end) + 1)
            expanded.extend(nrs)
        else:
            expanded.append(int(number))
    return expanded
 
 #######################################################################################
def FilesToReduce(parameters, evaluate_files):
    files_to_reduce = [] 

    if len(evaluate_files) == 0:
        files_to_reduce.extend(parameters)
    else:
        evaluate_files_l = evaluate_files_list(evaluate_files) # call funciton for retrieve the IDs list
        for parameter in parameters:
            if int(parameter['index']) in evaluate_files_l:
               files_to_reduce.append(parameter)
           
    return files_to_reduce



####################################################################################### 
# GENERAL #########################################################################################
####################################################################################### 

def GetPixelSize():     # reads current IDF and get pixelsize from there
    from mantid.api import ExperimentInfo
    import xml.etree.ElementTree as ET

    currentIDF = ExperimentInfo.getInstrumentFilename("Bilby")
    #print currentIDF
    tree = ET.parse(currentIDF)
    for node in tree.iter():
        if node.tag=="{http://www.mantidproject.org/IDF/1.0}height":
            name = node.attrib.get('val')
    pixelsize = float(name)
  
    return pixelsize

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
def ReadCSV(filename):
    parameters = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            parameters.append(row) 
    return parameters

#######################################################################################
def OutputFileFormatRecord_2024(diff_position_of_minimum, out_filename, format): #input is a list, path and filename and format "rows" or "columns"

    #filename = os.path.join(path,out_filename) # make an input parameter - or make it an input for the writing function

    if not os.path.exists(filename):                                   # Nice one but written not by me, though after me spending ages learning about lists, columns, izip etc
        file = open(filename, 'w+')                                      # Used here after it got understood...  tempfile, None and "*" are new things here for me
        print ('no file')
        file.close()                                                                

    if format == "rows":
        # If output wants to be rows - simple and logical
        with open(filename, 'ab') as f_ini:
            wr = csv.writer(f_ini, delimiter=',', lineterminator='\n')
            wr.writerow(diff_position_of_minimum)    # will write everything in one row
            
    elif format == "columns":
        print (format)
        tmpfile = tempfile.TemporaryFile('r+')                        # If output wants to be columns
        with open(filename) as csvfile:
            nrOfCols = rowCnt = 0
            print (csvfile)
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
def CorrectionTubesShift(ws_to_correct, path_to_shifts_file):

    shifts = []
    shifts = ReadCSV(path_to_shifts_file)     # shall be precisely sevel lines; shifts for rear left, rear right, left, right, top, bottom curtains [calculated from 296_Cd_lines_setup1 file] + value for symmetrical shift for entire rear panels                                                                                              

    pixelsize = GetPixelSize()

    CorrectElementOneStripe("BackDetectorLeft", pixelsize, shifts[0], ws_to_correct)
    CorrectElementOneStripe("BackDetectorRight", pixelsize, shifts[1], ws_to_correct)
    CorrectElementOneStripe("CurtainLeft", pixelsize, shifts[2], ws_to_correct)
    CorrectElementOneStripe("CurtainRight", pixelsize, shifts[3], ws_to_correct)
    CorrectElementOneStripe("CurtainTop", pixelsize, shifts[4], ws_to_correct)
    CorrectElementOneStripe("CurtainBottom", pixelsize, shifts[5], ws_to_correct)
    MoveRearPanels (shifts[6][0], pixelsize, ws_to_correct)
    
    #MoveInstrumentComponent( ws_to_correct, 'BackDetectorLeft', Y=-0.0045, Z=0 ) # latest edition: to correct for extra shift, as found analysing position of the beam centre of the direct beam
    #MoveInstrumentComponent( ws_to_correct, 'BackDetectorRight', Y=-0.0045, Z=0 ) # see results in the file S:\Bragg\Bilby\Bilby_calculations_commissioning\Detectors\gravity__drop.xlsx
   
    return

####################################################################################### 
def DetShift_before2016 (ws):
    shift_curtainl = 0.74/1000
    shift_curtainr = 6.92/1000
    shift_curtainu = -7.50/1000
    shift_curtaind = -1.59/1000
    
    MoveInstrumentComponent(ws, 'CurtainLeft',    X = shift_curtainl, Y = 0 , Z = 0)
    MoveInstrumentComponent(ws, 'CurtainRight',  X = shift_curtainr, Y = 0 , Z = 0)
    MoveInstrumentComponent(ws, 'CurtainTop',      X = 0,  Y=shift_curtainu , Z = 0)
    MoveInstrumentComponent(ws, 'CurtainBottom', X = 0,   Y=shift_curtaind , Z = 0)

    return ws

####################################################################################### 
# FOR TUBE ADJUSTMENT ################################################################################
####################################################################################### 
def CalculateShiftsArray(stripe_to_align_to, twoD_array_points): # extracting line or calculation average (first variable, str, digit from 1 to 9 or "average") from the second variable, array

    sum_all_av = []
    
    if stripe_to_align_to == 'average':
        for i in range (len(twoD_array_points[0])):           # Length of strings is the same, since the array is rectangular
            sum = 0.0
            for j in range (0, len(twoD_array_points)):
                sum = sum + float(twoD_array_points[j][i])    # list of sum of each i-th elements in the input array
            sum_av = sum/float(len(twoD_array_points))    # list of averaged sum of each i-th elements in the input array 
            sum_all_av.append(sum_av)
        shifts_array = sum_all_av
    elif int(stripe_to_align_to) >= 1 and int(stripe_to_align_to) <= 9:  # stripe_to_align_to is a digit, from 1 to 9
        shifts_array = twoD_array_points[int(stripe_to_align_to)-1]        # taking only string with a given number, calculated from bottom
    else:
        print ("Wrong number of input strings chosen. Shall be either \"average\" or a digit in a range from 1 to 9.")
        sys.exit()    

    return shifts_array # returns a line of shifts of each tube in array of 40

#######################################################################################
def CorrectElementOneStripe (panel, pixelsize, shift, ws): # sutable for one Cd stripe correction and for the stripes on BorAl mask on left curtain

    eightpack = ['eight_pack1','eight_pack2','eight_pack3','eight_pack4','eight_pack5']
    tube = ['tube1','tube2','tube3','tube4','tube5','tube6','tube7','tube8']

    i = 0
    for ei_pack, t_tube in product(eightpack, tube):
        if (panel== "BackDetectorLeft" or panel== "CurtainLeft"):
            direction = 1.0
            MoveInstrumentComponent(ws, panel + '/' + ei_pack + '/' + t_tube,  X=0, Y=-float(shift[i])*pixelsize*direction, Z=0)                       
        if (panel== "BackDetectorRight" or panel== "CurtainRight"):
            direction = -1.0
            MoveInstrumentComponent(ws, panel + '/' + ei_pack + '/' + t_tube,  X=0, Y=-float(shift[i])*pixelsize*direction, Z=0)           
        if (panel== "CurtainBottom"):
            direction = 1.0
            MoveInstrumentComponent(ws, panel + '/' + ei_pack + '/' + t_tube,  X=-float(shift[i])*pixelsize*direction, Y=0, Z=0)                       
        if (panel== "CurtainTop"):
            direction = -1.0
            MoveInstrumentComponent(ws, panel + '/' + ei_pack + '/' + t_tube,  X=-float(shift[i])*pixelsize*direction, Y=0, Z=0)           
        i = i + 1
    return ws
    
#######################################################################################    
def CorrectElementOneStripeRearL (panel, pixelsize, shift, ws): # suitable for stipes on the BorAl mask on left panel, rear detector

    eightpack = ['eight_pack2','eight_pack3','eight_pack4','eight_pack5']
    tube = ['tube1','tube2','tube3','tube4','tube5','tube6','tube7','tube8']
    direction = 1.0
    
    i = 4 #3
    for ei_pack, t_tube in product(eightpack, tube):
        MoveInstrumentComponent(ws, panel + '/' + ei_pack + '/' + t_tube,  X=0, Y=-float(shift[i])*pixelsize*direction, Z=0)                       
        i = i + 1
    
    #i = 1, 2, 3, tubes 6, 7, 8 in eight_pack1 + i = 4
    MoveInstrumentComponent(ws, panel + '/' + 'eight_pack1' + '/' + 'tube5',  X=0, Y=-float(shift[0])*pixelsize*direction, Z=0)                       
    MoveInstrumentComponent(ws, panel + '/' + 'eight_pack1' + '/' + 'tube6',  X=0, Y=-float(shift[1])*pixelsize*direction, Z=0)                       
    MoveInstrumentComponent(ws, panel + '/' + 'eight_pack1' + '/' + 'tube7',  X=0, Y=-float(shift[2])*pixelsize*direction, Z=0)                       
    MoveInstrumentComponent(ws, panel + '/' + 'eight_pack1' + '/' + 'tube8',  X=0, Y=-float(shift[3])*pixelsize*direction, Z=0)                       

    return ws

#######################################################################################    
def CorrectElementOneStripeRearRight (panel, pixelsize, shift, ws): # suitable for stipes + diagonal on the BorAl mask on right panel, rear detector
                                                                                                        # takes a panel, pixelsize,  list of shift values for each tube and ws to work on
    eightpack = ['eight_pack1', 'eight_pack2','eight_pack3','eight_pack4','eight_pack5']
    tube = ['tube1','tube2','tube3','tube4','tube5','tube6','tube7','tube8']
    direction = -1.0
    
    i = 0
    for ei_pack, t_tube in product(eightpack, tube):
        MoveInstrumentComponent(ws, panel + '/' + ei_pack + '/' + t_tube,  X=0, Y=-float(shift[i])*pixelsize*direction, Z=0)                       
        i = i + 1

    return ws


#######################################################################################    
def CorrectElementOneStripeRearLeft (panel, pixelsize, shift, ws): # 2024
    
    tube = ['tube1','tube2','tube3','tube4','tube5','tube6','tube7','tube8']
    eightpack = ['eight_pack1', 'eight_pack2','eight_pack3','eight_pack4','eight_pack5']
    direction = 1.0 ##2024: left curtain & left rear are upside down
    
    i = 0
    for ei_pack, t_tube in product(eightpack, tube):
        MoveInstrumentComponent(ws, panel + '/' + ei_pack + '/' + t_tube,  X=0, Y=-float(shift[i])*pixelsize*direction, Z=0)                       
        i = i + 1

    return ws


#######################################################################################
def MoveRearPanels (shift, pixelsize, ws): # moves only rear left and rear right, each on shift; +1 to the right panel to make them symmetrical

    panel = "BackDetectorLeft"
    direction = 1.0
    MoveInstrumentComponent(ws, panel,  X=0, Y=-float(shift)*pixelsize*direction, Z=0)                       

    panel = "BackDetectorRight"
    direction = -1.0
    MoveInstrumentComponent(ws, panel,  X=0, Y=-float(shift)*pixelsize*direction, Z=0)      
    
    return ws


####################################################################################### 
def OnePanelShiftValues(ws_corr, start_tube_number, current_tube_min_pixel_left, current_tube_min_pixel_right, sigma, height): # calculates shift for each tube for a stripe of given location
# sutable for Cd stripes correction and lines for BorAl mask on the left curtain
# input: ws, tube to start with, range of pixels to look for a peak (in a range from 1 to 256), estimated sigma and height for Gaussian peak
# output: list of average_position for a peak on each tube and diff_position_of_minimum, difference between initial position and average


    x_left = current_tube_min_pixel_left - 256*(start_tube_number - 1) # depends on panel - but can be calculated from previous; x - is not an important information for users
    x_right = current_tube_min_pixel_right  - 256*(start_tube_number - 1) # depends on panel  # range of pixels the minimum sits in 41130-256*160 = 170

    position_of_minimum = []
    sum_position_of_minimum = 0.0

    for tube_number in range (0, 40):    # one panel is always 40 tubes and 256 pixels
        x1 = [n for n in range(x_left, x_right+1)]
        current_tube_min_pixel = current_tube_min_pixel_left + 256 * tube_number
        current_tube_max_pixel = current_tube_min_pixel_right + 256 * tube_number
        y1 = [ws_corr.readY(n)[0] for n in range(current_tube_min_pixel, current_tube_max_pixel+1)]
        current_tube_ws = Create_WS(x1, y1)  #create ws for each tube; needed because Mantid fit works only with ws
        name_current_tube = 'ws_tube' + str(start_tube_number + tube_number)    
        AnalysisDataService.addOrReplace(name_current_tube, current_tube_ws) # Only now can I see it print mtd.getObjectNames()
    
    # Setup the data to fit - the same for each tube, because x is always the same - just range of pixels inside those 256
    # Perhaps it is not very good to rely on previous knowledge, but the file with Cd is one of a kind, so everything in this script is very much customised for that

        startX = x_left
        endX = x_right

    # Setup the Gaussian, to fit to data
        tryCentre = str((x_left + x_right)/2) #'190'   # A start guess on peak centre
        myFunc = 'name=LinearBackground, A0=60.0; name=Gaussian, Height=' + height + ', PeakCentre=' + tryCentre + ', Sigma=' + sigma

        #fitStatus, chiSq, covarianceTable, paramTable, fitWorkspace = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX=endX, Output='fit', Function=myFunc)
        #2024
        fit_output = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX=endX, Output='fit', Function=myFunc)


    # print "The fit was: " + fitStatus
        #print("Fitted centre value is: %.2f" % paramTable.column(1)[3])
    #plot([fitWorkspace],  [0,1])# - WHY does not work from here ??? Which module shall be Included?
   
        #x_plot = fitWorkspace.extractX()
        #print x_plot[0]
        #y_plot = fitWorkspace.extractY()
        #print y_plot[0]
        #plt.plot(x_plot[0], y_plot[0])
   

    # Create list of the minima positions
        position_of_minimum.append(paramTable.column(1)[3])
        sum_position_of_minimum += float(position_of_minimum[tube_number])

    # Calculate averaged position
    average_position = sum_position_of_minimum/40.0 #position_of_minimum[5]

    sum_5 = 0.0
    for i in range(0, 5):
        sum_5 =+ position_of_minimum[i]-position_of_minimum[0]
    sum_5_av = sum_5/5
    print ("position_of_minimum[0]", position_of_minimum[0])
    sum_35 = 0.0
    for i in range(5, 40):
        sum_35 =+ position_of_minimum[i]-position_of_minimum[5]
    sum_35_av = sum_35/35
    diff = sum_35_av - sum_5_av
    print ("sum_5_av, sum_35_av, diff", sum_5_av, sum_35_av, diff)
    print ("position_of_minimum[5]", position_of_minimum[5])

    # Create array of differences, relative shift in pixels
    diff_position_of_minimum = []
    for pos_of_min in position_of_minimum: 
        diff_position_of_minimum.append("%4.3f" % float(pos_of_min - average_position))

    return position_of_minimum, average_position, diff_position_of_minimum
    

####################################################################################### 
# Shall be custom made for rear detectors, because first five tubes are invisible
def OnePanelShiftValuesRearL(ws_corr, start_tube_number, current_tube_min_pixel_left, current_tube_min_pixel_right, sigma, height):# calculates shift for each tube for a stripe of given location
# sutable for BorAl mask on the left rear panel, since not considering first five tubes
# input: ws, tube to start with, range of pixels to look for a peak (in a range from 1 to 256), estimated sigma and height for Gaussian peak
# output: list of positions of minimum, list of average_position for a peak on each tube and diff_position_of_minimum, difference between initial position and average

    x_left = current_tube_min_pixel_left - 256*(start_tube_number) # depends on panel - but can be calculated from previous; x - is not an important information for users
    x_right = current_tube_min_pixel_right  - 256*(start_tube_number) # depends on panel  # range of pixels the minimum sits in 41130-256*160 = 170
    position_of_minimum = []
    sum_position_of_minimum = 0.0

    for tube_number in range (0, 36):    # one panel is always 40 tubes and 256 pixels = no,, only 35 for the RearL; careful !!! where to start from # try 36, i.e. starting from 5th tube
        x1 = [n for n in range(x_left, x_right+1)]
        current_tube_min_pixel = current_tube_min_pixel_left + 256 * tube_number
        current_tube_max_pixel = current_tube_min_pixel_right + 256 * tube_number
        y1 = [ws_corr.readY(n)[0] for n in range(current_tube_min_pixel, current_tube_max_pixel+1)]
        current_tube_ws = Create_WS(x1, y1)  #create ws for each tube; needed because Mantid fit works only with ws
        name_current_tube = 'ws_tube' + str(start_tube_number + tube_number)    
        AnalysisDataService.addOrReplace(name_current_tube, current_tube_ws) # Only now can I see it print mtd.getObjectNames()

        startX = x_left
        endX = x_right

    # Setup the Gaussian, to fit to data
        tryCentre = str((x_left + x_right)/2) #'190'   # A start guess on peak centre
        myFunc = 'name=FlatBackground, A0=10.0; name=Gaussian, Height=' + height + ', PeakCentre=' + tryCentre + ', Sigma=' + sigma

        #fitStatus, chiSq, covarianceTable, paramTable, fitWorkspace = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX=endX, Output='fit', Function=myFunc)
        #2024
        fit_output = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX=endX, Output='fit', Function=myFunc)
        #plot([fitWorkspace],  [0,1])# - WHY does not work from here ??? Which module shall be Included?
        #print("Fitted centre value is: %.2f" % paramTable.column(1)[2])

    # Create list of the minima positions
        position_of_minimum.append(paramTable.column(1)[2])
        sum_position_of_minimum += float(position_of_minimum[tube_number])

    # Calculate averaged position
    average_position = position_of_minimum[0]  #sum_position_of_minimum/35.0
    print (average_position)
    # Create array of differences, relative shift in pixels
    diff_position_of_minimum = []
    for pos_of_min in position_of_minimum: 
        diff_position_of_minimum.append("%4.3f" % float(pos_of_min - average_position))

    return position_of_minimum, average_position, diff_position_of_minimum

####################################################################################### 

def OnePanelShiftValuesRearR_2024(ws_corr, start_tube_number, current_tube_min_pixel_left, current_tube_min_pixel_right, tubes_list, sigma, height):# calculates shift for each tube for a stripe of given location
# sutable for BorAl diagonal mask on the rear right panel
# Most advanced (i.e. flexible) one
# input: ws, tube to start with, range of pixels to look for a peak (in a range from 1 to 256), list of tubes to consider, estimated sigma and height for Gaussian peak
# Tubes out of consideration marked as -1 - in the main script. Custom made stuff.
# output: list of positions of minimum, list of average_position for a peak on each tube and diff_position_of_minimum, difference between initial position and average

    x_left = current_tube_min_pixel_left - 256*(start_tube_number-1) # depends on panel - but can be calculated from previous; x - is not an important information for users
    print('x_left ', x_left)
    
    x_right = current_tube_min_pixel_right  - 256*(start_tube_number-1) # depends on panel  # range of pixels the minimum sits in 41130-256*160 = 170
    print('x_right ', x_right)

    position_of_minimum = []
    sum_position_of_minimum = 0.0

    i = -1 # index count
    Ind_minus1 = 0 # count of -1 tubes
    
    for tube_number in tubes_list:    # one panel is always 40 tubes and 256 pixels; -1 means tube is not considering
        i = i + 1
        if not (tube_number == -1):
            x1 = [n for n in range(x_left, x_right+1)]
            current_tube_min_pixel = current_tube_min_pixel_left + 256 * int(tube_number)
            current_tube_max_pixel = current_tube_min_pixel_right + 256 * int(tube_number)
            y1 = [ws_corr.readY(n)[0] for n in range(current_tube_min_pixel, current_tube_max_pixel+1)]
            current_tube_ws = Create_WS(x1, y1)  #create ws for each tube; needed because Mantid fit works only with ws
            name_current_tube = 'ws_tube' + str(start_tube_number + tube_number)   
            AnalysisDataService.addOrReplace(name_current_tube, current_tube_ws) # Only now can I see it print mtd.getObjectNames()

            startX = x_left
            endX = x_right
            
            tryCentre = str((x_left + x_right)/2) #'190'   # A start guess on peak centre
            print(tryCentre)
            myFunc = 'name=FlatBackground, A0=10.0; name=Gaussian, Height=' + height + ', PeakCentre=' + tryCentre + ', Sigma=' + sigma

            #fitStatus, chiSq, covarianceTable, paramTable, fitWorkspace = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX = endX, Output='fit', Function=myFunc)
            #2024
            fit_output = Fit(InputWorkspace=current_tube_ws, WorkspaceIndex=0, StartX = startX, EndX = endX, Output='fit', Function=myFunc)

            #2024 add
            ParamTable = fit_output.OutputParameters  # table containing the optimal fit parameters
            fitWorkspace = fit_output.OutputWorkspace
            # ========================================            

            calc_position_of_gauss = paramTable.column(1)[2]
            print(calc_position_of_gauss)
            #print calc_position_of_gauss "%4.3f" %
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

    #DeleteWorkspace(name_current_tube)# - sort out how to get back to these WS
    #print name_current_tube, "deleted" #

    return position_of_minimum, average_position, diff_position_of_minimum

#######################################################################################
