from mwaapre.preprocessor import Preprocessor

import json
import numpy as np

class CompoundPreprocessor:
    """
    Abstraction level for the single preprocessors. It is necessary in order to normalize 
    the gains simultaneously, which is fundamental for consistency.
    """
    def __init__(self, bfile, wfile, gfile, wtype, outdir, rho, name):
        self.w_preprocessor = Preprocessor('white', 
                wfile,
                gfile,
                wtype,
                outdir,
                rho,
                name
                )
        self.b_preprocessor = Preprocessor('black',
                bfile,
                gfile,
                wtype,
                outdir,
                rho,
                name
                )
        self.name = name
        self.rho = rho
        self.bfile = bfile
        self.wfile = wfile
        self.gfile = gfile
        self.outdir = outdir

    def set_lambdas(self, *args):
        self.w_preprocessor.set_lambdas(*args)
        self.b_preprocessor.set_lambdas(*args)

    def set_angles(self, *args):
        self.w_preprocessor.set_angles(*args)
        self.b_preprocessor.set_angles(*args)

    def raw_file_open(self):
        self.w_preprocessor.raw_file_open()
        self.b_preprocessor.raw_file_open()

    def calculate_avg(self):
        print("\n************************** \nStarting analysis...\n")
        self.w_preprocessor.calculate_avg()
        self.b_preprocessor.calculate_avg()

    def set_gains_dark(self):
        self.w_preprocessor.gd_file_open()
        self.b_preprocessor.gd_file_open()
    
    def confirm_start(self):
        print(f"\nOpening \"{self.bfile}\" for black data and \"{self.wfile}\" for white data.")
        print(f"Opening \"{self.gfile}\" for gains and dark data")
        print(f'The output files will be saved in the folder {self.outdir}.')
        print("Press ENTER to start the analysis, or CTRL-C to abort")

    def normalize_gains(self):
        """
        Takes care of normalizing the gains across both black and white.
        """
        g_u = []
        # Get a list of white gains:
        for wl in self.w_preprocessor.get_lambdas():
            for gain in self.w_preprocessor.get_gains(wl):
                g_u.append(gain)
        # Append all the black gains:
        for wl in self.b_preprocessor.get_lambdas():
            for gain in self.b_preprocessor.get_gains(wl):
                g_u.append(gain)
        # Get the max gain:
        g_u = np.max(g_u)
        # Normalize the white gains
        d = self.w_preprocessor.data
        for f_name in d.keys():
            for wlength in d[f_name].keys():
                for angle in d[f_name][wlength].keys():
                    # Dark subtraction and normalization:
                    v = d[f_name][wlength][angle]['mean']
                    g = d[f_name][wlength][angle]['gain']
                    dk = d[f_name][wlength][angle]['dark']
                    V = (v - dk) * (g_u / g)
                    d[f_name][wlength][angle]['norm'] = V
        # Normalize the black gains
        d = self.b_preprocessor.data
        for f_name in d.keys():
            for wlength in d[f_name].keys():
                for angle in d[f_name][wlength].keys():
                    # Dark subtraction and normalization:
                    v = d[f_name][wlength][angle]['mean']
                    g = d[f_name][wlength][angle]['gain']
                    dk = d[f_name][wlength][angle]['dark']
                    V = (v - dk) * (g_u / g)
                    d[f_name][wlength][angle]['norm'] = V

    def calculate_alpha(self):
        self.w_preprocessor.calculate_alpha()
        self.b_preprocessor.calculate_alpha()

    def integrate(self):
        self.w_preprocessor.integrate()
        self.b_preprocessor.integrate()
        print("\n**************************\nDone preprocessing.")

    def get_all_data(self):
        return self.b_preprocessor.get_all_data(), self.w_preprocessor.get_all_data()


    def write(self):
        if self.name is not None:
            bpath_json = self.outdir + self.name + '_mwaapre_black_integrals.json'
            wpath_json = self.outdir + self.name + '_mwaapre_white_integrals.json'
            bpath_csv = self.outdir + self.name + '_mwaapre_black_integrals.csv'
            wpath_csv = self.outdir + self.name + '_mwaapre_white_integrals.csv'
        else:
            bpath_json = self.outdir  + 'mwaapre_black_integrals.json'
            wpath_json = self.outdir  + 'mwaapre_white_integrals.json'
            bpath_csv = self.outdir + 'mwaapre_black_integrals.csv'
            wpath_csv = self.outdir + 'mwaapre_white_integrals.csv'
        self.b_preprocessor.csv_write(bpath_csv)
        self.w_preprocessor.csv_write(wpath_csv)
        self.b_preprocessor.json_write(bpath_json)
        self.w_preprocessor.json_write(wpath_json)
        return bpath_json, wpath_json

