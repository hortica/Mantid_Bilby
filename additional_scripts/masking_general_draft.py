from mantid.api import *
from mantid.api import DataProcessorAlgorithm, AlgorithmFactory
import math, os.path, csv
from pylab import *

#############################################################################
#  ##################################################################################
# User input start

## Choice of detectors
detector = "all" # all, rear, curtains, lr_only, ud_only, left, right, top, bottom

# 0 angle is along OX axis (from the middle of the detector to the right, looking along beam centreline)
# 90 angle is along OY axis, the vertical one 
## Start angle, in degrees, starting from the horizontal OX, from 0 to the right
phimin = 350 # For any symmetry apart from P1, this angle shal be in the range [0, 180]; for P1 [0, 360] is allowed
## End angle, in degrees, starting from the horizontal OX, from 0 to the right
phimax = 20 # For any symmetry apart from P1, this angle shal be in the range [0, 180]; for P1 [0, 360] is allowed

##in cm - radius of area to mask around center of the detector - to cover the beamstop
ellipse_horiz_semi_axis_to_mask = 3.0
ellipse_vert_semi_axis_to_mask = 5.0

## annulus_sector with the angle values chosen above
annulus_sector = False  # True False
# inner and outer radii will be ignored if there is no need in the annulus sectors (i.e. False above)
inner_rad = 20.0 # in cm - radia  of the annulus, origin is a geometrical center of the detector
outer_rad = 25.0

##  Symmetry. Mirror is not possible for the annulus_sector
symmetry = "P1" # P1, mirror, mirror_OY, mirror_OX, P2, P4, P6  # if mirror chosen, the sector will be reflected around OX and OY

## File needed to create the mask - any file on the Mantid path, needed as an input detectors' map and useful for checking the outcome mask
file_input = "BBY0014343.tar"

## path and filename for xml file to be saved - this script cannot guess where to save the file
path_main = 'D:/Mantid/__my_scripts/masking/'
filename = "mask_test.xml" # Choose the name of mask file to be created

# User input end
#  ##################################################################################

# Check input for the angle, radii and symmetry ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if symmetry != "P1":
    if (phimin > 180.0) or (phimax > 180.0) or (phimax < phimin):
        print "For any symmetry apart form P1, angle must belong to the range from 0 to 180deg, and max angle cannot be smaller than min. "
        sys.exit()
else:
   if (phimin > 360.0) or (phimax > 360.0): # or (phimax < phimin):
       print "For P1 symmetry, angle values cannot exceed 360 deg"
       sys.exit()

if (phimin < 0.0) or (phimax < 0.0): # or (phimax < phimin):
    print "Angle values cannot be negative"
    sys.exit()       

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if not(annulus_sector):
    inner_rad = 0.0
    outer_rad = 100.0
else:
    if (symmetry == "mirror" or symmetry == "mirror_OY" or symmetry == "mirror_OX"):
        print "For the annulus_sector mode symmetry \"mirror\", \"mirror_OY\", \"mirror_OX\" is not applicable."
        sys.exit()        
if (inner_rad < 0.0) or (outer_rad > 100.0) or (outer_rad < inner_rad):
    print "Radii range is from 0cm to 100cm; outer radius cannot be smaller than the inner one"
    sys.exit()
       
if  (phimin == phimax):
    print "Are you sure that it is OK to have angles the same?" 
    sys.exit()
# End of the check input for the angle, radii and symmetry ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
# Print output ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print "Detectors ", detector
print "phimin, phimax", phimin, phimax
print "annulus_sector: ", annulus_sector
if (annulus_sector):
    print "inner_rad ", inner_rad, "cm"
    print "outer_rad ", outer_rad, "cm"   
print "symmetry ", symmetry
# End of print output ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
#############################################################################
# Main class. It shall be improved eventually - from programming point of view
#  ##################################################################################

class TestingStaff():

    phimin = None
    phimax = None
    radius_to_mask = None
    file_input = None
    
    def __init__(self, detector, phimin, phimax, ellipse_horiz_semi_axis_to_mask, ellipse_vert_semi_axis_to_mask, symmetry, annulus_sector, inner_rad, outer_rad, file_input, xml_line, xml_extra):
        
        self.detector = detector
        self.phimin = phimin
        self.phimax = phimax
        self.ellipse_horiz_semi_axis_to_mask = ellipse_horiz_semi_axis_to_mask
        self.ellipse_vert_semi_axis_to_mask = ellipse_vert_semi_axis_to_mask        
        self.symmetry = symmetry
        self.annulus_sector = annulus_sector
        self.inner_rad = inner_rad
        self.outer_rad = outer_rad
       
        self.file_input = ws_file_input
        self.xml_line = xml_line
        
    def do_something(self):
        
# detectors selection ======================================================================================
        detector_range_low = 0 # all detector by defaut
        detector_range_high = 61440
        xml_extra = []

        if self.detector == "rear":
            detector_range_low = 40960
            detector_range_high = 61440
            xml_extra = [("0-40959")]
        
        if self.detector == "curtains":
            detector_range_low = 0
            detector_range_high = 40960
            xml_extra = [("40960-61439")]
       
        if self.detector == "lr_only":
            detector_range_low = 0
            detector_range_high = 20480
            xml_extra = [("20480-61439")]
            
        if self.detector == "ud_only":
            detector_range_low = 20480
            detector_range_high = 40960
            xml_extra = [("0-20479, 40960-61439")]
            
        if self.detector == "left":
            detector_range_low = 0
            detector_range_high = 10240
            xml_extra = [("10240-61439")]

        if self.detector == "right":
            detector_range_low = 10240
            detector_range_high = 20480
            xml_extra = [("0-10240, 20480-61439")]
            
        if self.detector == "top":
            detector_range_low = 20480
            detector_range_high = 30720
            xml_extra = [("0-20479, 30720-61439")]

        if self.detector == "bottom":
            detector_range_low = 30720
            detector_range_high = 40960
            xml_extra = [("0-30720, 40960-61439")]            

        self.xml_extra = xml_extra
# detectors selection ends =================================================================================

        detector_to_mask = []
        C = 180.0/math.pi

        if (self.annulus_sector): # annulus_sector True
            for i in range(detector_range_low, detector_range_high):              # for rear only the range will be ...
                detector = ws_file_input.getDetector(i)
                if (self.symmetry == "P1"):
                    if (phimin < phimax):                    
                        if  ( ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) < (math.pow(self.inner_rad*0.01 ,2))  ) \
                               or ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) > (math.pow(self.outer_rad*0.01 ,2)) ) \
                               or ( not( (detector.getPhi()) * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) ) ) ):
                            detector_to_mask.append(i)
                    else:  # phimax < phimin, for example 350->10
                        if  ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) < (math.pow(self.inner_rad*0.01 ,2))  ) \
                               or ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) > (math.pow(self.outer_rad*0.01 ,2)) ) \
                               or ( ((detector.getPhi()) * C <= (180.0 - self.phimax) and (detector.getPhi())*C >= (180.0 - self.phimin) )):
                            detector_to_mask.append(i)
                elif (self.symmetry == "P2"):
                    if  ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) < (math.pow(self.inner_rad*0.01 ,2))  ) \
                        or ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) > (math.pow(self.outer_rad*0.01 ,2)) ) \
                        or ( not(detector.getPhi() * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )) \
                        and ( not((detector.getPhi()) * C <= ((-1)*self.phimin) and (detector.getPhi())*C >= ((-1)*self.phimax) ) ):
                      detector_to_mask.append(i)                            
                elif (self.symmetry == "P4"):
                    if  ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) < (math.pow(self.inner_rad*0.01 ,2))  ) \
                        or ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) > (math.pow(self.outer_rad*0.01 ,2)) ) \
                        or ( not(detector.getPhi() * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )) \
                        and ( not(detector.getPhi() * C <= (90.0 - self.phimin) and (detector.getPhi())*C >= (90.0 - self.phimax) )) \
                        and ( not((detector.getPhi()) * C <= (- self.phimin) and (detector.getPhi())*C >= (- self.phimax) )) \
                        and ( not((detector.getPhi()) * C <= (270.0 - self.phimin) and (detector.getPhi())*C >= (270.0 - self.phimax) ) )\
                        and ( not((detector.getPhi()) * C <= (-90.0 - self.phimin) and (detector.getPhi())*C >= (-90.0 - self.phimax) ) ):
                      detector_to_mask.append(i)
                elif (self.symmetry == "P6"):
                    if  ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) < (math.pow(self.inner_rad*0.01 ,2))  ) \
                        or ( (math.pow(detector.getPos()[0], 2) + (math.pow(detector.getPos()[1], 2))) > (math.pow(self.outer_rad*0.01 ,2)) ) \
                        or ( not(detector.getPhi() * C <= (180.0 - self.phimin - 60.0) and (detector.getPhi())*C >= (120.0 - self.phimax) )) \
                        and ( not(detector.getPhi() * C <= (180.0 - self.phimin - 120.0) and (detector.getPhi())*C >= (60.0 - self.phimax) )) \
                        and ( not(detector.getPhi() * C <= (180.0 - self.phimin - 180.0) and (detector.getPhi())*C >= (-self.phimax) )) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin - 240.0) and (detector.getPhi())*C >= (180.0 -  self.phimax - 240.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin - 300.0) and (detector.getPhi())*C >= (180.0 - self.phimax - 300.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin + 60.0) and (detector.getPhi())*C >= (180.0 - self.phimax + 60.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin + 120.0) and (detector.getPhi())*C >= (180.0 - self.phimax + 120.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) ) ):
                      detector_to_mask.append(i)
        else:  # annulus_sector False
            for i in range(detector_range_low, detector_range_high):
                detector = ws_file_input.getDetector(i)
                if (self.symmetry == "mirror"):
                    if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                       or ( not(detector.getPhi() * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )) \
                       and ( not((detector.getPhi()) * C >= (self.phimin) and (detector.getPhi())*C <= (self.phimax) ) ) \
                       and ( not((detector.getPhi()) * C >= (self.phimin - 180.0) and (detector.getPhi())*C <= (self.phimax - 180.0) ) )  \
                       and ( not((detector.getPhi()) * C <= ((-1)*self.phimin) and (detector.getPhi())*C >= ((-1)*self.phimax) ) ):
                     detector_to_mask.append(i)
                if (self.symmetry == "mirror_OY"):
                    if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                       or ( not(detector.getPhi() * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )) \
                       and ( not((detector.getPhi()) * C >= (self.phimin) and (detector.getPhi())*C <= (self.phimax) ) ):
                     detector_to_mask.append(i)                     
                if (self.symmetry == "mirror_OX"):
                    if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                       or ( not(detector.getPhi() * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )) \
                       and ( not((detector.getPhi()) * C >= (self.phimin - 180.0) and (detector.getPhi())*C <= (self.phimax - 180.0) ) ):
                     detector_to_mask.append(i)  
                elif (self.symmetry == "P1"):
                    if (phimin < phimax): 
                        if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                            or ( not((detector.getPhi()) * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )):
                            detector_to_mask.append(i)
                    else: # phimax < phimin, for example 350->10
                        if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                            or ( ((detector.getPhi()) * C <= (180.0 - self.phimax) and (detector.getPhi())*C >= (180.0 - self.phimin) )):
                            detector_to_mask.append(i)
                elif (self.symmetry == "P2"):
                    if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                        or ( not(detector.getPhi() * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )) \
                        and ( not((detector.getPhi()) * C <= ((-1)*self.phimin) and (detector.getPhi())*C >= ((-1)*self.phimax) ) ):
                        detector_to_mask.append(i)
                elif (self.symmetry == "P4"):
                    if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                       or ( not(detector.getPhi() * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) )) \
                       and ( not(detector.getPhi() * C <= (90.0 - self.phimin) and (detector.getPhi())*C >= (90.0 - self.phimax) )) \
                       and ( not((detector.getPhi()) * C <= (- self.phimin) and (detector.getPhi())*C >= (- self.phimax) )) \
                       and ( not((detector.getPhi()) * C <= (270.0 - self.phimin) and (detector.getPhi())*C >= (270.0 - self.phimax) ) )\
                       and ( not((detector.getPhi()) * C <= (-90.0 - self.phimin) and (detector.getPhi())*C >= (-90.0 - self.phimax) ) ):
                       detector_to_mask.append(i)
                elif (self.symmetry == "P6"):
                    if  ((math.pow(detector.getPos()[0], 2)/ (math.pow(self.ellipse_horiz_semi_axis_to_mask*0.01 ,2)) + (math.pow(detector.getPos()[1], 2)/ math.pow(self.ellipse_vert_semi_axis_to_mask*0.01, 2))) <= 1.0) \
                        or ( not(detector.getPhi() * C <= (180.0 - self.phimin - 60.0) and (detector.getPhi())*C >= (120.0 - self.phimax) )) \
                        and ( not(detector.getPhi() * C <= (180.0 - self.phimin - 120.0) and (detector.getPhi())*C >= (60.0 - self.phimax) )) \
                        and ( not(detector.getPhi() * C <= (180.0 - self.phimin - 180.0) and (detector.getPhi())*C >= (-self.phimax) )) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin - 240.0) and (detector.getPhi())*C >= (180.0 -  self.phimax - 240.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin - 300.0) and (detector.getPhi())*C >= (180.0 - self.phimax - 300.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin + 60.0) and (detector.getPhi())*C >= (180.0 - self.phimax + 60.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin + 120.0) and (detector.getPhi())*C >= (180.0 - self.phimax + 120.0) ) ) \
                        and ( not((detector.getPhi()) * C <= (180.0 - self.phimin) and (detector.getPhi())*C >= (180.0 - self.phimax) ) ):
                     detector_to_mask.append(i) 
        # output
        self.xml_line = detector_to_mask
        return self.xml_line, self.xml_extra
# End of the main class

#############################################################################

#############################################################################
# initialisation

ws_file_input = LoadBBY(file_input) # load input file

xml_line = [] # initiate output array
xml_extra = []
settings = TestingStaff(detector, phimin, phimax, ellipse_horiz_semi_axis_to_mask, ellipse_vert_semi_axis_to_mask, symmetry, annulus_sector, inner_rad, outer_rad, ws_file_input, xml_line, xml_extra) # initiate input for the class
xml_line, xml_extra = settings.do_something() # execute method inside the class

##############################################################################
#  Clamsy way to record xml file; there is no care that it is an xml; there are known lines to be in the file, so they are just being dumped there
xml_line_1 = ['<?xml version="1.0"?>', '<detector-masking>', '<group>', '<detids>']
xml_line_2 = ['</detids>', '</group>', '</detector-masking>']

xml_edges = [("0-14,245-270,501-526,757-782,1013-1038,1269-1294,1525-1550,1781-1806,2037-2062,2293-2318,2549-2574,2805-2830,\
              3061-3086,3317-3342,3573-3598,3829-3854,4085-4110,4341-4366,4597-4622,4853-4878,5109-5134,5365-5390,5621-5646,\
              5877-5902,6133-6158,6389-6414,6645-6670,6901-6926,7157-7182,7413-7438,7669-7694,7925-7950,8181-8206,8437-8462,\
              8693-8718,8949-8974,9205-9230,9461-9486,9717-9742,9973-9998,10229-10253,10484-10509,10740-10765,10996-11021,\
              11252-11277,11508-11533,11764-11789,12020-12045,12276-12301,12532-12813,13044-13069,13300-13325,13556-13581,\
              13812-13837,14068-14093,14324-14349,14580-14605,14836-14861,15092-15117,15348-15373,15604-15629,15860-15885,\
              16116-16141,16372-16397,16628-16909,17140-17165,17396-17421,17652-17677,17908-17933,18164-18189,18420-18445,\
              18676-18701,18932-18957,19188-19213,19444-19469,19700-19725,19956-19981,20212-20237,20468-20502,20721-20758,\
              20977-21014,21233-21270,21489-21526,21745-21782,22001-22038,22257-22294,22513-22550,22769-22806,23025-23062,\
              23281-23318,23537-23574,23793-23830,24049-24086,24305-24342,24561-24598,24817-24854,25073-25110,25329-25366,\
              25585-25622,25841-25878,26097-26134,26353-26390,26609-26646,26865-26902,27121-27158,27377-27415,27633-27671,\
              27889-27927,28145-28183,28401-28439,28657-28695,28913-28951,29169-29207,29425-29463,29681-29719,29937-29975,\
              30193-30231,30449-30487,30705-30739,30955-30995,31211-31251,31467-31507,31723-31763,31979-32019,32235-32275,\
              32491-32531,32747-32787,33003-33043,33259-33299,33515-33555,33771-33811,34027-34067,34283-34323,34539-34579,\
              34795-34835,35051-35091,35307-35347,35563-35603,35819-35859,36075-36115,36331-36371,36587-36627,36843-36883,\
              37099-37139,37355-37395,37611-37651,37867-37907,38123-38163,38379-38419,38635-38675,38891-38931,39147-39187,\
              39403-39443,39659-39699,39915-39955,40171-40211,40427-40467,40683-40723,40939-40976,41201-41232,41457-41488,\
              41713-41744,41969-42000,42225-42256,42481-42512,42737-42768,42993-43024,43249-43280,43505-43536,43761-43792,\
              44017-44048,44273-44304,44529-44560,44785-44816,45041-45072,45297-45328,45553-45584,45809-45840,46065-46096,\
              46321-46352,46577-46608,46833-46864,47089-47120,47345-47376,47601-47632,47857-47888,48113-48144,48369-48400,\
              48625-48656,48881-48912,49137-49168,49393-49424,49649-49680,49905-49936,50161-50192,50417-50448,50673-50704,\
              50929-50960,51185-51215,51440-51471,51696-51727,51952-51983,52208-52239,52464-52495,52720-52751,52976-53007,\
              53232-53263,53488-53519,53744-53775,54000-54031,54256-54287,54512-54543,54768-54799,55024-55055,55280-55311,\
              55536-55567,55792-55823,56048-56079,56304-56335,56560-56591,56816-56847,57072-57103,57328-57359,57584-57615,\
              57840-57871,58096-58127,58352-58383,58608-58639,58864-58895,59120-59151,59376-59407,59632-59663,59888-59919,\
              60144-60175,60400-60431,60656-60687,60912-60943,61168-61199,61424-61439")]

#############################################################################
# record info into xml file
filename_path = os.path.join(os.path.expanduser(path_main), filename) # taken from User input, above

with open(filename_path, 'w') as f_ini: # mask file will be re-written, if existed
    wr = csv.writer(f_ini, delimiter='\n', lineterminator='\n',  quotechar="", quoting=csv.QUOTE_NONE)
    wr.writerow(xml_line_1) 
    wr = csv.writer(f_ini, delimiter=',', escapechar=' ',  quoting=csv.QUOTE_NONE)
    wr.writerow(xml_line + xml_edges + xml_extra) # main thing: list of detectors ID 
    #wr.writerow(xml_edges) # main thing: list of detectors ID    
    wr = csv.writer(f_ini, delimiter='\n', lineterminator='\n')
    wr.writerow(xml_line_2)
# finish recording: mask is ready
#############################################################################

#############################################################################
# Test: masking detectors

mask = filename_path
#print test_mask
ws_mask = LoadMask('Bilby', mask)
MaskDetectors(ws_file_input, MaskedWorkspace=ws_mask) 

print FileFinder.getFullPath(filename_path)