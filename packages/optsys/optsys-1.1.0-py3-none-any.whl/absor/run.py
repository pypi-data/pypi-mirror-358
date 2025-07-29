from mwaatk import toolkit as too
import json
import sys

def printUsage():
    print("Usage: \npython mwaatoolkit.py configfilepath")

try:
    cfile = sys.argv[-1]
except:
    printUsage()

with open(cfile, 'r') as f:
    loaded_file = json.load(cfile)
    too.run(loaded_file)




