import os
import pandas as pd

# Define the root directory containing the subfolders
root_dir = 'results'

# Initialize a list to store the results
results = []

# Loop over each subfolder in the root directory
for subfolder in os.listdir(root_dir):
    subfolder_path = os.path.join(root_dir, subfolder)
    if os.path.isdir(subfolder_path):
        # Parse the subfolder name
        parts = subfolder.split('_')
        datetime_part = parts[0]
        method_name = parts[1].split('[')[0]
        num_reduction_steps = int(parts[1].split('[')[1].split(']')[0])
        time_steps = int(parts[2])
        bound_alpha_factor = float(parts[3])
        scenario = parts[4]

        # Path to the results.csv file
        csv_file = os.path.join(subfolder_path, 'results.csv')

        # Read the CSV file
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            
            # Filter rows where reduction is true
            df_reduction = df[df['reduction'] == True]
            
            # Calculate the mean and standard deviation of runtime for reduction
            mean_runtime_reduction = df_reduction['runtime'].mean()
            std_runtime_reduction = df_reduction['runtime'].std()
            
            # Calculate the mean objective for reduction
            mean_objective_reduction = df_reduction['objective'].mean()

            # Filter rows where reduction is false (baseline)
            df_baseline = df[df['reduction'] == False]
            
            # Calculate the mean and standard deviation of runtime for baseline
            mean_runtime_baseline = df_baseline['runtime'].mean()
            std_runtime_baseline = df_baseline['runtime'].std()
            
            # Calculate the mean objective for baseline
            mean_objective_baseline = df_baseline['objective'].mean()

             # Calculate the percentual reduction in runtime
            if mean_runtime_baseline > 0:
                percentual_reduction_runtime = ((mean_runtime_baseline - mean_runtime_reduction) / mean_runtime_baseline) * 100
            else:
                percentual_reduction_runtime = 0  # Avoid division by zero

            # Append the results to the list
            results.append([method_name, num_reduction_steps, time_steps, bound_alpha_factor, scenario, 
                            mean_runtime_reduction, std_runtime_reduction, mean_objective_reduction,
                            mean_runtime_baseline, std_runtime_baseline, mean_objective_baseline, percentual_reduction_runtime])

# Convert the results list to a DataFrame
results_df = pd.DataFrame(results, columns=['method_name', 'num_reduction_steps', 'time_steps', 'bound_alpha_factor', 'scenario', 
                                            'mean_runtime_reduction', 'std_runtime_reduction', 'mean_objective_reduction',
                                            'mean_runtime_baseline', 'std_runtime_baseline', 'mean_objective_baseline', 'percentual_reduction_runtime'])

# Save the results to a CSV file
output_file = 'eu_results.csv'
results_df.to_csv(output_file, index=False)