from absor.absorbancecalculator import AbsorbanceCalculator
from absor.datasetabsorbancecalculator import DatasetAbsorbanceCalculator
from absor.dataset import Dataset
from absor.filtersample import Filter
import json
import sys
from pprint import pprint


def run(options, bfile=None, wfile=None):
    """
    Wrapper function for the ABS minimization routine.
    
    Parameters:
        options: string, 
            a path to the configuration file
        wfile: string (optional),
            a path to the input JSON file containing the white integrals
        bfile: string (optional),
            a path to the input JSON file containing the black integrals
    """
    with open(options, 'r') as f:
        opt = json.load(f)

    infile_b = opt['b_integrals'] if bfile is None else bfile
    infile_w = opt['w_integrals'] if wfile is None else wfile
    
    ds = Dataset(infile_b, infile_w, opt)
    ds.create_set()
    s = ds.get_full_set()
    dac = DatasetAbsorbanceCalculator(s, opt)
    dac.do_minimization()
    dac.calc_abs()
    dac.plot()
    abs_file = dac.write()
    return abs_file


def cli_script():
    """Command Line script to use as entry point"""
    try:
        run(sys.argv[1])
    except Exception as e:
        print(e)
        print("USAGE: abs <path-to-config-file>")
