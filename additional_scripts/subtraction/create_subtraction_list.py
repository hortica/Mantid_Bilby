import glob, csv, os

## FIRST ONE

# user input START =================================================================

# Set path where data sit
# https://docs.python.org/3.3/library/re.html#raw-string-notation
path_data = r"U:\data\proposal\05851\5_to_9_reduction/"
# Set mask for files selection; for example: *bby*12*2.0*20.0*.dat
mask = "*BBY00*5.0_9.0*.dat"

# NOTE: you will have file "selected_list.csv" in THE SAME folder where your initial data are; 
# Remember, that for "subtraction_final.py" script it is recommended to set-up a new folder with input csv list, because all subtracted files will sit in there

# user input END ===================================================================

os.chdir(path_data)
selected_list = glob.glob(mask)
print selected_list

list_file_name = "selected_list.csv"
path_list_file_name = path_data+list_file_name
print path_list_file_name
#set-up output file
if os.path.exists(path_list_file_name):           # check if it does exist; delete if yes - no avoid appending 
    os.remove(path_list_file_name)                 # ??? to check how does it know the path here ???
if not os.path.exists(path_list_file_name):
    file = open(path_list_file_name, 'w+')
    file.close()

for item in selected_list:
    with open(path_list_file_name, 'ab') as f_out:
        wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
        wr.writerow([item])