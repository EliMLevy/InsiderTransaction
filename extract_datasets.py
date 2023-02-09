import zipfile
import json
from os import path, listdir, mkdir
from os.path import isfile, join

target_dir = "./data/extraction_dir"
output_dir = "./data/"

outputs = []

def extract_file(zip_file, dest):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(dest)



for f in listdir(target_dir):
    if isfile(join(target_dir, f)) and f[-4:] == ".zip":
        dest_dir = output_dir + f[:6] # Grab first 6 chars ex: 2008q1
        outputs.append(dest_dir + "/")
        extract_file(join(target_dir, f), dest_dir)

print(json.dumps(outputs))


