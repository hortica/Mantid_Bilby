## Data reduction instruction

- Two csv files, similar to ([`input_csv_example.csv`](/example_data_reduction_settings/input_csv_example.csv) and [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv)) shall be created during the experiment; the names can be different, the format (especially the top line in each) must stay the same

- download [Mantid](http://www.mantidproject.org/), install it; don't open it before the next step will be completed;
For the Mac users, note to Click on the Mantid.app with the control key and select package contents; after that it will be come obvious where the *.py files should go
- Download files [`BilbyCustomFunctions_Reduction.py`](/reduction_scripts_const/BilbyCustomFunctions_Reduction.py) and  [`shift_assembled.csv`](/reduction_scripts_const/shift_assembled.csv) from [`reduction_scripts_const`](/reduction_scripts_const) 

- Copy (replace) [`BilbyCustomFunctions_Reduction.py`](/reduction_scripts_const/BilbyCustomFunctions_Reduction.py) into the folder where MantidInstall is installed: ...  \Mantid{Nightly}Install\scripts

	* Note: remove the file with the same name "BilbyCustomFunctions_Reduction" but extention ".pyc" from \Mantid{Nightly}Install\scripts

- File [`shift_assembled.csv`](/reduction_scripts_const/shift_assembled.csv) can be saved everywhere, but important thing is that the folder shall be on the path (added to “Mantid User Directories”)
   
- Add the folder with your *.tar files AND two csv files ([`input_csv_example.csv`](/example_data_reduction_settings/input_csv_example.csv) and [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv)) on the path (added to “Mantid User Directories”)
	* To keep it simple, one can put tar and csv files in one folder, but you can add as many folders on the paths as you want
- Version <=5: Open the Script menu in Mantid: press “View”, and then “Script window”; alternalively just press F3;
- Version 6 and higher: open Scripts in the Editor window.

- Open the reducer script [`reducer_example.py`](/example_data_reduction_settings/reducer_example.py) (in the “Python Window” open file, just “Ctrl-O” or File -> Open), update [lines 15-27](/example_data_reduction_settings/reducer_example.py#L15-L27) accordingly

- Run the reducer, Execute -> Execute All in the Menu
  * All output 1D files will be saved in the folder you define in the [`mantid_reduction_settings_example.csv`](/example_data_reduction_settings/mantid_reduction_settings_example.csv)