# 29 December 2017: to record list into a proper template, not just into one column
import glob, csv, os

## FIRST ONE

# user input START =================================================================

# Set path where data sit
### straight '/' and '/' at the end of the line
path_data = "D:/_full_path_here_/"

# Set mask for files selection; for example: *bby*12*2.0*20.0*.dat
mask = "*.dat"

list_file_name = "list_subtr.csv"

# NOTE: you will have file "selected_list.csv" in THE SAME folder where your initial data are; 
# Remember, that for "subtraction_final.py" script it is recommended to set-up a new folder with input csv list, because all subtracted files will sit in there

# user input END ===================================================================

os.chdir(path_data)
selected_list = glob.glob(mask)
#print selected_list

path_list_file_name = path_data+list_file_name
print (path_list_file_name)
#set-up output file
if os.path.exists(path_list_file_name):           # check if it does exist; delete if yes - no avoid appending 
    try:
        os.remove(path_list_file_name)                
    except:
        raise ValueError("It seems the file with this name already exists and open; please close it to proceed, note it will be overwritten.")

if not os.path.exists(path_list_file_name):
    file = open(path_list_file_name, 'w+')
    file.close()

header_1 = ['index', 'sample', 'background', 'scale_subtr', 'scale_mult', 'output_file_name', 'suffix']
print (type(header_1))
header_2 = ['', 'sample scattering 1D ASCII file name',  \
'background scattering 1D ASCII file name', \
'const to be subtracted from the SAMPLE scattering data', \
'const, BACKGROUND data will be multiplied on',\
'Can be left empty. In this case name will be [sample + suffix + _sub.dat]. If this name is given, the output file will be [name + suffix]',\
'Can be left empty. If given, will be added to the output name file. If the [output_file_name] is empty, the name will be [sample + suffix + _sub.dat]']

with open(path_list_file_name, 'w') as f_out:
    wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
    wr.writerow(header_1)
    wr.writerow(header_2)    

index = 0
for item in selected_list:
    raw = [index, item]
    index = index + 1
    with open(path_list_file_name, 'a+') as f_out:
        wr = csv.writer(f_out, delimiter=',', lineterminator='\n')
        wr.writerow(raw)
