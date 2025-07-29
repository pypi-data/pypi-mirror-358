import csv
import json
from pathlib import Path
from copy import copy
from pprint import pprint
import numpy as np
import pandas as pd
from blancapre.alphaminimizer import AlphaMinimizer
from scipy.optimize import curve_fit as fit
import matplotlib.pyplot as plt





class Preprocessor:
    '''
    A class that contains all the routines to elaborate the raw data into passed radiation and backscattered radiation integrals.
    '''

    def __init__(self, 
            typ, 
            infile, 
            outdir, 
            rho,
            plots,
            name,
            ):
        #?
        self.fwd_corr = 1
        self.bck_corr = 1
        self.rho       = rho   # The surface roughness parameter
        self.angles = [0, 125, 165] # For MWAA-style integration
        self.type = typ
        self.infile = infile
        self.outdir = outdir
        self.plots = plots
        if name is None:
            self.csv_fpath = outdir + "blancapre_" + self.type + "_integrals.csv"
            self.json_fpath = outdir + "blancapre_" + self.type + "_integrals.json"
        else:
            self.csv_fpath = outdir + name + "_blancapre_" + self.type + "_integrals.csv"
            self.json_fpath = outdir + name + "_blancapre_" + self.type + "_integrals.json"




#####################################################
# FILE OPENING (COMMON FOR ALL INTEGRATION MODES)
#####################################################

    def raw_file_open(self):
        """ Opens the file containing the raw data for analysis.
            For each excel tab a data dict is created and
            appended to the self.data list of dicts.
        """
        ##################################################
        # This method has to be cleaned up and streamlined
        ##################################################

        # sheet_name=None returns a dict of dataframes, one
        # per sheet.
        raw_data_dict = pd.read_excel(self.infile, sheet_name=None)
        #DEBUG
        #input(f'x-x opening {self.infile}')

        # Get the names of the individual worksheet (= the names 
        # of the filter samples)
        self.list_of_names = [x for x in raw_data_dict.keys()]
        #DEBUG
        #input(f'x-x list of names {self.list_of_names}')

        # Create a self.data empty list (no need for a dict
        # because the names are already stored in each data dict)
        self.datalist = []
        
        # Iterate over all worksheets
        for sample_name, raw_data in raw_data_dict.items():
            # Init the empty containers.
            wl, dark, meas = [], [], {}
            dark_1ms_list, dark_2s_list = [], []
            wl_new, dark_new, meas_new = [], [], {}
            dark_avg, meas_avg, n = 0, 0, 0

            # List of the names (and therefore the angles) of the measurements
            meas_list = [x for x in raw_data.keys() if 'measure' in x]
            # Isolated list of the angles
            angles = [float(x.split('_')[1]) for x in meas_list]
            # List that holds tuples (angle, integration time)
            timgles = [] 
            for key, value in raw_data.items():
                # Select only the columns that contain a time
                if key.split('_')[0] == 'time': 
                    # For these columns, the header is time_35
                    # where 35 is in milliseconds
                    timgles.append((float(key.split('_')[1]), value[0]))

            # First iteration to cut the wavelength and data tails above 900nm and below 350nm
            # and to read the data into dark and measure
            dummy, tmp = 0, []
            for meas_name in meas_list:
                for w, d, d1, d2000, m in zip(raw_data['wavelength'], raw_data['dark_0'], raw_data['dark_1ms'], raw_data['dark_2000ms'], raw_data[meas_name]):
                    if w > 350 and w < 1000:
                        if dummy == 0:
                            # For the first iteration only, process wavelength and dark
                            wl.append(w)
                            dark.append(d)
                            dark_1ms_list.append(d1)
                            dark_2s_list.append(d2000)
                        tmp.append(m)
                dummy += 1
                meas[meas_name] = [x for x in tmp]
                tmp = []

            # Second iteration to average over each integer wavelength
            dummy = 0
            for meas_name, measurement in meas.items():
                dark_avg, meas_avg, n, wl_new = 0, 0, 0, []
                for w, d, m in zip(wl, dark, measurement):
                    if float(int(w)) in wl_new:
                        if dummy == 0:
                            dark_avg += d
                        meas_avg += m
                        n += 1
                    elif float(int(w)) not in wl_new:
                        if n != 0:
                            if dummy == 0: 
                                dark_avg /= float(n)
                                dark_new.append(dark_avg)
                            meas_avg /= float(n)
                            tmp.append(meas_avg)
                            dark_avg, meas_avg, n = 0, 0, 0
                        wl_new.append(float(int(w)))
                        dark_avg += d
                        meas_avg += m
                        n += 1
                meas_new[meas_name] = [x for x in tmp]
                tmp = []
                dummy += 1

            # Third iteration: bin the lambdas into 5nm bins
            tmp, dmp, binn, dinn = [], [], 0, 0
            meas_binned = {}
            dark_binned = []
            wl_binned = [float(x) for x in wl_new if x % 5 == 0]
            for meas_name, measurement in meas_new.items():
                for i, w in enumerate(wl_new):
                    if w % 5 == 0:
                        binn = 0
                        dinn = 0
                        if i < 645: # 5*130 - 4 (the last wl has only 4 data)
                            for j in range(5):
                                binn += measurement[i+j]
                                dinn += dark_new[i+j]
                            binn /= 5.
                            dinn /= 5.
                        else:
                            for j in range(4):
                                binn += measurement[i+j]
                                dinn += dark_new[i+j]
                            binn /= 4.
                            dinn /= 4.
                        tmp.append(binn)
                        dmp.append(dinn)
                meas_binned[meas_name] = [(w,x) for (w, x) in zip(wl_binned, tmp)]
                dark_binned = [x for x in dmp]
                tmp = []

            # Dictionary object like in blancatk
            name = raw_data['filter_name'][0]
            data = {name:
                    {w:
                        {a:
                            {
                                'raw': None,
                                'mean': None,
                                'time': None,
                                'dark': None,  
                                'adj': None, # "adjusted" after dark subtraction
                                'norm': None, # for compatibility with blancatk
                                'unc': None
                                }
                            for a in angles
                            }
                        for w in wl_binned
                        }
                    }

            for meas_name, measurement in meas_binned.items():
                for i, w in enumerate(wl_binned):
                    if measurement[i][0] == w:
                        data[name][w][float(meas_name.split("_")[1])]["raw"] = measurement[i][1]
                    for angle, time in timgles:
                        data[name][w][angle]["time"] = time

            # At this point, the relevant variables are:
            # - data = a dictionary as detailed above
            ## data = {name: {wavelength: {angle: {"raw", "gain", "dark" (empty), "adj" (empty), "norm" (empty), "unc" (empty)}}}}
            # - dark_binned = list containing the 5 nm binned dark values from 350  to 900 nm
            # - dark_1ms_list = list containing the full unbinned dark at the extreme integration time
            # - dark_2s_list = list containing the full unbinned dark at the extreme integration time

            # Dark subtraction

            dark_slope, dark_intercept = 0, 0
            n = 0
            for d1, d2000 in zip(dark_1ms_list, dark_2s_list):
                # Get the slope of the line between the two points (1, dark1) (1000, dark1000) (it's an average)
                dark_slope += (d2000 - d1) / 1999 #1999 = 2000 - 1 
                first_term = d1
                second_term = 1 * (d2000 - d1) / 1999
                # Get the intercept of the line between the same two points (it's an average)
                dark_intercept += first_term - second_term 
                n += 1
            dark_slope /= n 
            dark_intercept /= n 
            #print(f'dark slope {dark_slope}')
            #print(f'dark intercept {dark_intercept}')
            # Carry out the dark rescale and subtraction
            for name, data_item in data.items():
                overall_time = data_item[375][0]['time'] # normalize to this
                for wlength, wlength_item, dark_at_zero in zip(data_item.keys(), data_item.values(), dark_binned):
                    for angle in wlength_item.keys():
                        if angle == 0:
                            data[name][wlength][angle]['dark'] = dark_at_zero 
                            data[name][wlength][angle]['adj'] = data[name][wlength][angle]['raw'] - data[name][wlength][angle]['dark']
                        else:
                            own_time = wlength_item[angle]['time']
                            # Dark rescaling
                            data[name][wlength][angle]['dark'] = dark_intercept + dark_slope * own_time
                            # Dark subtraction
                            data[name][wlength][angle]['adj'] = data[name][wlength][angle]['raw'] - data[name][wlength][angle]['dark']
                # Write the extracted data dictionary to the global list 
                self.datalist.append(data)
                #DEBUG
                #print('x-x current data')
                #pprint(data)
                #input(f'{list(data.keys())[0]}\n\n\n\n\n\n\n\n')


    def normalize_gain(self):
        # Gain (time) normalization
        # This is done to a fixed number (100) so that
        # the same normalization is applied between loaded
        # and blank filter
        for data in self.datalist:
            for name, data_item in data.items():
                overall_time = 100 # normalize to this
                for wlength, wlength_item in data_item.items():
                    for angle in wlength_item.keys():
                        val = wlength_item[angle]['adj']
                        own_time = wlength_item[angle]['time']
                        norm_factor = overall_time / own_time
                        data[name][wlength][angle]['norm'] = val * norm_factor


    def _write_angular_profile(self, sample_name, wavelength):
        """No high-level interface, just implement it from within compoundpreprocessor
           when needed."""
        filepath = self.outdir + sample_name + '_' + str(wavelength) + '_profile.csv'
        with open(filepath, 'w') as f:
            writa = csv.writer(f)
            for data in self.datalist:
                for name, data_item in data.items():
                    if name == sample_name:
                        for wlength, wlength_item in data_item.items():
                            if wlength == wavelength:
                                header = ['angle', 'value']
                                writa.writerow(header)
                                for angle in wlength_item.keys():
                                    row = [angle, wlength_item[int(angle)]['norm']] 
                                    writa.writerow(row)

    def write_angular_profile(self, sample_name, wavelength):
        try:
            self._write_angular_profile(sample_name, wavelength)
        except FileNotFoundError as fnfe:
            Path(self.outdir).mkdir(parents=True, exist_ok=True)
            self._write_angular_profile(sample_name, wavelength)



#############################################
# POLAR INTEGRATION
#############################################

    def polar_style_integrate(self):
        # To fit and extrapolate from 165 to 180 degrees
        def backward_function(x, A, B, C, D):
            x = x / 360 * 2*np.pi #transform to radians
            return A * (np.pi - x) ** 4 + B * (np.pi - x) ** 2 + C * np.cos(np.pi - x) + D
        # Integration
        for data in self.datalist:
            for name, data_item in data.items():
                if self.plots:
                    fig, ax = plt.subplots(2,1)
                for wlength, wlength_item in data_item.items():
                    forward_ang = []
                    backward_ang = []
                    forward_val = []
                    backward_val = []
                    backward_x = np.linspace(100, 165, 1000) # fit only in the data range
                    for angle in wlength_item.keys():
                        if angle <= 80:
                            forward_ang.append(angle)
                            forward_val.append(data[name][wlength][angle]['norm'])
                        elif angle >= 100 and angle <= 165:
                            backward_ang.append(angle)
                            backward_val.append(data[name][wlength][angle]['norm'])
                    # Do backward extrapolation through fit
                    backward_fit = fit(backward_function, backward_ang, backward_val, bounds=([-1e12,-1e12,-1e12,-1e12], [1e12, 1e12, 1e12, 1e12]))
                    final_range = np.linspace(166, 180, 15, dtype=int)
                    final_val = backward_function(final_range, backward_fit[0][0], backward_fit[0][1], backward_fit[0][2], backward_fit[0][3])
                    #if wlength == 375: 
                    #    input((name, f'A {backward_fit[0][0]} B {backward_fit[0][1]} C {backward_fit[0][2]} D {backward_fit[0][3]}'))
                    final_range = list(final_range)
                    final_val = list(final_val)
                    # New lists for plotting in degrees, without extrapolation
                    backward_ang_for_plot = [x for x in backward_ang]
                    backward_val_for_plot = [x for x in backward_val]
                    forward_ang_for_plot = [x for x in forward_ang]
                    forward_val_for_plot = [x for x in forward_val]
                    # Update the backward angle and values lists
                    backward_ang = [90,] + backward_ang + final_range
                    backward_ang = [2 * np.pi * x / 360 for x in backward_ang] # to radians
                    backward_val = [0.,] + backward_val + final_val
                    # Append the final values for the trapezoidal integration
                    forward_ang.append(90)
                    forward_ang = [2 * np.pi * x / 360 for x in forward_ang] # to radians
                    forward_val.append(0) # No scattering at 90 degrees
                    forward_y = [x * np.sin(y) for (x,y) in zip(forward_val, forward_ang)]
                    backward_y = [x * np.sin(y) for (x,y) in zip(backward_val, backward_ang)]
                    forward_integral =  np.trapz(forward_y, x=forward_ang)
                    backward_integral =  np.trapz(backward_y, x=backward_ang)
                    ## DEBUG INFORMATIon
                    #print(f'forward val {forward_val} backward val {backward_val}')
                    #print(f'forward {forward_integral} backward {backward_integral}')
                    #lam = 635
                    #if wlength == lam:
                    #    print(name)
                    #    for v in forward_val:
                    #        print(v)
                    #    for v in backward_val:
                    #        print(v)
                    if self.plots:
                        ax[0].plot(forward_ang_for_plot, forward_val_for_plot, '-k', linewidth=.2)
                        ax[0].set_xlabel('Angle [deg]')
                        ax[0].set_ylabel('A.U.')
                        ax[0].set_title('Forward')
                        ax[1].plot(backward_ang_for_plot, backward_val_for_plot, '-r', linewidth=.2)
                        ax[1].set_xlabel('Angle [deg]')
                        ax[1].set_ylabel('A.U.')
                        ax[1].set_title('Backward')
                    data[name][wlength]['p_f'] = forward_integral
                    data[name][wlength]['b_f'] = backward_integral
                if self.plots:
                    try:
                        plt.tight_layout()
                        plt.savefig(self.outdir + f'phaseplot_{list(data.keys())[0]}.png', dpi=300)

                    except FileNotFoundError as fnfe:
                        Path(self.outdir).mkdir(parents=True, exist_ok=True)
                        plt.tight_layout()
                        plt.savefig(self.outdir + f'phaseplot_{list(data.keys())[0]}.png', dpi=300)

                ###########################################################################
                # This integration has been verified manually and the results are correct #
                # at the wavelength of 635 nm                                             #
                ###########################################################################





###############################################
# MWAA-STYLE (3 angles) INTEGRATION
###############################################

    def s_alpha(self, alpha, theta=0.5, rho=0.5):
        """
        This method is used to calculate S(alpha | theta) as detailed in Petzold 2003.
        S is the functional form of the backscattered radiation assuming both diffuse 
        and Gaussian behaviour, in proportions dictated by the parameter alpha. 
        In this implementation, since alpha is the variable to to change in order to 
        find the zero later on, theta is the parameter and alpha the passed variable.
        
        """
        cos_t = np.cos(theta - np.pi)
        exp_t = np.exp(-0.5 * ((theta - np.pi) ** 2) / (self.rho ** 2))
        s_a = alpha * cos_t + (1 - alpha) * exp_t
        return s_a

    def r_alpha(self, alpha, theta_1=2.18, theta_2=2.88, rho=0.5):
        """
        The S-function ratio between S(alpha | theta = 125°) and S(alpha| theta = 165°)

        kwargs have to be theta_1=float, theta_2=float, rho=float
        """
        s_a_1 = self.s_alpha(alpha, theta=theta_1, rho=self.rho)
        s_a_2 = self.s_alpha(alpha, theta=theta_2, rho=self.rho)
        r_a   = s_a_1 / s_a_2
        return r_a

    def f_alpha(self, alpha, theta_1=2.18, theta_2=2.88, rho=0.5, val_1=5., val_2=8. ):
        """
        The difference between r_alpha and the measured ratio of the normalised photodiode
        readings at angles 125° and 165°.
        The method returns this difference squared to allow root finding through minimisation.

        kwargs have to be theta_1=float, theta_2=float, rho=float, val_1=float, val_2=float
        where val_1 and val_2 are the normalised photodiode readings at 125° and 165°,
        respectively.
        """
        r_a = self.r_alpha(alpha, theta_1=theta_1, theta_2=theta_2, rho=self.rho)
        r_x = val_1 / val_2
        f_a = r_x - r_a
        return f_a ** 2

    def calculate_alpha(self):
        """
        This method calculates the fraction of diffuse radiation in the backwards
        hemisphere following the approach developed by Petzold 2003. 
        The alpha calculated for each filter, for each wavelength is added to the dict 
        at the level of the angle key. So the dict after this step will look like this:
        self.data = {
                'filter_name': {
                        lambda: {
                                angle: {
                                        'gain': g,
                                        ('raw': np.array([...]) #unless it was deleted
                                        'dark': d,
                                        'mean': m,
                                        'norm: n
                                        },
                                'alpha': a
                                }
                        }
                }                       
        """
        status = 1
        theta_1_rad = (self.angles[1] / 360.) * 2 * np.pi
        theta_2_rad = (self.angles[2] / 360.) * 2 * np.pi
        m = AlphaMinimizer()
        m.set_bounds(0,1) # Alpha is a fraction
        m.set_function(self.f_alpha)
        for d in self.datalist:
            for fname in d.keys():
                for wlength in d[fname].keys():
                    x_1 = d[fname][wlength][125]['norm']
                    x_2 = d[fname][wlength][165]['norm']
                    args=(theta_1_rad, theta_2_rad, self.rho,
                            x_1, x_2) # The fixed arguments for each alpha minimization
                    res = m.do_minimization(args)
                    if not res[0]:
                        print('Minimizzazione non riuscita')
                        status = 0
                    else:
                        alpha = float(res[0])
                        d[fname][wlength]['alpha'] = alpha
                        #print(fname, wlength, alpha)
            if status == 0:
                return False
            else:
                return True

    def calculate_piscattered(self):
        """ 
        Calculates the amount of radiation scattered at 180° knowing alpha and the radiation scattered at 165°.  
        """ 
        self.calculate_alpha()
        theta_2_rad = (self.angles[2] / 360.) * 2 * np.pi
        for d in self.datalist:
            for f in d.keys():
                for w in d[f].keys():
                    alpha = d[f][w]['alpha']
                    #if w == 375 :
                    #    input((f, alpha))
                    S_165 = d[f][w][165]['norm']
                    cos = np.cos(theta_2_rad - np.pi)
                    exponent = -.5 * (((theta_2_rad - np.pi) ** 2) / self.rho ** 2)
                    exp = np.exp(exponent)
                    S_180 = S_165 / (alpha * cos + (1 - alpha) * exp)
                    d[f][w][180] = float(S_180) # Add to data dictionary

     
    def mwaa_style_integrate(self):
        """
        Calculates the integrals for the passed radiation and the backscattered radiation, and saves
        them in the data dictionary.
        """
        self.calculate_piscattered() # Radiation at 180°
        I_1 = 0.5  # Easy analytic integration
        theta = np.linspace(np.pi / 2, np.pi, 10000)
        exponent = - (((np.pi - theta) ** 2) / (2 * self.rho ** 2))
        int_2 = np.sin(theta) * np.exp(exponent)
        I_2 = np.trapz(int_2, x=theta) # ~= 0.3133175
        for d in self.datalist:
            for f in d.keys():
                for w in d[f].keys():
                    alpha = d[f][w]['alpha']
                    S_0 = d[f][w][0]['norm']
                    S_180 = d[f][w][180] #current
                    d[f][w]['p_f'] = float(I_1 * S_0 * self.fwd_corr)  # The passed radiation
                    d[f][w]['b_f'] = float(self.bck_corr * (S_180 * (alpha * I_1 + (1 - alpha) * I_2))) # The backscattered radiation
                    # DEBUG
                    #if w == 635:
                    #    print(f, alpha)
                    #    print(f, 'forward', d[f][w]['p_f'], 'backward', d[f][w]['b_f'])

                ###########################################################################
                # This integration has been verified manually and the results are correct #
                # at the wavelength of 635 nm                                             #
                ###########################################################################




##############################################
# WRITEOUT FUNCTIONS
##############################################

    def _csv_write(self):
        i = 0
        for data in self.datalist:
            if i == 0:
                with open(self.csv_fpath, 'w') as fwrite:
                    writer = csv.writer(fwrite)
                    header = ['Name', 'Type', 'Wavelength [nm]', 'P_f', 'B_f']
                    writer.writerow(header)
                    for fname in data.keys():
                        for wlength in data[fname].keys():
                            p_f, b_f = data[fname][wlength]['p_f'], data[fname][wlength]['b_f']
                            line = [fname, self.type, wlength, p_f, b_f]
                            writer.writerow(line)
            else:
                with open(self.csv_fpath, 'a') as fappend:
                    writer = csv.writer(fappend)
                    for fname in data.keys():
                        for wlength in data[fname].keys():
                            p_f, b_f = data[fname][wlength]['p_f'], data[fname][wlength]['b_f']
                            line = [fname, self.type, wlength, p_f, b_f]
                            writer.writerow(line)

            i += 1

    def csv_write(self):
        try:
            self._csv_write()
        except FileNotFoundError as fnfe:
            Path(self.outdir).mkdir(parents=True, exist_ok=True)
            self._csv_write()

    # STILL TO DO
    def _json_write(self):
        data_to_write = {}
        for data in self.datalist:
            # Join the dataset in a single dictionary
            data_to_write = data_to_write | data
        with open(self.json_fpath, 'w') as fwrite:
            json.dump(data_to_write, fwrite, indent=4)

    def json_write(self):
        try:
            self._json_write()
        except FileNotFoundError as fnfe:
            Path(self.outdir).mkdir(parents=True, exist_ok=True)
            self._json_write()


    ### Setters #########
    def set_lambdas(self, *args):
        """
        this function needs to be passed all the wavelengths at which the
        instrument operates. For example self.set_lambda(420, 546, 635)
        """
        self.wave = args
    
    def set_angles(self, *args):
        """
        this function needs to be passed all the wavelengths at which the
        instrument operates. For example self.set_angles(420, 546, 635)
        """
        self.angles = args

     
    ### Getters #######
    def get_names(self):
        """obsolete"""
        pass

    def get_wl(self):
        w = []
        for n in self.data.keys():
            for wl in self.data[n].keys():
                if wl not in w:
                    w.append(wl)
        return w

    def get_lambdas(self):
        """
        Returns a tuple containing the wavelengths at which the instrument operates.
        """
        lam = []
        try:
            name = list(self.data.keys())[0]
            for w in self.data[name].keys():
                lam.append(w)
            return lam
        except:
            print("ERROR: data not yet read from file, or problem reading data")

    def get_gains(self, wlength):
        """
        Returns a list containing the photodiode gains for the specified lambda.
        (assuming equal gains for all filters at a given wavelength).
        """
        gain = []
        try:
            name = list(self.data.keys())[0]
            for a in self.data[name][wlength].keys():
                gain.append(self.data[name][wlength][a]['gain'])
            return gain
        except:
            print("ERROR: data not yet read from file, or problem reading data")

    def get_mean(self, fname, wlength):
        """
        Returns a list containing the photodiode mean for the specified lambda 
        and filter name
        """
        mean = []
        try:
            name = fname
            for a in self.data[name][wlength].keys():
                mean.append(self.data[name][wlength][a]['mean'])
            return mean
        except:
            print("ERROR: data not yet read from file, problem reading data, or \
                    data not yet averaged using calculate_avg")

    def get_all_data(self):
        """
        Returns the entire data dictionary.
        """
        return self.datalist

    def get_one_data(self, f, wl):
        """
        UPDATE
        """
        return self.data[f][wl]

    def get_result(self, f, wl):
        """
        UPDATE
        """
        d = self.data
        return d[f][wl]['p_f'], d[f][wl]['b_f']



