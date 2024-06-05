import pandas as pd
import numpy as np
import toml

#assume gridsize = a squared number of 2^x for integers x
def create_clusters(locations, grid_size):
    clusters = []
    if grid_size == 4:
        for loc in locations:
            clusters.append([loc])
        return clusters
    
    new_grid_size = int(grid_size/4)
    new_locations = []
    for i in range(1, 5):
        loc_i = []
        new_locations.append(loc_i)
    for (j, loc) in enumerate(locations):
        col = int(np.sqrt(grid_size)) #column length
        size = grid_size / 2
        k = (j + 1) % col
        if ((k <= col / 2 and k != 0) and j + 1 <= size):
            new_locations[0].append(loc)
        elif (k <= col / 2 and k != 0):
            new_locations[2].append(loc)
        elif (j + 1 <= size):
            new_locations[1].append(loc)
        else:
            new_locations[3].append(loc)
    
    for new_loc in new_locations:
        clusters.append(create_clusters(new_loc, new_grid_size))
        
    return clusters

# grid_size is expected to be a squared number of 2^x for integers x
# loc_index is the index of the location for which you want to neighbors
def get_neighbors(loc_index, grid_size):
    neighbors = []
    n = int(np.sqrt(grid_size))
    if (loc_index % n != 0):
        neighbors.append(loc_index + 1)
    if (loc_index + n <= grid_size):
        neighbors.append(loc_index + n)
    
    return neighbors

np.random.seed(42)
#set the gridsize you want
gridsize = 64
time = 500
year_time = 8760


# New parameters
locations = [f'l{i}' for i in range(1, gridsize + 1)]
time_steps = list(range(1, time + 1))

create_clusters(locations, gridsize)

# Generate new demand data
demand_data = []
initial_demand = np.random.uniform(3000, 8000, size=len(locations))

for i, location in enumerate(locations):
    demand = initial_demand[i]
    for time_step in time_steps:
        demand_data.append([location, time_step, demand])
        change = np.random.uniform(-500, 500)
        demand = max(3000, min(8000, demand + change))

# add the demand file to the grid case study
demand_df = pd.DataFrame(demand_data, columns=['location', 'time_step', 'demand'])
demand_df.to_csv(f'./case_studies/grid/{time}_steps/inputs/demand.csv', index=False)

technologies = ['Gas']

#Add generation availability, which is nothing as of now.
generation_availability_data = []
generation_availability_df = pd.DataFrame(generation_availability_data, columns=['location', 'technology', 'time_step', 'availability'])
generation_availability_df.to_csv(f'case_studies/grid/{time}_steps/inputs/generation_availability.csv', index=False)

#Add generation data
generation_data = []
for technology in technologies:
    for location in locations:
        investment_cost = 23.33333 * (time/year_time)
        variable_cost = 0.05
        unit_capacity = 250
        ramping_rate = 0.75
        generation_data.append([technology, location, investment_cost, variable_cost, unit_capacity, ramping_rate])

# Create DataFrame for generation characteristics
generation_df = pd.DataFrame(generation_data, columns=['technology', 'location', 'investment_cost', 'variable_cost', 'unit_capacity', 'ramping_rate'])
generation_df.to_csv(f'case_studies/grid/{time}_steps/inputs/generation.csv', index=False)

# Generate new transmission data
transmission_data = []

for i, location in enumerate(locations):
    neighbors = get_neighbors(i+1, gridsize)
    for neighbor in neighbors:
        neighbor_location = f'l{neighbor}'
        export_capacity = 2000
        import_capacity = 2000
        transmission_data.append([location, neighbor_location, export_capacity, import_capacity])
        
# Create DataFrame for transmission lines
transmission_df = pd.DataFrame(transmission_data, columns=['from', 'to', 'export_capacity', 'import_capacity'])
transmission_df.to_csv(f'case_studies/grid/{time}_steps/inputs/transmission_lines.csv', index=False)


# Load the existing configuration
config_path = f"./case_studies/grid/{time}_steps/config.toml"
with open(config_path, 'r') as file:
    config = toml.load(file)
    
# Update the time_steps
config['input']['sets']['time_steps'] = time_steps

#update clusters
config['input']['data']['clusters'] = create_clusters(locations, gridsize)

# Save the updated configuration
with open(config_path, 'w') as file:
    toml.dump(config, file)


df_export = transmission_df[["from", "to", "export_capacity"]]
df_export = df_export.rename(columns={"export_capacity": "capacity"})

df_import = transmission_df[["to", "from", "import_capacity"]]
df_import = df_import.rename(columns={"import_capacity": "capacity", "from": "to", "to": "from"})

df_combined = pd.concat([df_import, df_export])

df_combined.to_csv(f"case_studies/grid/{time}_steps/inputs/transmission_lines2.csv", index=False)

