import pandas as pd
import numpy as np

# grid_size is expected to be a squared number of 2^x for integers x
# loc_index is the index of the location for which you want to neighbors
def get_neighbors(loc_index, grid_size=4):
    neighbors = []
    n = int(np.sqrt(grid_size))
    if (loc_index % n != 0):
        neighbors.append(loc_index + 1)
    if (loc_index + n <= grid_size):
        neighbors.append(loc_index + n)
    
    return neighbors

np.random.seed(42)
#set the gridsize you want
gridsize = 16

# New parameters
new_locations = [f'l{i}' for i in range(1, gridsize + 1)]
new_time_steps = list(range(1, 1001))

# Generate new demand data
new_demand_data = []
initial_demand = np.random.uniform(3000, 8000, size=len(new_locations))

for i, location in enumerate(new_locations):
    demand = initial_demand[i]
    for time_step in new_time_steps:
        new_demand_data.append([location, time_step, demand])
        change = np.random.uniform(-500, 500)
        demand = max(3000, min(8000, demand + change))

# add the demand file to the grid case study
new_demand_df = pd.DataFrame(new_demand_data, columns=['location', 'time_step', 'demand'])
new_demand_df.to_csv('case_studies/grid/new_demand.csv', index=False)

new_technologies = ['Gas']

#Add generation availability, which is nothing as of now.
new_generation_availability_data = []
new_generation_availability_df = pd.DataFrame(new_generation_availability_data, columns=['location', 'technology', 'time_step', 'availability'])
new_generation_availability_df.to_csv('case_studies/grid/new_generation_availability.csv', index=False)

#Add generation data
new_generation_data = []
for technology in new_technologies:
    for location in new_locations:
        investment_cost = 23.33333
        variable_cost = 0.05
        unit_capacity = 250
        ramping_rate = 0.75
        new_generation_data.append([technology, location, investment_cost, variable_cost, unit_capacity, ramping_rate])

# Create DataFrame for generation characteristics
new_generation_df = pd.DataFrame(new_generation_data, columns=['technology', 'location', 'investment_cost', 'variable_cost', 'unit_capacity', 'ramping_rate'])
new_generation_df.to_csv('case_studies/grid/new_generation.csv', index=False)

# Generate new transmission data
new_transmission_data = []

for i, location in enumerate(new_locations):
    neighbors = get_neighbors(i+1, grid_size=gridsize)
    for neighbor in neighbors:
        neighbor_location = f'l{neighbor}'
        export_capacity = 2000
        import_capacity = 2000
        new_transmission_data.append([location, neighbor_location, export_capacity, import_capacity])
        
# Create DataFrame for transmission lines
new_transmission_df = pd.DataFrame(new_transmission_data, columns=['from', 'to', 'export_capacity', 'import_capacity'])
new_transmission_df.to_csv('case_studies/grid/new_transmission_lines.csv', index=False)




