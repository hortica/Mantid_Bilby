# This script use 'mean' algorithm to average files
# The main option is to average all workspaces loaded to Mantid
# Line 21 explains how to average only the list of choice - the data shall be loaded already
# To load and avetrage, comment out lines 17, 20, 22, 26 and 27 and uncomment block between lines 30 and 77

from mantid.simpleapi import *
from mantid.api import AnalysisDataService as ADS

# Set the path for the output files
path_data = 'D:/Mantid_Bilby/additional_scripts/mean_testing/'
chosen_name = 'test_mean_2.dat'
output_name = path_data + chosen_name

#==================================================================================
# average all workspaces loaded in Mantid

Workspaces_list_load= (ADS.getObjectNames())  # getting list of everything

# A bit of a warning - to show how many files were averaged
print('You are about to average ', len(Workspaces_list_load), ' following workspaces:')

Workspaces_list = (', '.join(Workspaces_list_load))
# Comment out previous line and uncomment the following to do manually - but these shall be already loaded:
# Workspaces_list = 'BBY0078254_3.0_19.0_70D2O-30H2O, BBY0078255_3.0_19.0_78D2O-22H2O, BBY0078256_3.0_19.0_83D2O-17H2O, BBY0078252_3.0_19.0_8D2O-92H2O'

print(Workspaces_list)
Mean(Workspaces = Workspaces_list, OutputWorkspace = chosen_name) # Mean does not understand the list without ''; takes only fist argument


#==================================================================================
# another way - if the workspaces (files) to be loaded by this script

#file1 = 'BBY0078254_3.0_19.0_70D2O-30H2O.dat'
#file2 = 'BBY0078255_3.0_19.0_78D2O-22H2O.dat'
#file3 = 'BBY0078256_3.0_19.0_83D2O-17H2O.dat'
#file4 = 'BBY0078252_3.0_19.0_8D2O-92H2O.dat'

#ws_file1 = LoadAscii(file1, Unit = "MomentumTransfer")
#ws_file2 = LoadAscii(file2, Unit = "MomentumTransfer")
#ws_file3 = LoadAscii(file3, Unit = "MomentumTransfer")
#ws_file4 = LoadAscii(file4, Unit = "MomentumTransfer")

#Workspaces_list = 'ws_file1, ws_file2, ws_file3, ws_file4'

#Mean(Workspaces = Workspaces_list, OutputWorkspace = chosen_name)

#==================================================================================


# Save mean file - four columns
SaveAscii(InputWorkspace = chosen_name, Filename = output_name, WriteXError = True,  Separator = 'CSV') #saving file

# Check file exists
LoadAscii(output_name, Unit = "MomentumTransfer", OutputWorkspace = chosen_name[0:(len(chosen_name.strip())-4)] + '_loaded_back')
print ("File saved", FileFinder.getFullPath(chosen_name))
