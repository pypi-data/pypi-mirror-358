from pprint import pprint 
import enlighten  # for progress bar
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import csv

from absor.absorbancecalculator import AbsorbanceCalculator

class DatasetAbsorbanceCalculator:
    def __init__(self, dataset, optdict):
        """
        Creates a list of calculator objects.
        The dataset argument must be the output of a Dataset object (list of Filter objects).
        """
        self.options = optdict
        self.calculator_set = []
        fnames = []
        wlengths = []
        for f in dataset:
            self.calculator_set.append(AbsorbanceCalculator(f, self.options))
            fnames.append(f.name)
            wlengths.append(f.wlength)
        # Creates the dictionary to store the results
        self.results = {fname:
                                {wlength:
                                        {
                                            'tau': None,
                                            'omega': None,
                                            'ABS': None,
                                        }
                                        for wlength in wlengths
                                }
                                for fname in fnames
                        }


    def set_tolerance(self, tol):
        for c in self.calculator_set:
            c.set_tolerance(tol)


    def do_minimization(self):
        print("\n************************ \nPerforming ABS minimization...")
        failure_count = 0
        failed_fname = []
        failed_wlength = []
        t_0 = time.time()
        if not self.options['verbose']:
            pbar = enlighten.Counter(total=len(self.calculator_set), desc='Minimization progress', unit='filters')
        for c in self.calculator_set:
            if self.options['verbose']:
                print("\nAnalysing filter {} at wavelength {} nm, number {} of {}.".format(c.filter.name, c.filter.wlength, self.calculator_set.index(c)+1, len(self.calculator_set)))
            res = c.do_minimization()
            if not res: # Minimization failed
                failure_count = failure_count + 1
                failed_fname.append(c.filter.name)
                failed_wlength.append(c.filter.wlength)
                if self.options['debug']:
                    input("Press ENTER to continue")
                continue
            elif res == 'Error':
                failure_count = failure_count + 1
                failed_fname.append(c.filter.name)
                failed_wlength.append(c.filter.wlength)
                if self.options['debug']:
                        input("Press ENTER to continue")
            else:
                omega, tau = res
                name = c.filter.name
                wl = c.filter.wlength
                self.results[name][wl]['tau'] = tau
                self.results[name][wl]['omega'] = omega
            if not self.options['verbose']:
                pbar.update()
        print('\nABS minimization completed with {} failed minimization(s). Failed minimizations for {}.\nMinimization total time: {} s'.format(failure_count, list(zip(failed_fname, failed_wlength)), time.time()-t_0))
        print('\n********************** \nABS minimization complete.')

    def calc_abs(self):
        for c in self.calculator_set:
            ABS = c.calc_abs()
            name = c.filter.name
            wl = c.filter.wlength
            if ABS is not None:
                self.results[name][wl]['ABS'] = ABS
                self.results[name][wl]['conv'] = True
            else:
                self.results[name][wl]['conv'] = False

    def get_filter_abs(self, fname, wl=None):
        if wl == None:
            res = []
            for key, result in self.results.items():
                if key == fname:
                    res.append(result)
            return res
        else:
            return self.results[fname][wl]

    def print_abs(self, fname, wl=None):
        if wl == None:
            pprint(self.get_filter_abs(fname))
        else:
            pprint(self.get_filter_abs(fname, wl=wl))

    def make_plots(self, fname, wl):
        for c in self.calculator_set:
            if c.filter.name == fname and c.filter.wlength == wl:
                c.make_plots()

    def get_results(self):
        return self.results

    def get_one_result(self, f, w):
        r = self.results
        return r[f][w]['ABS'], r[f][w]['omega'], r[f][w]['tau']

    def write(self):
        #JSON
        json_fpath = self.options['out_folder'] + self.options['name'] +'_absor_out.json'
        with open(json_fpath, 'w') as json_file:
            json.dump(self.results, json_file, indent=4)
        #CSV 
        csv_fpath = self.options['out_folder'] + self.options['name'] + '_absor_out.csv'
        csv_ATO_fpath = self.options['out_folder'] + self.options['name'] + '_abstauome_out.csv'
        with open(csv_fpath, 'w') as fwrite:
            writer = csv.writer(fwrite)
            first_header = ['', '100 ABS']
            header = ['Name',]
            fn = list(self.results.keys())[0]
            for wlength in self.results[fn].keys():
                header.append(wlength)    
            writer.writerow(first_header)
            writer.writerow(header)
            for fname in self.results.keys():
                row = [fname,]
                abs_row = []
                for wlength in self.results[fname].keys():
                    ABS, OME, TAU = self.get_one_result(fname, wlength)
                    abs_row.append(ABS)
                row = row + abs_row
                writer.writerow(row)
        with open(csv_ATO_fpath, 'w') as fwrite:
            writer = csv.writer(fwrite)
            header = ['Name', 'Wavelength [nm]', '100ABS', 'Tau', 'SSA']
            writer.writerow(header)
            for name, item in self.results.items():
                for wlength, item_2 in item.items():
                    ABS, OME, TAU = self.get_one_result(name, wlength)
                    row = [name, wlength, ABS, TAU, OME]
                    writer.writerow(row)
        return json_fpath


    def plot(self):
        for fname, item in self.results.items():
            wl, ab = [], []
            fig, ax = plt.subplots()
            for wlength in self.results[fname].keys():
                wl.append(float(wlength))
                ab.append(self.results[fname][wlength]['ABS'])
            ax.plot(wl, ab, '.k')
            ax.grid(alpha=0.3)
            ax.set_xlabel("Wavelength [nm]")
            ax.set_ylabel("100 ABS")
            fig.tight_layout()
            fig.savefig(self.options['out_folder'] + fname + '_' + self.options['name'] + "_abs_plot.png", dpi=200)
            plt.close()

