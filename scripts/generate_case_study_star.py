import os
import numpy as np
from math import log2, ceil
from technologies import add_generation_and_generation_availability

def get_clusters(locations):
    if len(locations) == 0:
        return []
    if len(locations) == 1:
        return locations[0]
    clustered_locations = []
    for i in range(0, len(locations), 2):
        if i + 1 >= len(locations):
            clustered_locations.append([locations[i]])
        else:            
            clustered_locations.append([locations[i], locations[i+1]])
    return get_clusters(clustered_locations)


def create_middle_cluster(n):
    return f"l{0}" if n == 0 else [create_middle_cluster(n-1)]
    
    
def create_star_case_study(name, chain_length, degrees, time_steps, alpha):
    folder = f'case_studies/{name}/'

    # Create folders
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = folder + f'{time_steps}_steps/'
    if not os.path.exists(path):
        os.makedirs(path)
    input_folder = path + 'inputs/'
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    
    np.random.seed(42)
    
    total_locations = chain_length*degrees  + 1
    chains = []
    locations = [f"l{i}" for i in range(total_locations)]
    for i in range(1, total_locations, chain_length):
        chain = [[locations[i + x]] for x in range(chain_length)]
        chain_clusters = get_clusters(chain)
        chains.append(chain_clusters)
    assert len(chains) == degrees
    depth_chain_clusters = ceil(chain_length/2) + 1
    
    clusters = [create_middle_cluster(depth_chain_clusters)]
    clusters.extend(chains)
        
    # Demands
    initial_demand = np.random.uniform(3000, 8000, size=total_locations)
    demands = ["location,time_step,demand"]
    for location in range(total_locations):
        for time_step in range(1, time_steps):
            change = change = np.random.uniform(-500, 500)
            demands.append(f"l{location},{time_step},{initial_demand[location] + change}")

    with open(f'{input_folder}/demand.csv', 'w+') as f:
        f.write('\n'.join(demands) + '\n')


    # Generation availability
    generation_av = ["location,technology,time_step,availability"]
    # TODO add generation availability
    with open(f'{input_folder}/generation_availability.csv', 'w+') as f:
        f.write('\n'.join(generation_av) + '\n')


    # add_generation_and_generation_availability(total_locations, name, time_steps)
    
    # Generation
    generation = ["technology,location,investment_cost,variable_cost,unit_capacity,ramping_rate"]
    investment_factor = time_steps / 8760
    for location in range(total_locations):
        generation.append(f"Gas,l{location},{investment_factor * 23.33333333},0.05,250,0.75")

    with open(f'{input_folder}/generation.csv', 'w+') as f:
        f.write('\n'.join(generation) + '\n')

    # transmission_lines
    transmission_lines = ["from,to,capacity"]
    for i in range(1, total_locations, chain_length):
        transmission_lines.append(
            f"l{0},l{i},{np.random.uniform(500, 5000)}"
        )
        for j in range(0, chain_length-1):
            transmission_lines.append(
                f"l{i+j},l{i+j+1},{np.random.uniform(500, 5000)}"
            )            

    with open(f'{input_folder}/transmission_lines2.csv', 'w+') as f:
        f.write("\n".join(transmission_lines))

    with open(f'{input_folder}/scalars.toml', 'w+') as f:
        f.write("""# Value of lost load (cost of not supplying energy) [kEUR/MWh]
value_of_lost_load = 3.0
# If true, an LP relaxation of the problem will be solved
relaxation = false
    """)

    with open(f'{path}/config.toml', 'w+') as f:
        f.write(f"""[input.data]
# input directory with the files
dir = "inputs"
demand = "demand.csv"
generation_availability = "generation_availability.csv"
generation = "generation.csv"
transmission_lines = "transmission_lines2.csv"
scalars = "scalars.toml"
line_capacities_bidirectional = false
clusters = {clusters}
bound_alpha_factor = {alpha}

[input.sets]
time_steps = {list(range(1, time_steps))}
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

chain_lengths = [3, 5, 10]
degrees = [10, 6, 3]
time_steps = [24, 168, 720, 2160]
alphas = [1.0]
for i in range(len(chain_lengths)):
    for j in time_steps:
        for a in alphas:
            create_star_case_study(f"{chain_lengths[i]}_{degrees[i]}_star_1_tech_{a}", chain_lengths[i], degrees[i], time_steps=j, alpha=a)
