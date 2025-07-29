# OPTSYS quick start guide

## Installation

In a Linux terminal, create a virtual environment:

    python3 -m venv optsys
This will create a virtual environment where you can install the software without affecting any other installation present in the system; to activate the environment:

    source optsys/bin/activate
To make the activation automatic on login, you have to modify the terminal configuration file .bashrc. Open it with any text editor (create it if it doesn't exist) and write this line at the bottom: `source optsys/bin/activate`

Once the environment is activated, you can install the software with the following command:

    python3 -m pip install optsys

The environment needs to be activated any time you want to use the toolkit.

## Calculating the integrals for MWAA

You need an .xls(x) file for the loaded filters `black.xlsx`, an .xls(x) file for the blank reference `white.xlsx`, an .xlsx gain and dark file `gd.xlsx` (the files can have any name, the names I wrote here are just as an example). You also need to create a folder to store all the output of the calculations, `results/`. The black, white and gains files have to follow exactly the provided templates. 

The command for this step is:

    mpre -b black.xlsx -w white.xlsx -g gd.xlsx -o results/ --name analysis_name
The integrals for the black and white filters will be saved in the results/ folder, in a human-readable .csv format and in a machine-readable .json format (which the ABS calculation routine will use as input).

## Calculating the integrals for BLAnCA

You need an .xlsx file for the loaded filters `black.xlsx`, with multiple tabs. Each tab contains the spectra for a filter, and its name corresponds to the filter name. Another file for the blank reference `white.xlsx`, with only one tab. If in doubt, check the provided templates.

The command for this step is:

    bpre -b black.xlsx -w white.xlsx -o results/ --name analysis_name
where results/ is the folder for the output (it does not need to be created in advance, unlike the MWAA case).  The integrals for the black and white filters will be saved in the results/ folder, in a human-readable .csv format and in a machine-readable .json format (which the ABS calculation routine will use as input).

## ABS minimization

The integral calculation for MWAA and BLAnCA produce an output in the same exact format, so they can be both used for the same minimization procedure. Like previous versions, the configuration for this step is contained in a JSON file, that has to contain all the keywords as the provided template. Generally, the only options that you will need to change are the following:

| **key** | **type** | **explanation** |
|---|---|---|
| b_integrals | string | The (relative) path to the black integrals file. |
| w_integrals | string | The (relative) path to the black integrals file. |
| out_folder | string | The (relative) path to the output folder. |
| name | string | The analysis name. |
| tolerance | float | The tolerance for the minimization. The default value of 1e-3 is good enough in most cases. |

Start the analysis with
    
    abs config.json
where `config.json` is the path to the configuration file.
