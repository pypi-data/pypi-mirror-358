import json, sys
from pprint import pprint

from blancapre.preprocessor import Preprocessor
from blancapre.compoundpreprocessor import CompoundPreprocessor



def run(bfile, 
        wfile, 
        out, 
        rho, 
        method, 
        plots, 
        name, 
        dfolder, 
        angular_type, 
        angular_name, 
        angular_wl
        ):
    """
    Wrapper function for the integrals calculations from BLAnCA raw data.
    """
    cp = CompoundPreprocessor(bfile, wfile, out, rho, method, plots, name, dfolder)
    cp.confirm_start()
    cp.raw_file_open()
    cp.normalize_gain()
    if dfolder is not None:
        cp.do_diagnosis()
    if angular_wl is not None:
        cp.write_angular_profile(str(angular_type), 
                str(angular_name), 
                int(angular_wl))
    cp.integrate()
    cp.write()

def cli_script():
    """Command Line script to use as entry point"""
    try:
        if "-o" in sys.argv:
            outdir = sys.argv[sys.argv.index("-o") + 1]
        else:
            outdir = "./results/"
        if "-r" in sys.argv:
            rho = sys.argv[sys.argv.index("-r") + 1]
        else:
            rho = 0.6
        if "-m" in sys.argv:
            method = sys.argv[sys.argv.index("-m") + 1]
        else:
            method = "polar"
        if "--name" in sys.argv:
            name = sys.argv[sys.argv.index("--name") + 1]
        else:
            name = None
        if "--noplots" in sys.argv:
            plots = False
        else:
            plots = True
        if "--diagnose" in sys.argv:
            dfolder = sys.argv[sys.argv.index("--diagnose") + 1]
        else:
            dfolder = None
        if "--angular" in sys.argv:
            idx = sys.argv.index("--angular")
            ang_t = sys.argv[idx + 1]
            ang_n = sys.argv[idx + 2]
            ang_w = sys.argv[idx + 3]
        else:
            ang_t, ang_n, ang_w = None, None, None
        indb = sys.argv.index("-b")
        indw = sys.argv.index("-w")
        bfile = sys.argv[indb + 1]
        wfile = sys.argv[indw + 1]
        run(bfile, wfile, outdir, rho, 
            method, plots, name, dfolder,
            ang_t, ang_n, ang_w)
    except ValueError as e:
        print(f"DEBUG {e}")
        print("ERROR: unrecognized and/or missing options.\nUSAGE:\n\
    bpre -b <path-to-blackfile> -w <path-to-whitefile> [-o <path-to-outfolder> -r <rho> -m <integration-method> --noplots --name <analysis-name> --diagnose <diagnosis-folder> --angular <filter_type> <filter_name> <wavelength>]")
