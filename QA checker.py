import os
import csv
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.messagebox as messagebox

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
        for line in file:
            # If the line contains the particular string, stop reading the file
            if 'SEQ-ICV' in line:
                break
            line = line.strip().lower()
            if not any(exclusion in line for exclusion in ["dlz - summary report",
                                                           "sample description:",
                                                           "batch id:",  
                                                           "initial sample quantity (mg):", 
                                                           "sample prep volume (ml):",
                                                           "aliquot volume (ml):",
                                                           "diluted to volume (ml):",
                                                            "method file:",
                                                            "analyst  :",
                                                            "intensities", 
                                                            "qc calculated values"]):
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
    pairs_to_exclude = [('"cal std 2@2305748"', '"al"')]  # Replace with the actual sample-analyte pairs to exclude
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
    return data


def open_file():
    filename = filedialog.askopenfilename()
    _, file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()  # Convert the file extension to lowercase
    if file_extension == '.csv':
        df = process_csv(filename)  # Call the existing process_csv() function
        print('dictonary')
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

    # Create the "Help" button
    help_button = tk.Button(frame, text="Read Me", command=show_help, relief=tk.RAISED)
    help_button.grid(row=0, column=1, padx=10, pady=10)

    # Create the "Quit" button
    quit_button = tk.Button(frame, text="Quit", command=root.quit, relief=tk.RAISED, fg="red")
    quit_button.grid(row=0, column=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()