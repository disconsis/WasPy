import glob 
import sys

my_path = '../' 
if len(sys.argv) > 1: 
    my_path = sys.argv[1]

files = glob.glob(my_path + '/**/*.py', recursive=True)
for file in files:
    print(file)
