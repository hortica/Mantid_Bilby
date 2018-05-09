# History
# 2017 - 10 - 03
# updated writing into xml file (escape char, no "" in the final mask file)
# updated list for standard edges: inner 8-pack on the top curtain is working now

from mantid.api import DataProcessorAlgorithm, AlgorithmFactory
import math, os.path, csv
from pylab import *

#############################################################################
# User input start

# File needed to create the mask
file_input = FileFinder.getFullPath('BBY0015914.tar')

# 0 angle is along OX axis (from the middle of the detector to the right, looking along beam centreline)
# 90 angle is along OY axis, the vertical one 
# Area between angles will NOT be masked

# Start angle, in degrees, starting from the horizontal OX, from 0 to the right
phimin = 85.0
# End angle, in degrees, starting from the horizontal OX, from 0 to the right
phimax = 90.0         
#  if mirror chosen, the sector will be reflected around OX and OY
mirror = True

# in cm - axes of the ellipse to mask around center of the detector
ellipse_horiz_semi_axis_to_mask = 8.0
ellipse_vert_semi_axis_to_mask = 8.0

# Mask file name: to create
# Mask will be created in the same folder as your data
mask_file_name = "mask_test_tt.xml"

# User input end
#############################################################################

# paths
full_path_dir = os.path.dirname(file_input)
print full_path_dir
filename = full_path_dir + "/" + mask_file_name
print filename

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

xml_edges = [("0-16,241-272,497-528,753-784,1009-1040,1265-1296,1521-1552,1777-1808,2033-2064,2289-2320,2545-2576,2801-2832,3057-3088,3313-3344,3569-3600,3825-3856,4081-4112,4337-4368,4593-4624,4849-4880,5105-5136,5361-5392,5617-5648,5873-5904,6129-6160,6385-6416,6641-6672,6897-6928,7153-7184,7409-7440,7665-7696,7921-7951,8177-8207,8433-8463,8689-8719,8945-8975,9201-9231,9457-9487,9712-9743,9968-9999,10224-10252,10481-10508,10737-10764,10993-11020,11249-11276,11505-11532,11761-11788,12017-12044,12273-12300,12529-12812,13041-13068,13297-13324,13553-13580,13809-13836,14065-14092,14321-14348,14577-14604,14833-14860,15089-15116,15345-15372,15601-15628,15857-15884,16113-16140,16369-16396,16625-16908,17137-17164,17393-17421,17649-17677,17905-17933,18161-18189,18417-18445,18673-18701,18929-18957,19185-19213,19441-19469,19697-19725,19953-19981,20209-20237,20465-20494,20721-20750,20977-21006,21233-21262,21489-21518,21745-21774,22001-22030,22257-22286,22513-22542,22769-22798,23025-23054,23281-23310,23537-23566,23793-23822,24049-24078,24305-24334,24561-24590,24817-24846,25073-25102,25329-25358,25585-25614,25841-25870,26097-26126,26353-26382,26609-26638,26865-26894,27121-27150,27377-27406,27633-27662,27889-27918,28145-28174,28401-28430,28657-28686,28913-28942,29169-29198,29425-29454,29681-29710,29937-29966,30193-30222,30449-30478,30705-30735,30960-30991,31216-31248,31472-31504,31728-31760,31984-32016,32240-32272,32496-32528,32752-32784,33008-33040,33264-33296,33520-33552,33777-33808,34033-34064,34289-34320,34545-34576,34801-34832,35057-35088,35313-35344,35569-35600,35825-35856,36081-36112,36337-36368,36593-36624,36849-36880,37105-37136,37361-37392,37617-37648,37873-37904,38129-38160,38385-38416,38641-38672,38897-38928,39153-39184,39409-39440,39665-39696,39921-39952,40177-40208,40433-40464,40689-40720,40945-40979,41197-41235,41453-41491,41709-41747,41965-42003,42221-42259,42477-42515,42733-42771,42989-43027,43245-43283,43501-43539,43757-43795,44013-44051,44269-44307,44525-44563,44781-44819,45037-45075,45293-45331,45549-45587,45805-45843,46061-46099,46317-46355,46573-46611,46829-46867,47085-47123,47341-47379,47597-47635,47853-47891,48109-48147,48365-48403,48621-48659,48877-48915,49133-49171,49389-49427,49645-49683,49901-49939,50157-50195,50413-50451,50669-50707,50925-50963,51181-51219,51437-51475,51694-51731,51950-51987,52206-52243,52462-52499,52718-52755,52974-53011,53230-53267,53486-53523,53742-53779,53998-54035,54254-54291,54510-54547,54766-54803,55022-55059,55278-55315,55534-55571,55790-55827,56046-56083,56302-56339,56558-56595,56814-56851,57070-57107,57326-57363,57582-57619,57838-57875,58094-58131,58350-58387,58606-58643,58862-58899,59118-59155,59374-59411,59630-59667,59886-59923,60142-60179,60398-60435,60654-60691,60910-60947,61166-61203,61422-61439")]


#############################################################################
# record info into xml file
filename_path = filename # taken from User input, above

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





