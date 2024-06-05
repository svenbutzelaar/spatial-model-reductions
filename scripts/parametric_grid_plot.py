import os
import pandas as pd
import matplotlib.pyplot as plt
import re

# Define the root directory containing the subdirectories with CSV files
root_directory = './results'

# Initialize dictionaries to store data
data = {'True': [], 'False': []}
time_steps = []

# Recursively traverse through the root directory to find all relevant directories
for subdir, _, files in os.walk(root_directory):
    if 'results.csv' in files:
        # Extract time step from directory name (assuming it's in the format '...-time_steps')
        match = re.search(r'-(\d+)_steps', subdir)
        if match:
            timestep = int(match.group(1))
            time_steps.append(timestep)

            # Read the CSV file
            df = pd.read_csv(os.path.join(subdir, 'results.csv'))

            # Group by reduction status and compute the average objective and runtime
            grouped = df.groupby('reduction').agg({'objective': 'mean', 'runtime': 'mean'}).reset_index()

            for _, row in grouped.iterrows():
                data[str(row['reduction'])].append({'timestep': timestep, 'objective': row['objective'], 'runtime': row['runtime']})

# Convert lists to DataFrames
true_data = pd.DataFrame(data['True']).sort_values(by='timestep')
false_data = pd.DataFrame(data['False']).sort_values(by='timestep')

# Plot the data
plt.figure(figsize=(12, 6))

# Plot for reduction = true
plt.plot(true_data['objective'], true_data['runtime'], label='Reduction = True', marker='o')
for _, row in true_data.iterrows():
    plt.annotate(row['timestep'], (row['objective'], row['runtime']))

# Plot for reduction = false
plt.plot(false_data['objective'], false_data['runtime'], label='Reduction = False', marker='o')
for _, row in false_data.iterrows():
    plt.annotate(row['timestep'], (row['objective'], row['runtime']))

# Add labels and legend
plt.xlabel('Objective Function')
plt.ylabel('Runtime')
plt.title('Objective Function vs Runtime with Time Step Annotations')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()

# Plot for reduction = true
plt.plot(true_data['timestep'], true_data['objective'], label='Reduction = True', marker='o')

# Plot for reduction = false
plt.plot(false_data['timestep'], false_data['objective'], label='Reduction = False', marker='o')

# Add labels and legend
plt.xlabel('Time Step')
plt.ylabel('Objective Function')
plt.title('Objective Function over Time Steps')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()

# Plot for reduction = true
plt.plot(true_data['timestep'], true_data['runtime'], label='Reduction = True', marker='o')

# Plot for reduction = false
plt.plot(false_data['timestep'], false_data['runtime'], label='Reduction = False', marker='o')

# Add labels and legend
plt.xlabel('Time Step')
plt.ylabel('Runtime')
plt.title('Runtime over Time Steps')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()