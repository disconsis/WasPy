import glob 
import sys
from parsing import replace_safe_str

my_path = '../' 
if len(sys.argv) > 1: 
    my_path = sys.argv[1]

files = glob.glob(my_path + '/**/*.py', recursive=True)
for file in files:
    print(file)
    replaced_data = None
    with open(file, 'r') as fileptr:
        data = fileptr.read()
        replaced_data = replace_safe_str(data)
    if replaced_data is not None:
        with open(file, 'w') as fileptr:
            fileptr.write(replaced_data)
