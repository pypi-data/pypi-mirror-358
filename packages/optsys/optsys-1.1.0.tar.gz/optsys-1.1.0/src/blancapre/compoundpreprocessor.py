from blancapre.preprocessor import Preprocessor
from blancapre.diagnose import DataDoctor

import json
from pathlib import Path
import numpy as np

class CompoundPreprocessor:
    """
    Abstraction level for the single preprocessors. It is necessary in order to normalize 
    the gains simultaneously, which is fundamental for consistency.
    """
    def __init__(self, 
            bfile, 
            wfile, 
            outdir, 
            rho,
            int_style,
            plots,
            name,
            dfolder):
        self.w_preprocessor = Preprocessor('white', 
                wfile, 
                outdir, 
                rho,
                plots, 
                name)
        self.b_preprocessor = Preprocessor('black', 
                bfile, 
                outdir, 
                rho,
                plots, 
                name)
        self.int_style = int_style
        self.wfile = wfile
        self.bfile = bfile
        self.rho = rho
        self.plots = plots
        self.outdir = outdir
        self.name = name
        self.diagnosis_folder = dfolder

    def set_lambdas(self, *args):
        self.w_preprocessor.set_lambdas(*args)
        self.b_preprocessor.set_lambdas(*args)

    def set_angles(self, *args):
        self.w_preprocessor.set_angles(*args)
        self.b_preprocessor.set_angles(*args)

    def raw_file_open(self):
        self.w_preprocessor.raw_file_open()
        self.b_preprocessor.raw_file_open()

    def confirm_start(self):
        print(f"\nOpening \"{self.bfile}\" for black data and \"{self.wfile}\" for white data. I will write results to {self.outdir}")
        print(f"I will calculate integrals {self.int_style} style, with a rho = {self.rho}")
        print("I will write phase plots to disk") if self.plots else print("I won't write phase plots to disk")
        input("Press ENTER to start the analysis, or CTRL-C to abort")
        print(f"\n**************************\n --- Started preprocessing.")

    def normalize_gain(self):
        self.w_preprocessor.normalize_gain()
        self.b_preprocessor.normalize_gain()

    def write_angular_profile(self, typ, sample_name, wavelength):
        if typ == 'w':
            self.w_preprocessor.write_angular_profile(sample_name, wavelength)
        elif typ == 'b':
            self.b_preprocessor.write_angular_profile(sample_name, wavelength)
        else:
            print("passing write_angular_profile")

    def integrate(self):
        if self.int_style == 'mwaa':
            self.w_preprocessor.mwaa_style_integrate()
            self.b_preprocessor.mwaa_style_integrate()
        elif self.int_style == 'polar':
            self.w_preprocessor.polar_style_integrate()
            self.b_preprocessor.polar_style_integrate()
        print(f"\n**************************\n --- Done preprocessing.")

    def get_all_data(self):
        return self.b_preprocessor.get_all_data(), self.w_preprocessor.get_all_data()

    def do_diagnosis(self):
        print(f"\n**************************\n ----- Started diagnosis.")
        bdata, wdata = self.get_all_data()
        doctor = DataDoctor(bdata, wdata, wfolder=self.diagnosis_folder)
        doctor.check()
        print(f"\n**************************\n ----- Done diagnosis.")


    def write(self):
        self.b_preprocessor.csv_write()
        self.w_preprocessor.csv_write()
        self.b_preprocessor.json_write()
        self.w_preprocessor.json_write()
        #except FileNotFoundError as fnfe:
        #    Path(self.options['out_folder']).mkdir(parents=True, exist_ok=True)
        #    self.b_preprocessor.csv_write(bpath_csv)
        #    self.w_preprocessor.csv_write(wpath_csv)
        #    self.b_preprocessor.json_write(bpath_json)
        #    self.w_preprocessor.json_write(wpath_json)

