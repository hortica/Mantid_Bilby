Scripts for [BILBY SANS instrument](http://www.ansto.gov.au/ResearchHub/OurInfrastructure/ACNS/Facilities/Instruments/Bilby/index.htm) data reduction and initial analysis

### reduction_scripts_const
#### This folder contains those scripts used for Bilby data reduction which do not require adaptation for each user experiment
- [`SANSDataProcessor.py`](/reduction_scripts_const/SANSDataProcessor.py) is the main script sitting in the following folder:[root]\MantidInstall\plugins\python\algorithms\WorkflowAlgorithms
- [`shift_assembled.csv`](/reduction_scripts_const/shift_assembled.csv) is the table which contains values for tube position correction
- [`BilbyCustomFunctions_Reduction.py`](/reduction_scripts_const/BilbyCustomFunctions_Reduction.py) is a set of subroutines used for the Bilby data reduction

### example_data_reduction_settings
#### This folder contains set of experimental files and files to be customised for every new data set
- set of experimental `*.tar` files
- [`input_csv_example.csv`](/example_data_reduction_settings/input_csv_background_6123.csv) file is a formatted list of input data;
- [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_background_6123.csv) is a formatted list of data reduction setting
-  [`reducer_example.py`](/example_data_reduction_settings/reducer_example.py) is a reducer file which shall be updated for each set of data; only a block between [lines 15-27](/example_data_reduction_settings/reducer_example.py#L15-L27) shall be updated indicating requested data reduction settings along with a set of the data files to be reduced
- `*mask*.xml`: masks files created for any separate data set

### additional_scripts
#### Any other scripts to be used for Bilby data treatment

subtraction
create_subtraction_list.py
subtraction.py

control_flux_sums.py

mask_sector.py


- [`transmission_fit.py`](/additional_scripts/transmission_fit.py) is a script to estimate transmission fitted with functions available in Mantid
- [`transmission_estimation_T_sample_blocked_beam_out.py`](/additional_scripts/transmission_estimation_T_sample_blocked_beam_out.py) is a script to check chahces of the multiple scattering presence

