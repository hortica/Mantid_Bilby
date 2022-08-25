# 2018-06-26 Include reactor power and cold source temp
# 2021-07-21: Remove bug with opening output file; add checks if the parameter is presented in the file

__script__.title = 'BBY Overview'
__script__.version = '2019-12-10 include HM2 magnet'

# Use inout: full path to the output file
__FOLDER_PATH__ = 'U:/data/proposal/07998/'

#if not os.path.exists(__FOLDER_PATH__):
#    os.makedirs(__FOLDER_PATH__)


# Setup the window panel
####################################################################################

# First block Sample
SampleName_tick = Par('bool', True)
SampleName_tick.title = 'Sample Name'
SamplePosition_tick = Par('bool', True)
SamplePosition_tick.title = '    Sample Position'

g0 = Group('Sample')
g0.numColumns = 6
g0.add(SampleName_tick,SamplePosition_tick)

# Second block Measurement
StartTime_tick = Par('bool', True)
StartTime_tick.title = '   StartTime'
EndTime_tick = Par('bool', True)
EndTime_tick.title = '   EndTime'

RunTime_tick = Par('bool', True)
RunTime_tick.title = '   Runtime'
TotalCounts_tick = Par('bool', True)
TotalCounts_tick.title = '   Total Counts'
Att_tick = Par('bool', True)
Att_tick.title = 'Attenuator'
SampleAperture_tick = Par('bool', False)
SampleAperture_tick.title = 'SampleAperture'

g0 = Group('Measurement')
g0.numColumns = 3
g0.add(StartTime_tick, EndTime_tick, RunTime_tick, TotalCounts_tick, Att_tick, SampleAperture_tick)

# Third block Detector Settings
L1_tick = Par('bool', False)
L1_tick.title = '  L1'
L2det_tick = Par('bool', False)
L2det_tick.title = '  L2 rear'
L2curtainLR_tick = Par('bool', False)
L2curtainLR_tick.title = '  L2 curtain LR'
L2curtainUD_tick = Par('bool', False)
L2curtainUD_tick.title = '  L2 curtain UD'
curtainL_tick = Par('bool', False)
curtainL_tick.title = '  curtainL'
curtainR_tick = Par('bool', False)
curtainR_tick.title = '  curtainR'
curtainU_tick = Par('bool', False)
curtainU_tick.title = '  curtainU'
curtainD_tick = Par('bool', False)
curtainD_tick.title = '  curtainD'

g0 = Group('Detector Settings')
g0.numColumns = 4
g0.add(L1_tick, L2det_tick, L2curtainLR_tick, L2curtainUD_tick, curtainL_tick, curtainR_tick, curtainU_tick, curtainD_tick)

# Fourth block Chopper Settings
MasterChopper1_tick = Par('bool', False)
MasterChopper1_tick.title = '  Master chopper 1'
MasterChopper2_tick = Par('bool', False)
MasterChopper2_tick.title = '  Master chopper 2'
MasterChopperFreq_tick = Par('bool', False)
MasterChopperFreq_tick.title = '  Master chopper Freq'
T0Chopper_tick = Par('bool', False)
T0Chopper_tick.title = '  T0 chopper'
T0ChopperFreq_tick = Par('bool', False)
T0ChopperFreq_tick.title = '  T0 chopper Freq'
T0ChopperPhase_tick = Par('bool', False)
T0ChopperPhase_tick.title = '  T0 chopper Phase'

velsel_lambda_tick = Par('bool', False)
velsel_lambda_tick.title = '  Lambda' 

g0 = Group('Chopper Settings')
g0.numColumns = 3
g0.add(MasterChopper1_tick, MasterChopper2_tick, MasterChopperFreq_tick,\
       T0Chopper_tick, T0ChopperFreq_tick, T0ChopperPhase_tick,velsel_lambda_tick)

# Fifth block Temperature tc1, tc2, tc3
Temp_tc1_12Peltier_setpoint_tick = Par('bool', False)
Temp_tc1_12Peltier_setpoint_tick.title = '  Temp_tc1_12Peltier_setpoint'
Temp_tc1_12Peltier_sensor_tick = Par('bool', False)
Temp_tc1_12Peltier_sensor_tick.title = '  Temp_tc1_12Peltier_sensor'

Temp_tc2_setpoint_tick = Par('bool', False)
Temp_tc2_setpoint_tick.title = '  Temp_tc2_SP'
Temp_tc2_VTE_tick = Par('bool', False)
Temp_tc2_VTE_tick.title = '  Temp_tc2_VTE'
Temp_tc2_VTI_tick = Par('bool', False)
Temp_tc2_VTI_tick.title = '  Temp_tc2_VTI'


Temp_tc3_LakeshoreC_tick = Par('bool', False)
Temp_tc3_LakeshoreC_tick.title = '  Temp_tc3_LS_C'
Temp_tc3_LakeshoreD_tick = Par('bool', False)
Temp_tc3_LakeshoreD_tick.title = '  Temp_tc3_LS_D'

g0 = Group('Temperature tc1,tc2,tc3')
g0.numColumns = 2
g0.add(Temp_tc1_12Peltier_setpoint_tick,Temp_tc1_12Peltier_sensor_tick,\
       Temp_tc3_LakeshoreC_tick,Temp_tc3_LakeshoreD_tick,\
       Temp_tc2_setpoint_tick,Temp_tc2_VTE_tick,Temp_tc2_VTI_tick)

# Sixth block magnet/cryostat settings for HM2
Sample_temp_tick = Par('bool', False) # old data format
Sample_temp_tick.title = '  SampleTemp, K'
Magnetic_field_tick = Par('bool', False) # old data format
Magnetic_field_tick.title = '  MagneticField, T'

g0 = Group('HM2 settings')
g0.numColumns = 3
g0.add(Sample_temp_tick, Magnetic_field_tick)

# Seventh block Reactor
Reactor_power_tick = Par('bool', False) # old data format
Reactor_power_tick.title = '  ReactorPower, K'
ColdSourceTemp_tick = Par('bool', False) # old data format
ColdSourceTemp_tick.title = '  ColdSourceTemp'

g0 = Group('Reactor')
g0.numColumns = 3
g0.add(Reactor_power_tick, ColdSourceTemp_tick)

# Eighth block Show/Export

export_tick = Par('bool', True)
export_tick.title = 'export'
exportfilename = Par('string', 'Overview_7998')
exportfilename.title = 'Filename'
'''
# will be added later
print_tick = Par('bool', True)
print_tick.title = 'print - not working yet'
'''
g0 = Group('Show/Export Parameters:')
g0.numColumns = 2
g0.add(export_tick, exportfilename) #, print_tick)

####################################################################################
def __run_script__(fns):
    # Use the provided resources, please don't remove.
    global Plot1
    global Plot2
    global Plot3 

    # check if a list of file names has been given
    if (fns is None or len(fns) == 0) :
        print 'no input datasets'
    else :
        pass

        i = 0 # so that header is only written once
              # careful here; if trying to get information for data from different proposals,
              # file will be recorded badly
        
        for fn in fns:
            # load dataset with each file name
            ds = df[fn]
            filename = os.path.basename(fn) # gets rid of the path
            filename = filename[:filename.find('.nx.hdf')] # gets rid of the hdf
            header = []
            data = []
            header.append('filename')
            data.append(filename)
            print 'filename ', filename
            
            if SampleName_tick.value:     #~~~~~~~~~~~~~~~~~~~~~   
                a = str(ds['entry1/sample/name'])
                if ((a == 'UNKNOWN') or (not(a))):
                    a = "none"
                    data.append(a)
                else:
                    data.append(a.replace(',' , '___'))
                header.append('SampleName')
                #print 'SampleName', a

            if SamplePosition_tick.value: #~~~~~~~~~~~~~~~~~~~~~ 
                a = str(ds['entry1/sample/samx'])
                # Value of 20 is a bit synthetic, taken from checking the array
                # In case of multiple entry it contains some meta information
                if (len(a)>20):
                    print 'samx', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%6.3f' %float(a)                      
                    #print 'samx', ' single entry', a
                data.append(a)
                header.append('SamplePosition')              

            if StartTime_tick.value:      #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/detector/daq_dirname'])
                a = a.replace('DAQ_','')
                a = a.replace('T',' ')
                data.append(a)
                header.append('Start Time')   

            if EndTime_tick.value:        #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/end_time'])
                data.append(a)
                header.append('End Time') 

            if RunTime_tick.value:        #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/detector/time'])
                # Value of 20 is a bit synthetic, taken from checking the array
                # In case of multiple entry it contains some meta information        
                # The same comment is applicable to all values below        
                if (len(a)>20):
                    print 'RunTime', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.2f' %float(a)
                    #print 'RunTime', ' single entry', a
                data.append(a)
                header.append('Run Time')
                
            if TotalCounts_tick.value:    #~~~~~~~~~~~~~~~~~~~~~ 
                a = str(ds['entry1/instrument/detector/total_counts'])
                if (len(a)>20):
                    print 'TotalCounts', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%12.2f' %float(a)
                    #print 'TotalCounts', ' single entry', a                
                data.append(a)
                header.append('Total Counts')

            if Att_tick.value:            #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/att_pos'])
                if (len(a)>20):
                    print 'Attenuator position', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%5.1f' %float(a)
                    #print 'Attenuator position', ' single entry', a                
                data.append(a)
                header.append('Attenuator')
                
            if SampleAperture_tick.value: #~~~~~~~~~~~~~~~~~~~~~  
                try:
                    a = str(ds['entry1/sample/sample_aperture'])
                    #print 'SampleAperture ', a
                except:
                    a = 'Nonsense but Sample Aperture is not in the file'
                    print 'Nonsense, but Sample Aperture is not in the file'
                data.append(a)
                header.append('Sample Aperture')              

            if L1_tick.value:              #~~~~~~~~~~~~~~~~~~~~~ 
                a = str(ds['entry1/instrument/L1'])
                if (len(a)>20):
                    print 'L1', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'L1', ' single entry', a                
                data.append(a)
                header.append('L1 [mm]')

            if L2det_tick.value:           #~~~~~~~~~~~~~~~~~~~~~ 
                a = str(ds['entry1/instrument/L2_det'])
                if (len(a)>20):
                    print 'L2_det', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'L2_det', ' single entry', a                
                data.append(a)
                header.append('L2 rear [mm]')                                

            if L2curtainLR_tick.value:     #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/L2_curtainr'])
                if (len(a)>20):
                    print 'L2_curtainr', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'L2_curtainr', ' single entry', a                      
                data.append(a)
                header.append('L2 curtain LR [mm]')

            if L2curtainUD_tick.value:     #~~~~~~~~~~~~~~~~~~~~~  
                a = str(ds['entry1/instrument/L2_curtainu'])
                if (len(a)>20):
                    print 'L2_curtainu', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'L2_curtainu', ' single entry', a               
                data.append(a)
                header.append('L2 curtain UD [mm]')

            if curtainL_tick.value:        #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/detector/curtainl'])
                if (len(a)>20):
                    print 'curtainl', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'curtainl', ' single entry', a       
                data.append(a)
                header.append('curtain L [mm]')

            if curtainR_tick.value:        #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/detector/curtainr'])
                if (len(a)>20):
                    print 'curtainR', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'curtainR', ' single entry', a                
                data.append(a)
                header.append('curtain R [mm]')                

            if curtainU_tick.value:        #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/detector/curtainu'])
                if (len(a)>20):
                    print 'curtainU', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'curtainU', ' single entry', a                
                data.append(a)
                header.append('curtain U [mm]')               

            if curtainD_tick.value:        #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/detector/curtaind'])
                if (len(a)>20):
                    print 'curtainD', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%8.3f' %float(a)
                    #print 'curtainD', ' single entry', a                
                data.append(a)
                header.append('curtain D [mm]')

            if MasterChopper1_tick.value:   #~~~~~~~~~~~~~~~~~~~~~ 
                try:
                    a = str(ds['entry1/instrument/master1_chopper_id'])
                except:
                    a = 'Choppers not in use'
                data.append(a)
                header.append('Master Chopper 1')                

            if MasterChopper2_tick.value:   #~~~~~~~~~~~~~~~~~~~~~
                try:   
                    a = str(ds['entry1/instrument/master2_chopper_id'])                
                except:
                    a = 'Choppers not in use'
                data.append(a)
                header.append('Master Chopper 2')
                    
            if MasterChopperFreq_tick.value: #~~~~~~~~~~~~~~~~~~~~~
                try:   
                    a = str(ds['entry1/instrument/master_chopper_freq'])
                    if (len(a)>20):
                        print 'master_chopper_freq', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%8.3f' %float(a)
                        #print 'master_chopper_freq', ' single entry', a                    
                except:
                    a = 'Choppers not in use'
                data.append(a)
                header.append('Master Chopper Freq [Hz]')             
      
            if T0Chopper_tick.value:         #~~~~~~~~~~~~~~~~~~~~~
                try:
                    a = str(ds['entry1/instrument/t0_chopper_id'])  # array
                    if (len(a)>20):
                        print 't0_chopper_id', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%8.3f' %float(a)
                        #print 't0_chopper_id', ' single entry', a                    
                except:
                    a = 'Choppers not in use'
                data.append(a)
                header.append('T0 Chopper ID')
                
            if T0ChopperFreq_tick.value:      #~~~~~~~~~~~~~~~~~~~~~
                try:   
                    a = str(ds['entry1/instrument/t0_chopper_freq'])
                    if (len(a)>20):
                        print 't0_chopper_freq', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%8.3f' %float(a)
                        #print 't0_chopper_freq', ' single entry', a                    
                except:
                    a = 'Choppers not in use'
                data.append(a)
                header.append('T0 Chopper Freq [Hz]')          

            if T0ChopperPhase_tick.value:     #~~~~~~~~~~~~~~~~~~~~~
                try:   
                    a = str(ds['entry1/instrument/t0_chopper_phase'])
                    if (len(a)>20):
                        print 't0_chopper_phase', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%8.3f' %float(a)
                        #print 't0_chopper_phase', ' single entry', a                    
                except:
                    a = 'Choppers not in use'
                data.append(a)
                header.append('T0 Chopper Phase')
            
            if velsel_lambda_tick.value:      #~~~~~~~~~~~~~~~~~~~~~
                try:   
                    a = str(ds['entry1/instrument/nvs067/lambda'])
                    if (len(a)>20):
                        print 'lambda', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %float(a)
                        #print 'lambda', ' single entry', a                    
                except:
                    a = 'Velocity selector not in use'
                data.append(a)
                header.append('NVS wavelength')
                
            if Temp_tc1_12Peltier_setpoint_tick.value: #~~~~~~~~~~~~~~~~~~~~~
                try: 
                    data.append(str(ds['entry1/sample/tc1/loop_12/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_11/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_10/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_09/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_08/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_07/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_06/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_05/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_04/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_03/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_02/setpoint']))
                    data.append(str(ds['entry1/sample/tc1/loop_01/setpoint']))
                except:
                    #print 'No temperature tc1 vSP data'
                    data.append('no loop_12/setpoint')
                    data.append('no loop_11/setpoint')
                    data.append('no loop_10/setpoint')
                    data.append('no loop_09/setpoint')
                    data.append('no loop_08/setpoint')
                    data.append('no loop_07/setpoint')
                    data.append('no loop_06/setpoint')
                    data.append('no loop_05/setpoint')
                    data.append('no loop_04/setpoint')
                    data.append('no loop_03/setpoint')
                    data.append('no loop_02/setpoint')
                    data.append('no loop_01/setpoint')
                    
                header.append('Temp tc1 BBY1')
                header.append('Temp tc1 BBY2')
                header.append('Temp tc1 BBY3')
                header.append('Temp tc1 BBY4')
                header.append('Temp tc1 BBY5')
                header.append('Temp tc1 BBY6')
                header.append('Temp tc1 BBY7')
                header.append('Temp tc1 BBY8')
                header.append('Temp tc1 BBY9')
                header.append('Temp tc1 BBY10')
                header.append('Temp tc1 BBY11')
                header.append('Temp tc1 BBY12')
            
            if Temp_tc1_12Peltier_sensor_tick.value:   #~~~~~~~~~~~~~~~~~~~~~
                try: 
                    data.append(str(ds['entry1/sample/tc1/loop_12/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_11/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_10/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_09/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_08/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_07/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_06/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_05/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_04/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_03/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_02/sensor']))
                    data.append(str(ds['entry1/sample/tc1/loop_01/sensor']))
                except:
                    #print 'No temperature tc1 vSP data'
                    data.append('no loop_12/sensor')
                    data.append('no loop_11/sensor')
                    data.append('no loop_10/sensor')
                    data.append('no loop_09/sensor')
                    data.append('no loop_08/sensor')
                    data.append('no loop_07/sensor')
                    data.append('no loop_06/sensor')
                    data.append('no loop_05/sensor')
                    data.append('no loop_04/sensor')
                    data.append('no loop_03/sensor')
                    data.append('no loop_02/sensor')
                    data.append('no loop_01/sensor')
 
                header.append('Temp tc1 BBY1 sensor')
                header.append('Temp tc1 BBY2 sensor')
                header.append('Temp tc1 BBY3 sensor')
                header.append('Temp tc1 BBY4 sensor')
                header.append('Temp tc1 BBY5 sensor')
                header.append('Temp tc1 BBY6 sensor')
                header.append('Temp tc1 BBY7 sensor')
                header.append('Temp tc1 BBY8 sensor')
                header.append('Temp tc1 BBY9 sensor')
                header.append('Temp tc1 BBY10 sensor')
                header.append('Temp tc1 BBY11 sensor')
                header.append('Temp tc1 BBY12 sensor')
            
            if Temp_tc2_setpoint_tick.value:      #~~~~~~~~~~~~~~~~~~~~~ 
                try:  
                    a = str(ds['entry1/sample/tc2/Loop1/vSP'])
                    if (len(a)>20):
                        print 'vSP', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %float(a)
                        #print 'vSP', ' single entry', a
                except:
                    a = 'No tc2 vSP'
                data.append(a)
                header.append('Temp tc2 vSP')
                    
            if Temp_tc2_VTE_tick.value:           #~~~~~~~~~~~~~~~~~~~~~
                try:  
                    a = str(ds['entry1/sample/tc2/Loop1/vTE'])
                    if (len(a)>20):
                        print 'vTE', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %float(a)
                        #print 'vTE', ' single entry', a
                except:
                    a = 'No tc2 vTE data'
                data.append(a)
                header.append('Temp tc2 vTE')
                    
            if Temp_tc2_VTI_tick.value:           #~~~~~~~~~~~~~~~~~~~~~
                try:  
                    a = str(ds['entry1/sample/tc2/Loop1/vTI'])
                    if (len(a)>20):
                        print 'vTI', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %float(a)
                        #print 'vTI', ' single entry', a
                except:
                    a = 'No tc2 vTI data'
                data.append(a)
                header.append('Temp tc2 vTI')
                    
            if Temp_tc3_LakeshoreC_tick.value:    #~~~~~~~~~~~~~~~~~~~~~
                try:  
                    a = float(ds['entry1/sample/tc3/sensor/sensorValueC'])
                    if (len(a)>20):
                        print 'Temp tc3 Lakeshore C', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %(float(a) - 273.15)                
                        #print 'Temp tc3 Lakeshore C', ' single entry', a
                except:
                    a = 'No tc3 Lakeshore C'
                data.append(a)
                header.append('Temp tc3 Lakeshore C')
                    
            if Temp_tc3_LakeshoreD_tick.value:     #~~~~~~~~~~~~~~~~~~~~~
                try:  
                    a = float(ds['entry1/sample/tc3/sensor/sensorValueD'])
                    if (len(a)>20):
                        print 'Temp tc3 Lakeshore D', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %(float(a) - 273.15) 
                        #print 'Temp tc3 Lakeshore D', ' single entry', a
                except:
                    a = 'No tc3 Lakeshore D'
                data.append(a)
                header.append('Temp tc3 Lakeshore D')


            if Sample_temp_tick.value:             #~~~~~~~~~~~~~~~~~~~~~
                try:   
                    a = str(ds['entry1/sample/tc1/sensor/sensorValueB'])
                    # Careful here, sensor A or B is defined solely by the experiment set-up
                    if (len(a)>20):
                        print 'SampleTemp', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %float(a)
                        #print 'SampleTemp', ' single entry', a
                except:
                    a = 'HM2 magnet: no value for sample T'
                data.append(a)
                header.append('SampleTemp') 


            if Magnetic_field_tick.value:          #~~~~~~~~~~~~~~~~~~~~~
                try:   
                    a = str(ds['entry1/sample/ma1/magnet/setpoint'])
                    # Careful here; this is settings for HM-2 magnet; HM-3 has a bit different node
                    if (len(a)>20):
                        print 'MagneticField', ' multiple data, possibly ranscan'
                        a = 'run scan'
                    else:
                        a = '%5.2f' %float(a)
                        #print 'MagneticField', ' single entry', a                    
                except:
                    a = 'HM2 magnet: no value for the field'
                data.append(a)
                header.append('MagneticField')   # array
                  
            if Reactor_power_tick.value:            #~~~~~~~~~~~~~~~~~~~~~
                a = str(ds['entry1/instrument/source/power'])
                if (len(a)>20):
                    print 'ReactorPower', ' multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                   a = '%5.2f' %float(a)
                   #print 'ReactorPower', ' single entry', a
                data.append(a)
                header.append('ReactorPower')
                          
            if ColdSourceTemp_tick.value:          #~~~~~~~~~~~~~~~~~~~~~  
                a = str(ds['entry1/instrument/source/cns_out'])
                if (len(a)>20):
                    print 'ColdSourceTemp', 'multiple data, possibly ranscan'
                    a = 'run scan'
                else:
                    a = '%5.2f' %float(a)
                    #print 'ColdSourceTemp', 'single entry', a                
                data.append(a)
                header.append('ColdSourceTemp')      

# Recording header
            f = open(__FOLDER_PATH__ + str(exportfilename.value) + '.csv', 'a+')        
            if i == 0:
                for h in range(len(header)):                  
                    f.write(header[h])
                    f.write(',') 
                f.write('\n')
                #print 'header', header
            i = 1
            for h in range(len(data)):           
                f.write(data[h])
                f.write(',')
            f.write('\n')
            #print 'data', data
            f.close()
# File shall be closed by now, but for some reason sometimes system keeps it open
        
        print 'finished output ' + f.name               

def __dispose__():
    global Plot1
    global Plot2
    global Plot3
    #Plot1.clear()
    #Plot2.clear()
    #Plot3.clear()