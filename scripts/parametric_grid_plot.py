import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np


# Define the root directory containing the subdirectories with CSV files
root_directory = './results'

# Initialize dictionaries to store data
data = {'True': [], 'False': [], 'One_step': [], 'Two_step': []}

# Recursively traverse through the root directory to find all relevant directories
for subdir, _, files in os.walk(root_directory):
    if 'results.csv' in files:
        # Extract time step from directory name (assuming it's in the format '...-time_steps')
        match = re.search(r'-(\d+)_steps', subdir)
        if match:
            timestep = int(match.group(1))
            # Read the CSV file
            df = pd.read_csv(os.path.join(subdir, 'results.csv'))

            # Group by reduction status and compute the average objective and runtime
            grouped = df.groupby('reduction').agg({'objective': 'mean', 'runtime': 'mean'}).reset_index()

            for _, row in grouped.iterrows():
                data[str(row['reduction'])].append({'timestep': timestep, 'objective': row['objective'], 'runtime': row['runtime']})
    if 'results_1_step.csv' in files:
        # Extract time step from directory name (assuming it's in the format '...-time_steps')
        match = re.search(r'-(\d+)_steps', subdir)
        if match:
            timestep = int(match.group(1))
            # Read the CSV file
            df = pd.read_csv(os.path.join(subdir, 'results_1_step.csv'))

            # Group by reduction status and compute the average objective and runtime
            grouped = df.groupby('reduction').agg({'objective': 'mean', 'runtime': 'mean'}).reset_index()

            for _, row in grouped.iterrows():
                data['One_step'].append({'timestep': timestep, 'objective': row['objective'], 'runtime': row['runtime']})
    if 'results_2_step.csv' in files:
        # Extract time step from directory name (assuming it's in the format '...-time_steps')
        match = re.search(r'-(\d+)_steps', subdir)
        if match:
            timestep = int(match.group(1))
            # Read the CSV file
            df = pd.read_csv(os.path.join(subdir, 'results_2_step.csv'))

            # Group by reduction status and compute the average objective and runtime
            grouped = df.groupby('reduction').agg({'objective': 'mean', 'runtime': 'mean'}).reset_index()

            for _, row in grouped.iterrows():
                data['Two_step'].append({'timestep': timestep, 'objective': row['objective'], 'runtime': row['runtime']})

# Convert lists to DataFrames
two_reduction_data = pd.DataFrame(data['True']).sort_values(by='timestep')
no_reduction_data = pd.DataFrame(data['False']).sort_values(by='timestep')
one_reduction_data = pd.DataFrame(data['One_step']).sort_values(by='timestep')
one_reduction_two_depth_data = pd.DataFrame(data['Two_step']).sort_values(by='timestep')

# Function to identify outliers using IQR
def identify_outliers(df, column):
    Q1 = df[column].quantile(0.10)
    Q3 = df[column].quantile(0.90)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] < lower_bound) | (df[column] > upper_bound)].index

# Identify outliers in no_reduction_data
outliers_indices = identify_outliers(no_reduction_data, 'runtime')

# Remove these outliers from both two_reduction_data and no_reduction_data
two_reduction_data = two_reduction_data.drop(index=outliers_indices)
no_reduction_data = no_reduction_data.drop(index=outliers_indices)
one_reduction_data = one_reduction_data.drop(index=outliers_indices)
one_reduction_two_depth_data = one_reduction_two_depth_data.drop(index=outliers_indices)


plt.figure(figsize=(12, 6))

# Plot for reduction = true
plt.scatter(two_reduction_data['objective'], two_reduction_data['runtime'], label='2 reduction steps', marker='o')

# Plot for reduction = false
plt.scatter(no_reduction_data['objective'], no_reduction_data['runtime'], label='No reduction', marker='o')

plt.scatter(one_reduction_data['objective'], one_reduction_data['runtime'], label='1 reduction step', marker='o')

plt.scatter(one_reduction_two_depth_data['objective'], one_reduction_two_depth_data['runtime'], label='1 reduction step 2 deep', marker='o')

# Add labels and legend
plt.xlabel('Objective Function')
plt.ylabel('Runtime')
plt.title('Objective Function vs Runtime with Time Step Annotations')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()

plt.figure(figsize=(12, 6))

# Plot for reduction = true
plt.plot(two_reduction_data['timestep'], two_reduction_data['objective'] / two_reduction_data['timestep'], label='2 reduction steps', marker='o')

# Plot for reduction = false
plt.plot(no_reduction_data['timestep'], no_reduction_data['objective'] / no_reduction_data['timestep'], label='No reduction steps', marker='o')

plt.plot(one_reduction_data['timestep'], one_reduction_data['objective'] / one_reduction_data['timestep'], label='1 reduction step', marker='o')

plt.plot(one_reduction_two_depth_data['timestep'], one_reduction_two_depth_data['objective'] / one_reduction_two_depth_data['timestep'], label='1 reduction step 2 deep', marker='o')

# Add labels and legend
plt.xlabel('Time Step')
plt.ylabel('Objective Function')
plt.title('Objective Function over Time Steps')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()

plt.figure(figsize=(12, 6))

# Plot for reduction = true
plt.plot(two_reduction_data['timestep'], two_reduction_data['runtime']/two_reduction_data['timestep'], label='2 reduction steps', marker='o')

# Plot for reduction = false
plt.plot(no_reduction_data['timestep'], no_reduction_data['runtime']/no_reduction_data['timestep'], label='No reduction steps', marker='o')

plt.plot(one_reduction_data['timestep'], one_reduction_data['runtime']/one_reduction_data['timestep'], label='1 reduction step', marker='o')

plt.plot(one_reduction_two_depth_data['timestep'], one_reduction_two_depth_data['runtime'] / one_reduction_two_depth_data['timestep'], label='1 reduction step 2 deep', marker='o')

# Add labels and legend
plt.xlabel('Time Step')
plt.ylabel('Runtime')
plt.title('Runtime over Time Steps')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()


# Merge dataframes on 'timestep' for correct alignment
# Merge dataframes on 'timestep' for correct alignment
merged_data = pd.merge(two_reduction_data, no_reduction_data, on='timestep', suffixes=('_2step', '_noreduction'))
merged_data = pd.merge(merged_data, one_reduction_data, on='timestep')
merged_data = pd.merge(merged_data, one_reduction_two_depth_data, on='timestep', suffixes=('_1step', '_1step_2deep'))

# Explicitly rename columns for clarity and consistency
merged_data.rename(columns={
    'objective': 'objective_1step', 
    'runtime': 'runtime_1step',
    'objective_2step': 'objective_2step',
    'runtime_2step': 'runtime_2step',
    'objective_noreduction': 'objective_noreduction',
    'runtime_noreduction': 'runtime_noreduction',
    'objective_1step_2deep': 'objective_1step_2deep',
    'runtime_1step_2deep': 'runtime_1step_2deep'
}, inplace=True)
def calculate_percentage_increase(new_values, original_values):
    with np.errstate(divide='ignore', invalid='ignore'):
        percentage_increase = np.where(original_values != 0, ((new_values / original_values) * 100) - 100, 0)
    return percentage_increase

merged_data['objective_increase_2step'] = calculate_percentage_increase(merged_data['objective_2step'], merged_data['objective_noreduction'])
merged_data['objective_increase_1step'] = calculate_percentage_increase(merged_data['objective_1step'], merged_data['objective_noreduction'])
merged_data['objective_increase_1step_2deep'] = calculate_percentage_increase(merged_data['objective_1step_2deep'], merged_data['objective_noreduction'])

plt.figure(figsize=(12, 6))

# # Plot for reduction = true
plt.plot(merged_data['timestep'], merged_data['objective_increase_2step'], label='Value of the increase 2 steps', marker='o')
plt.plot(merged_data['timestep'], merged_data['objective_increase_1step'], label='Value of the increase 1 step', marker='o')
plt.plot(merged_data['timestep'], merged_data['objective_increase_1step_2deep'], label='Value of the increase 1 step 2 deep', marker='o')


# # Add labels and legend
plt.xlabel('Time Step')
plt.ylabel('Percentage Increase in Objective Function')
plt.title('Percentage Increase in Objective Function over Time Steps')
plt.legend()
plt.grid(True)

plt.show()

merged_data['runtime_increase_2step'] = calculate_percentage_increase(merged_data['runtime_2step'], merged_data['runtime_noreduction'])
merged_data['runtime_increase_1step'] = calculate_percentage_increase(merged_data['runtime_1step'], merged_data['runtime_noreduction'])
merged_data['runtime_increase_1step_2deep'] = calculate_percentage_increase(merged_data['runtime_1step_2deep'], merged_data['runtime_noreduction'])

plt.figure(figsize=(12, 6))

# Plot percentage increase in runtime
plt.plot(merged_data['timestep'], merged_data['runtime_increase_2step'], label='Value of the increase 2 steps', marker='o')
plt.plot(merged_data['timestep'], merged_data['runtime_increase_1step'], label='Value of the increase 1 step', marker='o')
plt.plot(merged_data['timestep'], merged_data['runtime_increase_1step_2deep'], label='Value of the increase 1 step 2 deep', marker='o')

# Add labels and legend
plt.xlabel('Time Step')
plt.ylabel('Percentage Increase in Runtime')
plt.title('Percentage Increase in Runtime over Time Steps')
plt.legend()
plt.grid(True)

plt.show()