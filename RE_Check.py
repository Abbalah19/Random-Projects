import pandas as pd
import numpy as np

data = []
with open('110623.CSV', 'r') as file:
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

# Create a list of the desired analyte names
desired_analytes = ['be', 'al', 'v', 'cr', 'mn', 'fe', 'co',
                    'ni', 'cu', 'zn', 'as', 'se', 'mo', 'ag',
                    'cd', 'sb', 'ba', 'pb']

# Create dictionary
intensity_values = {}

# Convert the 'Intensity' column to numeric
df['Intensity'] = pd.to_numeric(df['Intensity'], errors='coerce')

# Remove double quotes from 'Analyte' column
df['Analyte'] = df['Analyte'].str.replace('"', '')

# Go through each row
for index, row in df.iterrows():
    analyte = row['Analyte']
    # If the 'Analyte' column is one of the desired analytes and is not in the dictionary, add it with an empty list as the value
    if analyte in desired_analytes and analyte not in intensity_values:
        intensity_values[analyte] = []
    # If the 'Analyte' column is one of the desired analytes and the 'Intensity' value is not NaN, add the 'Intensity' column result to the list for this analyte
    elif analyte in desired_analytes and not np.isnan(row['Intensity']):
        intensity_values[analyte].append(row['Intensity'])

# Convert the lists to numpy arrays
for analyte in intensity_values:
    intensity_values[analyte] = np.array(intensity_values[analyte])

# Print each array on its own line
for analyte, intensity in intensity_values.items():
    print(f"{analyte}: {intensity}\n")