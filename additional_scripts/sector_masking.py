from mantid.api import DataProcessorAlgorithm, AlgorithmFactory
import math, os.path, csv
from pylab import *

#############################################################################
# User input start

# 0 angle is along OX axis (from the middle of the detector to the right, looking along beam centreline)
# 90 angle is along OY axis, the vertical one 
# Area between angles will NOT be masked

# Start angle, in degrees, starting from the horizontal OX, from 0 to the right
phimin = 40
# End angle, in degrees, starting from the horizontal OX, from 0 to the right
phimax = 80             
# in cm - radius of area to mask around center of the detector
ellipse_horiz_semi_axis_to_mask = 15.0
ellipse_vert_semi_axis_to_mask = 15.0

#  if mirror chosen, the sector will be reflected around OX and OY
mirror = False

# File needed to create the mask
file_input = "BBY0014343.tar"

# path and filename for xml file to be saved
path_main = 'D:/_work/projects/____SANS_II/commissioning_data_reduction/Mantid/__my_scripts/masking/'
filename = "mask_test.xml"

# User input end
#############################################################################

#############################################################################
# quick check of input angles

print "phimin, phimax", phimin, phimax # to check - output
if (mirror): print "mirror image"
elif (not mirror):
    print "no mirror"
    
if  (phimin < 0 or phimin > 360.0 or phimax < 0.0 or phimax > 360.0):
    print "Check value of input angle" 
    print "Both, phimin and phimax", phimin, phimax, "shall belong to [0, 360]deg interval"     
    sys.exit()
    
if  (phimin > phimax):
    print "Check value of input angles; phimin cannot be larger than phimax" 
    sys.exit()    
    
if  (phimin == phimax):
    print "Are you sure that it is OK to have angles the same?" 
    sys.exit()        
#############################################################################

#############################################################################
# Main class. It shall be improved eventually - from programming point of view

class TestingStaff(Object):

    phimin = None
    phimax = None
    radius_to_mask = None
    file_input = None
    
    def __init__(self, phimin, phimax, ellipse_horiz_semi_axis_to_mask, ellipse_vert_semi_axis_to_mask, mirror, file_input, xml_line):
        
        self.phimin = phimin
        self.phimax = phimax
        self.ellipse_horiz_semi_axis_to_mask = ellipse_horiz_semi_axis_to_mask
        self.ellipse_vert_semi_axis_to_mask = ellipse_vert_semi_axis_to_mask        
        self.mirror = mirror
        self.file_input = ws_file_input
        self.xml_line = xml_line

    def do_something(self):
        detector_not_to_mask = []
        
        for i in range(0, 61440):
            detector = ws_file_input.getDetector(i)
            if (self.mirror):
                if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                   or ( not(detector.getPhi() * 180.0/math.pi <= (180.0 - self.phimin) and (detector.getPhi())*180.0/math.pi >= (180.0 - self.phimax) )) \
                   and ( not((detector.getPhi()) * 180.0/math.pi >= (self.phimin) and (detector.getPhi())*180.0/math.pi <= (self.phimax) ) ) \
                   and ( not((detector.getPhi()) * 180.0/math.pi >= (self.phimin - 180.0) and (detector.getPhi())*180.0/math.pi <= (self.phimax - 180.0) ) )  \
                   and ( not((detector.getPhi()) * 180.0/math.pi <= ((-1)*self.phimin) and (detector.getPhi())*180.0/math.pi >= ((-1)*self.phimax) ) ):        
                       detector_not_to_mask.append(i)
            if (not self.mirror):
                if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                  or ( not((detector.getPhi()) * 180.0/math.pi <= (180.0 - self.phimin) and (detector.getPhi())*180.0/math.pi >= (180.0 - self.phimax) )):
                      detector_not_to_mask.append(i)
        # output
        self.xml_line = detector_not_to_mask
        return self.xml_line

# End of the main class
#############################################################################

#############################################################################
# initialisation

ws_file_input = LoadBBY(file_input) # load input file

xml_line = [] # initiate output array
settings = TestingStaff(phimin, phimax, ellipse_horiz_semi_axis_to_mask, ellipse_vert_semi_axis_to_mask, mirror, ws_file_input, xml_line) # initiate input for the class
xml_line = settings.do_something() # execute method inside the class

##############################################################################
#  Clamsy way to record xml file; there is no care that it is an xml; there are known lines to be in the file, so they are just being dumped there
xml_line_1 = ['<?xml version="1.0"?>', '<detector-masking>', '<group>', '<detids>']
xml_line_2 = ['</detids>', '</group>', '</detector-masking>']

xml_edges = [("0-15,242-271,498-527,754-783,1010-1039,1266-1295,1522-1551,1778-1807,2034-2063,2290-2319,2546-2575,\
2802-2831,3058-3087,3314-3343,3570-3599,3826-3855,4082-4111,4338-4367,4594-4623,4850-4879,5106-5135,5362-5391,\
5618-5647,5874-5903,6130-6159,6386-6415,6642-6671,6898-6927,7154-7183,7410-7439,7666-7695,7922-7951,8178-8207,\
8434-8463,8690-8719,8946-8975,9202-9231,9458-9487,9714-9743,9970-9999,10226-10255,10481-10511,10737-10767,10993-11023,\
11249-11279,11505-11535,11761-11791,12017-12047,12273-12303,12529-12559,12785-12815,13041-13071,13297-13327,\
13553-13583,13809-13839,14065-14095,14321-14351,14577-14607,14833-14863,15089-15119,15345-15375,15601-15631,15857-15887,\
16113-16143,16369-16399,16625-16655,16881-16911,17137-17167,17393-17423,17649-17679,17905-17935,18161-18191,18417-18447,\
18673-18703,18929-18958,19185-19214,19441-19470,19697-19726,19953-19982,20209-20238,20465-22543,22768-22799,23024-23055,\
23280-23311,23536-23567,23792-23823,24048-24079,24304-24335,24560-24591,24816-24847,25071-25103,25327-25359,25583-25615,\
25839-25872,26095-26128,26351-26384,26607-26640,26863-26896,27119-27152,27375-27408,27631-27664,27887-27920,28143-28176,\
28399-28432,28655-28688,28911-28944,29167-29200,29423-29456,29679-29712,29935-29968,30191-30224,30446-30480,30702-30735,\
30961-30991,31217-31247,31473-31503,31729-31759,31985-32015,32241-32271,32497-32527,32753-32783,33009-33039,33265-33295,\
33521-33551,33777-33807,34033-34063,34289-34319,34545-34575,34801-34831,35057-35087,35313-35343,35569-35599,35824-35855,\
36080-36111,36336-36367,36592-36623,36848-36879,37104-37135,37360-37391,37616-37647,37872-37903,38128-38159,38384-38415,\
38640-38671,38896-38927,39152-39183,39408-39439,39664-39695,39920-39951,40176-40207,40432-40463,40688-40719,40944-40976,\
41198-41232,41454-41488,41710-41744,41966-42000,42222-42256,42478-42512,42734-42768,42990-43024,43246-43280,43502-43536,\
43758-43792,44014-44048,44270-44304,44526-44560,44782-44816,45038-45072,45294-45328,45550-45584,45806-45840,46062-46096,\
46318-46352,46574-46608,46830-46864,47086-47120,47342-47376,47598-47632,47854-47888,48110-48144,48366-48400,48622-48656,\
48878-48912,49134-49168,49390-49423,49646-49679,49902-49935,50158-50191,50414-50447,50670-50703,50926-50959,51182-51218,\
51440-51474,51696-51730,51952-51986,52208-52242,52464-52498,52720-52754,52976-53010,53232-53266,53488-53522,53743-53778,\
53999-54033,54255-54289,54511-54545,54767-54801,55023-55057,55279-55313,55535-55569,55791-55825,56047-56081,56303-56337,\
56559-56593,56815-56849,57071-57105,57327-57361,57583-57617,57839-57873,58095-58129,58351-58385,58607-58641,58863-58897,\
59119-59153,59375-59409,59631-59665,59887-59921,60143-60177,60399-60433,60655-60689,60911-60945,61167-61201,61423-61439")]


#############################################################################
# record info into xml file
filename_path = os.path.join(os.path.expanduser(path_main), filename) # taken from User input, above

with open(filename_path, 'wb') as f_ini: # mask file will be re-written, if existed
    wr = csv.writer(f_ini, delimiter='\n', lineterminator='\n',  quotechar="", quoting=csv.QUOTE_NONE)
    wr.writerow(xml_line_1) 
    wr = csv.writer(f_ini, delimiter=',', escapechar=' ',  quoting=csv.QUOTE_NONE)
    wr.writerow(xml_line + xml_edges) # main thing: list of detectors ID    
    wr = csv.writer(f_ini, delimiter='\n', lineterminator='\n')
    wr.writerow(xml_line_2)
# finish recording: mask is ready
#############################################################################

#############################################################################
# Test: masking detectors
# Not needed for making the mask

test_mask = filename
print test_mask
ws_mask_test = LoadMask('Bilby', test_mask)
MaskDetectors(ws_file_input, MaskedWorkspace=ws_mask_test) 





