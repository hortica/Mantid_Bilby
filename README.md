Scripts for [BILBY SANS instrument](http://www.ansto.gov.au/ResearchHub/OurInfrastructure/ACNS/Facilities/Instruments/Bilby/index.htm) data reduction and initial analysis

Repository content
------------------

### reduction_scripts_const
    #### This folder contains those scripts used for Bilby data reduction which do not require adaptation for each user experiment.
        -"SANSDataProcessor.py" is the main script sitting in the following folder:
        [root] \MantidInstall\plugins\python\algorithms\WorkflowAlgorithms

        -"shift_assembled.csv" is the table which contains values for tube position correction

        -"BilbyCustomFunctions_Reduction.py" is a set of subroutines used for the Bilby data reduction

### example_data_reduction_settings
    #### This folder contains set of experimental files and files to be customised for every new data set
        - set of experimental "*.tar" files
        
        - "input_csv*.csv" file is a formatted list of input data;
        
        - "mantid_reduction_background_6123.csv" is a formatted list of data reduction setting
        
        - "reducer_example.py" is a reducer file which shall be updated for each set 
        of data; Only a block between Lines 15-27 shall be updated indicating
        requested data reduction settings along with a set of the data files to be reduced
        
        - "*mask*.xml": masks files created for any separate data set

### additional_scripts
    #### Any other scripts to be used for Bilby data treatment
        - "transmission_fit_final.py" is a script to estimate transmission fitted
        with different functions

        - "transmission_estimation_T_sample_blocked_beam_out.py" is a script to check cnahces
        of the multiple scattering presence
