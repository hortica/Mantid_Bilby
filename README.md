Instruction, scripts and test files for [BILBY SANS instrument](https://www.ansto.gov.au/user-access/instruments/neutron-scattering-instruments/bilby-small-angle-neutron-scattering) data reduction


### Data reduction instruction

[`DataReductionHelp`](/DataReductionHelp.md) - a detailed instruction of how to make Bilby data reduction working

### example_data_reduction_settings
#### This folder contains set of experimental files and files to be customised for every new data set
- set of experimental `*.tar` files
- [`input_csv_example.csv`](/example_data_reduction_settings/input_csv_example.csv) file is a formatted list of input data
- [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv) is a formatted list of data reduction setting
-  [`reducer_example.py`](/example_data_reduction_settings/reducer_example.py) is a reducer file which shall be updated for each set of data; only a block between [lines 15-27](/example_data_reduction_settings/reducer_example.py#L15-L27) shall be updated indicating requested data reduction settings along with a set of the data files to be reduced
- `*mask*.xml`: transmission and scattering mask files made for any given data set
- [`1d_data`](/example_data_reduction_settings/1d_data) 1D standard output AgBh file

### reduction_scripts_const
#### This folder contains those scripts used for Bilby data reduction which do not require adaptation for each user experiment
- [`BilbyCustomFunctions_Reduction.py`](/reduction_scripts_const/BilbyCustomFunctions_Reduction.py) is a set of subroutines used for the Bilby data reduction
- [`SANSDataProcessor.py`](/reduction_scripts_const/SANSDataProcessor.py) is the main script sitting in the following folder:[root]\MantidInstall\plugins\python\algorithms\WorkflowAlgorithms
- [`shift_assembled.csv`](/reduction_scripts_const/shift_assembled.csv) is the table which contains values for tube position correction

### additional_scripts
#### Any other scripts to be used for Bilby data treatment

##### subtraction
[`subtraction`](/additional_scripts/subtraction) contains set of scripts to prepare file for subtractions and execute it
- [`create_subtraction_list.py`](/additional_scripts/subtraction/create_subtraction_list.py) creates the csv list for the subtraction
- [`subtraction.py`](/additional_scripts/subtraction/subtraction.py) performs subtraction using cvs file written by a standard described in [`create_subtraction_list.py`](/additional_scripts/subtraction/create_subtraction_list.py) creates the csv list for the subtraction

##### other scripts

- [`control_flux_sums.py`](/additional_scripts/control_flux_sums.py) calculates flux for the transmision measurements, using cvs list as an input
- [`sector_masking.py`](/additional_scripts/sector_masking.py) creates a sector mask
- [`transmission_estimation_T_sample_blocked_beam_out.py`](/additional_scripts/transmission_estimation_T_sample_blocked_beam_out.py) estimates ratio between scattered and transmitted neutrons using a transmission mask as an input
- [`transmission_fit.py`](/additional_scripts/transmission_fit.py) is a script to estimate using [CalculateTransmission](http://docs.mantidproject.org/nightly/algorithms/CalculateTransmission-v1.html) transmission fitted with functions available in Mantid