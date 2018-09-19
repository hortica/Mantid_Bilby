## Data reduction instruction

- Two csv files, similar to ([`input_csv_example.csv`](/example_data_reduction_settings/input_csv_example.csv) and [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv)) shall be created during the experiment; the names can be different, the format (especially the top line in each) must stay the same

- download [Mantid](http://www.mantidproject.org/), install it; don't open it before the next step will be completed

- Script [`SANSDataProcessor.py`](/reduction_scripts_const/SANSDataProcessor.py) to be copied into folder where MantidInstall is installed: ...  \MantidInstall\plugins\python\algorithms\WorkflowAlgorithms

- Download scripts from [`reduction_scripts_const`](/reduction_scripts_const) 

* Two following scripts can be saved everywhere, but important thing is that the folder shall be on the path (added to "Mantid User Directories")
   * [`BilbyCustomFunctions_Reduction.py`](/reduction_scripts_const/BilbyCustomFunctions_Reduction.py)
   * [`shift_assembled.csv`](/reduction_scripts_const/shift_assembled.csv)

- Add the folder with your *.tar files AND two csv files ([`input_csv_example.csv`](/example_data_reduction_settings/input_csv_example.csv) and [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv)) on the path as well

- To keep it simple, one can put tar and csv files in one folder, but you can add as many folders on the paths as you want

- Open the script menu: open menu “View”, then “Script window”; alternalively just press F3

- Open the reducer script [`reducer_example.py`](/example_data_reduction_settings/reducer_example.py) (in the “Python Window” open file, just “Ctrl-O” or File -> Open), update [lines 15-27](/example_data_reduction_settings/reducer_example.py#L15-L27) accordingly

- Run the reducer, Execute -> Execute All in the Menu
  * All output 1D files will be saved in the folder you define in the [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv))