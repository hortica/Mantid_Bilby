#07 January 2016
#23 October 2019

from mantid.simpleapi import *
from pymantidplot.qtiplot import plot
import numpy as np
import math

##add min separation for not shadowing curtains in space for given L2s

# Functions ====================================================================================
# Q-calculation - equation only
def q_value(wl, dist_x, L2_det):
   #calculates q for given L2, lambda and distance from the beam centreline
   return (4*np.pi/wl)*np.sin(0.5*np.arctan(dist_x / L2_det))

# Calculation of Q-range
def curtain_q(idc, n, dx, separation, L2_curtain):
    #2.81mm is the pixel size
    x1 = np.ones(n) + dx
    y1 = separation + 2.81/2 + 2.81*np.arange(0, n)
    ws_max = CreateWorkspace(OutputWorkspace='wl_max_'+idc, UnitX='Q', DataX=q_value(wl_max, y1[:], L2_curtain), DataY=x1)
    delta_step_wl_max = ws_max.readX(0)[1] - ws_max.readX(0)[0] 

    ws_min = CreateWorkspace(OutputWorkspace='wl_min_'+idc, UnitX='Q', DataX=q_value(wl_min, y1[:], L2_curtain), DataY=x1)
    delta_step_wl_min= ws_min.readX(0)[1] - ws_min.readX(0)[0] 
      
    return  ws_max, delta_step_wl_max, ws_min, delta_step_wl_min

#INPUT 
# wavelengths =================================================================================
wl_range = [6.0, 6.5]                # wavelength, Angstroms  

assymetry_expected_horizontal_only = False # Added to be sure that no gaps are appearing on the data when half of the curtains are masked off
assymetry_expected_vertical_only = False     # Added to be sure that no gaps are appearing on the data when half of the curtains are masked off
Bragg_edge_suspected = False                       # Added to be sure that no short wavelengths (<4.5A) are considered for the samples wiht the Bragg edge


#INPUT Geometry =============================================================================

source_aper = 40.00                    # source aperture diameter, in mm
sample_aper = 12.5                    #sample aperture diameter, in mm
L1 = 14764.0                                 # L1, source - sample distance, in mm

bs = 40.0                                   # beamstop radius, in mm
L2_det = 18000.1                    # sample - rear detector distance, in mm

#Curtains up & down
L2_curtain_ud = 3500                 # sample - curtain distance, in mm, assumed the same for top & bottom
separation_u = 200                    # distance from the last inner tube on a curtain to the beam center, in mm
separation_d = 200                 # distance from the last inner tube on a curtain to the beam center, in mm

#Curtains left & right
L2_curtain_lr = 1500                   # sample - curtain distance, in mm, assumed the same for left and right
separation_l = 140                       # distance from the last inner tube on a curtain to the beam center, in mm
separation_r = 350                       # distance from the last inner tube on a curtain to the beam center, in mm

# PROCESSING ==================================================================================
# Size of the direct beam spot  ======================================================================

direct_shadow = L2_det*source_aper/L1 + (L2_det + L1)*sample_aper/L1
direct_shadow_radius = direct_shadow/2
print ('Direct beam shadow radius is %5.2f' % direct_shadow_radius, 'mm')

# wavelength range ================================================================================
wl_min = wl_range[0]
if Bragg_edge_suspected:
    if (wl_min < 4.5 ):
        wl_min = 4.5
        print ('Min wavelength value has been changed from ', wl_range[0], 'to 4.5A because of the possible Bragg edge appearance.')

wl_max = wl_range[1]
print ('Q (1/Angstrom) values for wavelengths range from ', wl_range, 'Angstroms')

# Q calculations ===================================================================================
# REAR detector
print ('============ Rear detector ============')
#max_width  = math.sqrt((separation_u + panel_width) **2 + panel_width**2)
#print 'bs, direct_shadow, direct_shadow_radius'
#print bs, direct_shadow, direct_shadow_radius

if direct_shadow_radius >  bs: # if chosen bs is large, bigger than the shadow
   bs = direct_shadow_radius
   #print bs
   
n = 118.0 - math.floor(bs / 2.81) #118*2.81 ~= 331.6mm
nn = int(n)
separation_rear = bs

ws_max, delta_step_wl_max, ws_min, delta_step_wl_min = curtain_q('rear', nn, 0.0, separation_rear, L2_det)

#print mtd.getObjectNames()

print('Qmin for rear and Step for max wavelength: %5.4f %5.4f' % (ws_max.readX(0)[0], delta_step_wl_max))
print('Qmax for rear and Step for min wavelength: %5.4f %5.4f' % (ws_min.readX(0)[nn-1] , delta_step_wl_min))

#plot([ws_max,ws_min],  [0], color='green', hold='on')
#print l.numCurves()
#l.removeCurve(0)

#Plot section below needs cleaning up
g = plot([ws_max, ws_min],  0, type=Layer.Line) 
l = g.activeLayer()
l.setTitle('Q range for rear, top, bottom, left, right curtains')
l.showGrid()

#CURTAIN detector ================================================================================
n = 118 #330mm divided by 2.8mm pixel size

# -------------------------------------------------------------------------------------------------------------------------------------------------
if assymetry_expected_horizontal_only is False:
    print ('=================== Top Curtain ===================')

    ws_max, delta_step_wl_max, ws_min, delta_step_wl_min = curtain_q('curtain_u', n, 0.5, separation_u, L2_curtain_ud)

    print('Qmin for top curtain and Step for max wavelength: %5.4f %5.4f' % (ws_max.readX(0)[0], delta_step_wl_max))
    print('Qmax for top curtain and Step for min wavelength: %5.4f %5.4f' % (ws_min.readX(0)[n-1] , delta_step_wl_min))

    g1 = plot([ws_max,ws_min],  [0])
    g = mergePlots (g, g1)
    #c - how to make it work properly??

# -------------------------------------------------------------------------------------------------------------------------------------------------
    print ('================= Bottom Curtain ===================')

    ws_max, delta_step_wl_max, ws_min, delta_step_wl_min = curtain_q('curtain_d', n, 1.0, separation_d, L2_curtain_ud)

    print('Qmin for bottom curtain and Step for max wavelength: %5.4f %5.4f' % (ws_max.readX(0)[0], delta_step_wl_max))
    print('Qmax for bottom curtain and Step for min wavelength: %5.4f %5.4f' % (ws_min.readX(0)[n-1] , delta_step_wl_min))

    g1 = plot([ws_max,ws_min],  [0])
    g = mergePlots (g, g1)

# -------------------------------------------------------------------------------------------------------------------------------------------------
if assymetry_expected_vertical_only is False:
    print ('================= Left Curtain ===================')

    ws_max, delta_step_wl_max, ws_min, delta_step_wl_min = curtain_q('curtain_l', n, 1.5, separation_l, L2_curtain_lr)
    print('Qmin for left curtain and Step for max wavelength: %5.4f %5.4f' % (ws_max.readX(0)[0], delta_step_wl_max))

    print('Qmax for left curtain and Step for min wavelength: %5.4f %5.4f' % (ws_min.readX(0)[n-1] , delta_step_wl_min))

    g1 = plot([ws_max,ws_min],  [0])
    g = mergePlots (g, g1)

# -------------------------------------------------------------------------------------------------------------------------------------------------
    print ('================= Right Curtain ==================')

    ws_max, delta_step_wl_max, ws_min, delta_step_wl_min = curtain_q('curtain_r', n, 2.0, separation_r, L2_curtain_lr)

    print('Qmin for right curtain and Step for max wavelength: %5.4f %5.4f' % (ws_max.readX(0)[0], delta_step_wl_max))
    print('Qmax for right curtain and Step for min wavelength: %5.4f %5.4f' % (ws_min.readX(0)[n-1] , delta_step_wl_min))

    g1 = plot([ws_max,ws_min],  [0])
    g = mergePlots (g, g1)