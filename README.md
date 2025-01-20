Instruction, scripts and test files for [BILBY SANS instrument](https://www.ansto.gov.au/user-access/instruments/neutron-scattering-instruments/bilby-small-angle-neutron-scattering) data reduction


### Data reduction instruction

[`DataReductionHelp`](/DataReductionHelp.md) is a detailed instruction of how to make Bilby data reduction working

### mantid_install_files_to_be_replaced
#### This folder contains scrips which have to be replaced in the folder where Mantid is installed; the plan is to update the main Mantid repo - once done, this step will not be needed
- [`SANSDataProcessor.py`](/mantid_install_files_to_be_replaced/BilbySANSDataProcessor.py) is the main script sitting in the following folder:[root]\MantidInstall\plugins\python\algorithms\WorkflowAlgorithms
- [`BilbyCustomFunctions_Reduction.py`](/mantid_install_files_to_be_replaced/BilbyCustomFunctions_Reduction.py) is a set of subroutines used for the Bilby data reduction
- [`BILBY_Parameters.xml`](/mantid_install_files_to_be_replaced/BILBY_Parameters.xml) Parameters file
- [`BILBY_Definition_Jan2025_summary.xml`](/mantid_install_files_to_be_replaced/BILBY_Definition_Jan2025_summary.xml) Bilby IDF file, valid from October 2024

### example_data_reduction_settings
#### This folder contains set of experimental files and files to be customised for every new data set
- set of experimental `*.tar` files
- [`input_csv_example.csv`](/example_data_reduction_settings/input_csv_example.csv) file is a formatted list of input data
- [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv) is a formatted list of data reduction setting
- [`reducer_example.py`](/example_data_reduction_settings/reducer_example.py) is a reducer file which shall be updated for each set of data; only a block between [lines 15-27](/example_data_reduction_settings/reducer_example.py#L15-L27) shall be updated indicating requested data reduction settings along with a set of the data files to be reduced
- `*mask*.xml`: transmission and scattering mask files
- [`1d_data`](/example_data_reduction_settings/1d_data) 1D standard output AgBh file
- [`standard_masks`](/example_data_reduction_settings/standard_masks) a set of masks for the last column option in the settings-input file, quodrants and six panels

### reduction_scripts_const
#### This folder contains those scripts used for Bilby data reduction which do not require adaptation for each user experiment
- [`shift_assembled.csv`](/reduction_scripts_const/shift_assembled.csv) and [`shift_assembled_Oct2024.csv`](/reduction_scripts_const/shift_assembled_Oct2024.csv) are the table which contains values for tube position correction, applicable for set-up before and after September 2024

### additional_scripts
#### Any other scripts to be used for Bilby data treatment
- set of working scripts to calculate total number of currents, flux, extract values from HDF files (for GumTree), masking, qmin_qmax estimation, transmissions etc.
##### subtraction
[`subtraction`](/additional_scripts/subtraction) contains set of scripts to prepare file for subtractions and execute it, and an example of usage
- [`create_subtraction_list.py`](/additional_scripts/subtraction/create_subtraction_list.py) creates the csv list for the subtraction
- [`subtraction.py`](/additional_scripts/subtraction/subtraction.py) performs 1D subtraction using cvs file written by a standard described in [`create_subtraction_list.py`](/additional_scripts/subtraction/create_subtraction_list.py)
- [`subtraction_2D.py`](/additional_scripts/subtraction/subtraction_2D.py) performs 2D subtraction using cvs file written by a standard described in [`create_subtraction_list.py`](/additional_scripts/subtraction/create_subtraction_list.py)
[`alignment_2024`](/additional_scripts/alignment_2024) contains set of scripts updated in 2024 to assess alignment of the detectors using flood measurements using masks and Cd stripes; very specific, applicable only to certain types of data (which panel/mask/stripe are considered)

##### other scripts
- [`control_flux_sums.py`](/additional_scripts/control_flux_sums.py) calculates flux for the transmision measurements, using cvs list as an input
- [`sector_masking.py`](/additional_scripts/sector_masking.py) creates a sector mask
- [`transmission_estimation_T_sample_blocked_beam_out.py`](/additional_scripts/transmission_estimation_T_sample_blocked_beam_out.py) estimates ratio between scattered and transmitted neutrons using a transmission mask as an input
- [`transmission_fit.py`](/additional_scripts/transmission_fit.py) is a script to estimate using [CalculateTransmission](http://docs.mantidproject.org/nightly/algorithms/CalculateTransmission-v1.html) transmission fitted with functions available in Mantid

##### commissioning_information
- [`control_flux_files_counts.xlsx`](/commissioning_information/control_flux_files_counts.xlsx) flux measurements results; updated periodically; more for storage / internal use