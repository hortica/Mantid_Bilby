# 29 December 2017: to record list into a proper template, not just into one column
import glob, csv, os

## FIRST ONE

# user input START =================================================================

# Set path where data sit
### straight '/' and '/' at the end of the line
path_data = "D:\_work\projects\JohnWhite\Emulsions_dec2017\data\ready/"

# Set mask for files selection; for example: *bby*12*2.0*20.0*.dat
#mask = "*BBY00*5.0_9.0*.dat"
mask = "BBY*"

list_file_name = "FileList_test_6255.csv"

# NOTE: you will have file "selected_list.csv" in THE SAME folder where your initial data are; 
# Remember, that for "subtraction_final.py" script it is recommended to set-up a new folder with input csv list, because all subtracted files will sit in there

# user input END ===================================================================

os.chdir(path_data)
selected_list = glob.glob(mask)
#print selected_list

path_list_file_name = path_data+list_file_name
print path_list_file_name
#set-up output file
if os.path.exists(path_list_file_name):           # check if it does exist; delete if yes - no avoid appending 
    try:
        os.remove(path_list_file_name)                
    except:
        raise ValueError("It seems the file with this name already exists and open; please close it to proceed, note it will be overwritten.")

if not os.path.exists(path_list_file_name):
    file = open(path_list_file_name, 'w+')
    file.close()

header_1 = ['index', 'sample', 'background', 'scale_subtr', 'scale_mult']

header_2 = ['', 'sample scattering 1D ASCII file name',  \
'background scattering 1D ASCII file name', \
'const to be subtracted from the SAMPLE scattering data', \
'const, BACKGROUND data will be multiplied on']

with open(path_list_file_name, 'ab') as f_out:
    wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
    wr.writerow(header_1)
    wr.writerow(header_2)    

index = 0
for item in selected_list:
    raw = [index, item]
    index = index + 1
    with open(path_list_file_name, 'ab') as f_out:
        wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
        wr.writerow(raw)
