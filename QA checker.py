import os
import csv
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.messagebox as messagebox
import re
import pprint

def show_help():
    messagebox.showinfo("Help", "The checker is meant to look at the calibration and calculate the Relative error of the "
                        "low and mid point for each element.\n\nV 1.0:\n* The checker only works with Elans CSV files. I'll add"
                        " Agilent's excel and ICP2's PRN files later if I feel like it\n"
                        "* The checker will only collect the data until it sees an ICV run, i.e. if you re-run a cal standard "
                        "after an ICV, the checker will not calculate the correct information.\n"
                        "* Some of the cal names and concentrations are hard coded, so if you change the names or "
                        "concentrations the checker will not work and I'm to lazy to make a more dynamic code. (Changing STD "
                        "ID numbers will not affect the checker)")

def open_file():
    filename = filedialog.askopenfilename()
    _, file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()  # Convert the file extension to lowercase
    if file_extension == '.csv':
        df = process_csv(filename)  # Call the existing process_csv() function
    elif file_extension == '.prn':
        df = pd.read_fwf(filename)
    elif file_extension == '.xlsx':
        df = pd.read_excel(filename)
    else:
        print("Unsupported file type")
        return None
    return df

def process_csv(filename):
    data = []
    with open(filename, 'r') as file:
        data = []
        for line in file:
            if 'SEQ-ICV' in line:
                break
            line = re.sub(r'@\d+', '', line).strip().lower()
            exclusions = ["dlz - summary report", "sample description:", "batch id:", "initial sample quantity (mg):",
                          "sample prep volume (ml):", "aliquot volume (ml):", "diluted to volume (ml):", "method file:",
                          "analyst  :", "intensities", "qc calculated values"]
            if not any(exclusion in line for exclusion in exclusions):
                data.append(line.split(','))
    df = pd.DataFrame(data)
    df = df.drop(df.columns[ [3, 4, 5 ] ], axis=1)
    df.columns = ['IS Group', 'Analyte', 'Mass #', 'Intensity']
    print(df)
    df = dictionaryCSV(df)
    return df

def dictionaryCSV(df):
    data = {}
    current_sample = None
    analytes_to_exclude = ['"li"', '"in"', '"bi"', '"ge"']
    pairs_to_exclude = [('"cal std 2"', '"al"'),('"cal std 2"', '"v"'),('"cal std 2"', '"cr"'),
                        ('"cal std 2"', '"mn"'),('"cal std 2"', '"fe"'),('"cal std 2"', '"co"'),
                        ('"cal std 2"', '"ni"'),('"cal std 2"', '"cu"'),('"cal std 2"', '"zn"'),
                        ('"cal std 2"', '"as"'),('"cal std 2"', '"se"'),('"cal std 2"', '"mo"'),
                        ('"cal std 2"', '"ag"'),('"cal std 2"', '"sb"'),('"cal std 2"', '"ba"'),
                        ('"cal std 2"', '"pb"'),
                        ('"cal std 3"', '"al"'),('"cal std 3"', '"v"'),('"cal std 3"', '"cr"'),
                        ('"cal std 3"', '"mn"'),('"cal std 3"', '"fe"'),('"cal std 3"', '"co"'),
                        ('"cal std 3"', '"ni"'),('"cal std 3"', '"zn"'),('"cal std 3"', '"se"'),
                        ('"cal std 3"', '"mo"'),('"cal std 3"', '"ag"'),('"cal std 3"', '"sb"'),
                        ('"cal std 3"', '"ba"'),
                        ('"cal std 4"', '"al"'),('"cal std 4"', '"v"'),('"cal std 4"', '"ni"'),
                        ('"cal std 4"', '"zn"'),('"cal std 4"', '"se"'),('"cal std 4"', '"sb"'),
                        ('"cal std 5"', '"se"')]
    for index, row in df.iterrows():
        if 'sample date/time:' in row['IS Group'].lower():
            continue  # Skip this row and continue to the next iteration
        if '"i/s"' in row['IS Group'].lower():
            continue  # Skip this row and continue to the next iteration
        elif 'sample id:' in row['IS Group'].lower():
            current_sample = row['Analyte']  # Get the sample label
            data[current_sample] = {'analytes': {}}
        elif current_sample is not None and row['Analyte'] is not None:
            if row['Analyte'].lower() in analytes_to_exclude or (current_sample, row['Analyte'].lower()) in pairs_to_exclude:
                continue  # Skip this row and continue to the next iteration
            analyte = row['Analyte']
            intensity = row['Intensity']
            data[current_sample]['analytes'][analyte] = intensity  # Add the analyte and intensity to the current sample

    expected_concentrations = {
    '"rinse"': {'be': 0, 'al': 0, 'v': 0, 'cr': 0, 'mn': 0, 'fe': 0, 'co': 0, 'ni': 0, 'cu': 0, 'zn': 0, 
                'as': 0, 'se': 0, 'mo': 0, 'ag': 0, 'cd': 0, 'sb': 0, 'ba': 0, 'pb': 0, 'tl': 0},

    '"cal std 1"': {'be': 0, 'al': 0, 'v': 0, 'cr': 0, 'mn': 0, 'fe': 0, 'co': 0, 'ni': 0, 'cu': 0, 'zn': 0, 'as': 0,
                  'se': 0, 'mo': 0, 'ag': 0, 'cd': 0, 'sb': 0, 'ba': 0, 'pb': 0, 'tl': 0},

    '"cal std 2"': {'be': 0.2, 'cd': 0.2, 'tl': 0.2},

    '"cal std 3"': {'be': 0.5, 'cu': 1, 'as': 0.5, 'cd' : 0.5, 'tl': 0.5, 'pb': 0.5},

    '"cal std 4"': {'be': 1, 'cr': 1, 'mn': 1, 'fe': 20, 'co': 1, 'cu': 2, 'as': 1,
                  'mo': 0.4, 'ag': 0.2, 'cd': 1, 'ba': 4, 'pb': 1, 'tl': 1},

    '"cal std 5"': {'be': 5, 'al': 50, 'v': 5, 'cr': 5, 'mn': 5, 'fe': 100, 'co': 5, 'ni': 5, 'cu': 10, 
                  'zn': 10, 'as': 5, 'mo': 2, 'ag': 1, 'cd': 5, 'sb': 1, 'ba': 20, 'pb': 5, 'tl': 5},

    '"cal std 6"': {'be': 10, 'al': 100, 'v': 10, 'cr': 10, 'mn': 10, 'fe': 200, 'co': 10, 'ni': 10, 'cu': 20, 
                  'zn': 20, 'as': 10, 'se': 4, 'mo': 4, 'ag': 2, 'cd': 10, 'sb': 2, 'ba': 40, 'pb': 10, 'tl': 10},

    '"cal std 7"': {'be': 50, 'al': 500, 'v': 50, 'cr': 50, 'mn': 50, 'fe': 1000, 'co': 50, 'ni': 50, 'cu': 100, 'zn': 100,
                    'as': 50, 'se': 20, 'mo': 20, 'ag': 10, 'cd': 50, 'sb': 10, 'ba': 200, 'pb': 50, 'tl': 50},

    '"cal std 8"': {'be': 100, 'al': 1000, 'v': 100, 'cr': 100, 'mn': 100, 'fe': 2000, 'co': 100, 'ni': 100, 'cu': 200,
                    'zn': 200, 'as': 100, 'se': 40, 'mo': 40, 'ag': 20, 'cd': 100, 'sb': 20, 'ba': 400, 'pb': 100, 'tl': 100},

    '"cal std 9"': {'be': 500, 'al': 5000, 'v': 500, 'cr': 500, 'mn': 500, 'fe': 10000, 'co': 500, 'ni': 500, 'cu': 1000,
                    'zn': 1000, 'as': 500, 'se': 200, 'mo': 200, 'ag': 100, 'cd': 500, 'sb': 100, 'ba': 2000, 'pb': 500, 'tl': 500},
    }

    '''   
    # Add expected concentrations to df
    for std in df.keys():
        if std in expected_concentrations:  # Check if the standard is in the expected_concentrations dictionary
            for analyte in df[std]['analytes'].keys():
                try:
                    expected_concentration = expected_concentrations[std][analyte]
                except KeyError:
                    expected_concentration = 0  # or some other default value
                df[std]['analytes'][analyte] = {
                    'measured_intensity': df[std]['analytes'][analyte],
                    'expected_concentration': expected_concentration
                }
    '''
    return data


def open_file():
    filename = filedialog.askopenfilename()
    _, file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()  # Convert the file extension to lowercase
    if file_extension == '.csv':
        df = process_csv(filename)  # Call the existing process_csv() function
        #print('dictonary', (df))
        pprint.pprint(df)
    elif file_extension == '.prn':
        df = pd.read_fwf(filename)
    elif file_extension == '.xlsx':
        df = pd.read_excel(filename)
    else:
        print("Unsupported file type")
        return None
    return df

def create_gui():
    root = tk.Tk()
    root.title("Super Secret QC Tool")
    root.geometry("300x200")

    # Create a frame for the buttons
    frame = tk.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor='center')

    # Create the "Open File" button
    open_button = tk.Button(frame, text="Calibration Check", command=open_file, relief=tk.RAISED)
    open_button.grid(row=0, column=0, padx=10, pady=10)

    # Create the "Read Me" button
    help_button = tk.Button(frame, text="Read Me", command=show_help, relief=tk.RAISED)
    help_button.grid(row=0, column=1, padx=10, pady=10)

    # Create the "Quit" button
    quit_button = tk.Button(frame, text="Quit", command=root.quit, relief=tk.RAISED, fg="red")
    quit_button.grid(row=0, column=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()