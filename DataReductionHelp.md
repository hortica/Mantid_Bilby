## Data reduction instruction

- Download scripts from [`reduction_scripts_const`](/reduction_scripts_const) 

* Two scripts:
   * “BilbyCustomFunctions_Reduction.py”
   * “shift_assembled.csv”
Can be saved everywhere, but important thing is that the folder shall be on the path, see below:
Then you see this window, the proceed with “Browse to directory” and “Add directory”:

3). The script "SANSDataProcessor.py" - 
to be copied into folder where MantidInstall is installed:
...  \MantidInstall\plugins\python\algorithms\WorkflowAlgorithms

4). You _have to_ add your data with your *.tar files AND two csv files (the List of files and the Settings) on the path as well.
Please use the same logic as in 2).
To keep it simple, one can put tar and csv files in one folder, but you can add as many folders on the paths as you want.

5). To open your reducer script, open scripts window: go to Mantid, menu “View”, then “Script window” (or just press F3).

6). In the “Python Window” open file, just “Ctrl-O” or File -> Open.

7). To run the reducer, Execute -> Execute All in the Menu.
All your 1D files will be saved in the folder you define in the Settings file.
The other thing that would be good to get from you is a description to put into the algorithm documentation of what the algorithm does. I have again added a skeleton of the documentation to the pull requests but wanted to check with you what a good description of the algorithm would be?
