import json, sys
from pprint import pprint

from mwaapre.preprocessor import Preprocessor
from mwaapre.compoundpreprocessor import CompoundPreprocessor



def run(bfile, wfile, gfile, wtype, out, rho, name):
    """
    Wrapper function for the integrals calculations from MWAA raw data.
    """
    cp = CompoundPreprocessor(bfile, wfile, gfile, wtype, out, rho, name)
    cp.confirm_start()
    input()
    cp.raw_file_open()
    cp.set_gains_dark()
    cp.calculate_avg()
    cp.normalize_gains()
    cp.calculate_alpha()
    cp.integrate()
    cp.write()

def cli_script():
    """Command Line script to use as entry point"""
    if "-g" in sys.argv:
        gfile = sys.argv[sys.argv.index("-g") + 1]
    else:
        outdir = "./results/"
    if "-o" in sys.argv:
        outdir = sys.argv[sys.argv.index("-o") + 1]
    else:
        outdir = "./results/"
    if "-r" in sys.argv:
        rho = float(sys.argv[sys.argv.index("-r") + 1])
    else:
        rho = 0.6
    if "--wtype" in sys.argv:
        white_type = sys.argv[sys.argv.index("--wtype") + 1]
    else:
        white_type = 'single'
    if "--name" in sys.argv:
        name = sys.argv[sys.argv.index("--name") + 1]
    else:
        name = None
    try:
        indb = sys.argv.index("-b")
        indw = sys.argv.index("-w")
        bfile = sys.argv[indb + 1]
        wfile = sys.argv[indw + 1]
        run(bfile, wfile, gfile, white_type, outdir, rho, name)
    except Exception as e:
        print(e)
        print("ERROR: unrecognized and/or missing options.\nUSAGE:\n\
    mpre -b <path-to-blackfile> -w <path-to-whitefile> -g <path-to-gainfile> [-o <path-to-outfolder> -r <rho> --wtype <white-type> --name <analysis-name>]")
