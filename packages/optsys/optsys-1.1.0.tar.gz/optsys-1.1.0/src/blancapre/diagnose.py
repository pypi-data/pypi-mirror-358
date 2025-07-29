# Script to analyse the raw BLAnCA data and show spectra and polar behaviour.  

###########################################################
# IMPORTS
###########################################################
import csv, json, sys
from pprint import pprint
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt






###########################################################
# CLASS TO HANDLE THE DATA DIAGNOSIS
###########################################################
class DataDoctor:
    """Class to handle the data diagnosis. 
        fpath is the raw data file path
        wfolder is the (optional) path where plots will be saved
    """
    def __init__(self, bdata, wdata, wfolder='./'):
        """The data is a dictionary provided by the CompoundPreprocessor 
        object. wfolder is the folder where all the plots will
        be saved."""
        self.wdata = wdata
        self.bdata = bdata
        self.working_folder = wfolder

    def check(self):
        # Get the white values and normalize them
        wdict = self.wdata[0]
        lambdas = []
        # I_0 vs lambda at 0 and 165 deg
        I_0_0, I_0_165 = [], []
        # I_0 vs angle at some wavelengths
        I_0_375, I_0_405, I_0_530, = [], [], []
        I_0_635, I_0_850, I_0_1000 = [], [], []
        for sub1 in wdict.values():
            for wl, sub2 in sub1.items():
                lambdas.append(float(wl))
                angles = [float(x) for x in sub2.keys()]
                for ang, sub3 in sub2.items():
                    # Fixed angles
                    if int(ang) == 0:
                        # Append the gain-normalized value
                        I_0_0.append(sub3['norm'])
                    if int(ang) == 165:
                        # Append the gain-normalized value
                        I_0_165.append(sub3['norm'])
                    # Fixed wavelengths
                    if int(wl) == 375:
                        # Append the gain-normalized value
                        I_0_375.append(sub3['norm'])
                    if int(wl) == 405:
                        # Append the gain-normalized value
                        I_0_405.append(sub3['norm'])
                    if int(wl) == 530:
                        # Append the gain-normalized value
                        I_0_530.append(sub3['norm'])
                    if int(wl) == 635:
                        # Append the gain-normalized value
                        I_0_635.append(sub3['norm'])
                    if int(wl) == 850:
                        # Append the gain-normalized value
                        I_0_850.append(sub3['norm'])
                    if int(wl) == 1000:
                        # Append the gain-normalized value
                        I_0_1000.append(sub3['norm'])
                    
                        
                    
        # Dict to store the lists of each black sample
        I_dict = {}
        for bdict in self.bdata: # access each black dict
            for name, sub1 in bdict.items():
                I_dict[name] = {'I_0' : [],
                                'I_165' : [],
                                'I_375' : [],
                                'I_405' : [],
                                'I_530' : [],
                                'I_635' : [],
                                'I_850' : [],
                                'I_1000' : []
                               }
                # I vs lambda at 0 and 165 deg
                I_0, I_165 = [], []
                # I vs angle at some wavelengths
                I_375, I_405, I_530, = [], [], []
                I_635, I_850, I_1000 = [], [], []
                for wl, sub2 in sub1.items():
                    for ang, sub3 in sub2.items():
                        # Fixed angles
                        if int(ang) == 0:
                            # Append the gain-normalized value
                            I_dict[name]['I_0'].append(sub3['norm'])
                        if int(ang) == 165:
                            # Append the gain-normalized value
                            I_dict[name]['I_165'].append(sub3['norm'])
                        # Fixed wavelengths
                        if int(wl) == 375:
                            # Append the gain-normalized value
                            I_dict[name]['I_375'].append(sub3['norm'])
                        if int(wl) == 405:
                            # Append the gain-normalized value
                            I_dict[name]['I_405'].append(sub3['norm'])
                        if int(wl) == 530:
                            # Append the gain-normalized value
                            I_dict[name]['I_530'].append(sub3['norm'])
                        if int(wl) == 635:
                            # Append the gain-normalized value
                            I_dict[name]['I_635'].append(sub3['norm'])
                        if int(wl) == 850:
                            # Append the gain-normalized value
                            I_dict[name]['I_850'].append(sub3['norm'])
                        if int(wl) == 1000:
                            # Append the gain-normalized value
                            I_dict[name]['I_1000'].append(sub3['norm'])

        # Make the plots
        for name, subdict in I_dict.items():
            fig, ax = plt.subplots(nrows=3, ncols=2)
            # I/I0 at 0 deg
            I = subdict['I_0']
            transmittance = [i/i_0 for (i, i_0) in zip(I, I_0_0)]
            ax[0][0].plot(lambdas, transmittance, '-k')
            ax[0][0].set_xlabel('Wavelength [nm]')
            ax[0][0].set_ylabel(r'$I/I_0$')
            ax[0][0].set_title(r'Transmitted $I/I_0$ at 0 deg')
            ax[0][0].grid(alpha=.3)
            # ATN at 0 deg
            atn = [- 100 * np.log(x) for x in transmittance]
            ax[1][0].plot(lambdas, atn, '-k')
            ax[1][0].set_xlabel('Wavelength [nm]')
            ax[1][0].set_ylabel(r'$-100$log($I/I_0$)')
            ax[1][0].set_title(r'Transmitted ATN at 0 deg')
            ax[1][0].grid(alpha=.3)
            # I/I0 at 165 deg
            I = subdict['I_165']
            reflectance = [i/i_0 for (i, i_0) in zip(I, I_0_165)]
            ax[0][1].plot(lambdas, reflectance, '-k')
            ax[0][1].set_xlabel('Wavelength [nm]')
            ax[0][1].set_ylabel(r'$I/I_0$')
            ax[0][1].set_title(r'Reflected $I/I_0$ at 165 deg')
            ax[0][1].grid(alpha=.3)
            # ATN at 165 deg
            r_atn = [- 100 * np.log(x) for x in reflectance]
            ax[1][1].plot(lambdas, r_atn, '-k')
            ax[1][1].set_xlabel('Wavelength [nm]')
            ax[1][1].set_ylabel(r'$-100$log($I/I_0$)')
            ax[1][1].set_title(r'Reflected ATN at 165 deg')
            ax[1][1].grid(alpha=.3)
            # I/I0 vs theta
            I375 = subdict['I_375']
            t375 = [i/i_0 for (i, i_0) in zip(I375, I_0_375)]
            I405 = subdict['I_405']
            t405 = [i/i_0 for (i, i_0) in zip(I405, I_0_405)]
            I530 = subdict['I_530']
            t530 = [i/i_0 for (i, i_0) in zip(I530, I_0_530)]
            I635 = subdict['I_635']
            t635 = [i/i_0 for (i, i_0) in zip(I635, I_0_635)]
            I850 = subdict['I_850']
            t850 = [i/i_0 for (i, i_0) in zip(I850, I_0_850)]
            #I1000 = subdict['I_1000']
            #t1000 = [i/i_0 for (i, i_0) in zip(I1000, I_0_1000)]
            ax[2][0].plot(angles, t375, '-', color='magenta', label='375 nm')
            ax[2][0].plot(angles, t405, '-', color='blue', label='405 nm')
            ax[2][0].plot(angles, t530, '-', color='green', label='530 nm')
            ax[2][0].plot(angles, t635, '-', color='red', label='635 nm')
            ax[2][0].plot(angles, t850, '-', color='brown', label='850 nm')
            #ax[2][0].plot(angles, t1000, '-', color='black', label='1000 nm')
            ax[2][0].set_xlabel('Angle [deg]')
            ax[2][0].set_ylabel(r'$I/I_0$')
            ax[2][0].set_title(r'$I/I_0$ vs $\theta$')
            ax[2][0].grid(alpha=.3)
            # ATN vs theta
            A375 = [-100*np.log(r) for r in I375]
            A405 = [-100*np.log(r) for r in I405]
            A530 = [-100*np.log(r) for r in I530]
            A635 = [-100*np.log(r) for r in I635]
            A850 = [-100*np.log(r) for r in I850]
            #A1000 = [-100*np.log(r) for r in I1000]
            ax[2][1].plot(angles, A375, '-', color='magenta', label='375 nm')
            ax[2][1].plot(angles, A405, '-', color='blue', label='405 nm')
            ax[2][1].plot(angles, A530, '-', color='green', label='530 nm')
            ax[2][1].plot(angles, A635, '-', color='red', label='635 nm')
            ax[2][1].plot(angles, A850, '-', color='brown', label='850 nm')
            #ax[2][1].plot(angles, A1000, '-', color='black', label='1000 nm')
            ax[2][1].set_xlabel('Angle [deg]')
            ax[2][1].set_ylabel(r'$-100$log($I/I_0$)')
            ax[2][1].set_title(r'ATN vs $\theta$')
            ax[2][1].grid(alpha=.3)
            # Save the figure
            path = self.working_folder + name + '.png'
            fig.tight_layout()
            try:
                fig.savefig(path, dpi=150)
            except FileNotFoundError as fnfe:
                Path(self.working_folder).mkdir(parents=True, exist_ok=True)
                fig.savefig(path, dpi=150)
            plt.close(fig)










