import glob 
import os
from argparse import ArgumentParser
from parsing import replace_safe_str
import shutil

parser = ArgumentParser()
parser.add_argument("in_path")
parser.add_argument("--out", dest="out_path")
args = parser.parse_args()

if args.out_path:
    if os.path.isdir(args.in_path):
        shutil.copytree(args.in_path, args.out_path)
    else:
        shutil.copyfile(args.in_path, args.out_path)

    path = args.out_path

else:
    path = args.in_path


def replace_file(file):
    print("Writing:", file)
    replaced_data = None
    with open(file, 'r') as fileptr:
        data = fileptr.read()
        replaced_data = replace_safe_str(data)
    if replaced_data is not None:
        with open(file, 'w') as fileptr:
            fileptr.write(replaced_data)


if os.path.isdir(path):
    files = glob.glob(path + '/**/*.py', recursive=True)
    for file in files:
        replace_file(file)
else:
    replace_file(path)

