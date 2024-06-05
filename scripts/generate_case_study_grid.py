import pandas as pd
import numpy as np
import toml
import os

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

def create_tomls(path, inputpath):
    with open(inputpath + 'scalars.toml', 'w+') as f:
        f.write("""# Value of lost load (cost of not supplying energy) [kEUR/MWh]
                    value_of_lost_load = 3.0
                    # If true, an LP relaxation of the problem will be solved
                    relaxation = false
                    """)
        
    with open(path + 'config.toml', 'w+') as f:
        f.write(f"""[input.data]
                # input directory with the files
                dir = "inputs"
                demand = "demand.csv"
                generation_availability = "generation_availability.csv"
                generation = "generation.csv"
                transmission_lines = "transmission_lines2.csv"
                scalars = "scalars.toml"
                line_capacities_bidirectional = false
                clusters = "auto"
                [input.sets]
                time_steps = "auto"
                locations = "auto"
                transmission_lines = "auto"
                generators = "auto"
                [output]
                dir = "output"
                investment = "investment.csv"
                production = "production.csv"
                line_flow = "line_flow.csv"
                loss_of_load = "loss_of_load.csv"
                scalars = "scalars.toml"
                                """)

#generates all the instances of possible parameters
def generate(time, yeartime, gridsize, seed):
    folder = f'./case_studies/grid_{seed}/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = folder + f'{time}_steps/'
    if not os.path.exists(path):
        os.makedirs(path)
    inputpath = path + 'inputs/'
    if not os.path.exists(inputpath):
        os.makedirs(inputpath)
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
    demand_df.to_csv(inputpath + 'demand.csv', index=False)

    technologies = ['Gas']

    #Add generation availability, which is nothing as of now.
    generation_availability_data = []
    generation_availability_df = pd.DataFrame(generation_availability_data, columns=['location', 'technology', 'time_step', 'availability'])
    generation_availability_df.to_csv(inputpath + 'generation_availability.csv', index=False)

    #Add generation data
    generation_data = []
    for technology in technologies:
        for location in locations:
            investment_cost = 23.33333 * (time/yeartime)
            variable_cost = 0.05
            unit_capacity = 250
            ramping_rate = 0.75
            generation_data.append([technology, location, investment_cost, variable_cost, unit_capacity, ramping_rate])
            
    # Create DataFrame for generation characteristics
    generation_df = pd.DataFrame(generation_data, columns=['technology', 'location', 'investment_cost', 'variable_cost', 'unit_capacity', 'ramping_rate'])
    generation_df.to_csv(inputpath + 'generation.csv', index=False)

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
    transmission_df.to_csv(inputpath + 'transmission_lines.csv', index=False)
    
    create_tomls(path, inputpath)

    # Load the existing configuration
    config_path = path + 'config.toml'
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

    df_combined.to_csv(inputpath + 'transmission_lines2.csv', index=False)

if __name__ == '__main__':
    seed = 600
    np.random.seed(seed)
    #set the gridsize you want
    gridsize = 16
    yeartime = 8760

    for i in range(50, 1001, 50):
        generate(i, yeartime, gridsize, seed)