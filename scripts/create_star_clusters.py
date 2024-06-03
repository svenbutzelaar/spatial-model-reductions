import random
import os
from math import log2, ceil

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
    return 0 if n == 0 else [create_middle_cluster(n-1)]
    
    
def create_star_case_study(name, chain_length, degrees, time_steps):
    folder = f'case_studies/{name}'
    input_folder = f'{folder}/inputs'

    # Create folders
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    total_locations = chain_length*degrees  + 1
    chains = []
    locations = [f"l{i}" for i in range(total_locations)]
    for i in range(1, total_locations, chain_length):
        chain = [[locations[i + x]] for x in range(chain_length)]
        chain_clusters = get_clusters(chain)
        chains.append(chain_clusters)
    assert len(chains) == degrees
    print(chains)
    depth_chain_clusters = ceil(chain_length/2) + 1
    print(depth_chain_clusters)
    
    clusters = [create_middle_cluster(depth_chain_clusters)]
    clusters.extend(chains)
    print(clusters)
        
    # Demands
    demands = ["location,time_step,demand"]
    for location in range(total_locations):
        for time_step in range(time_steps):
            demands.append(f"l{location},{time_step},100")

    with open(f'{input_folder}/demand.csv', 'w+') as f:
        f.write('\n'.join(demands) + '\n')


    # Generation availability
    generation_av = ["location,technology,time_step,availability"]
    # TODO add generation availability
    with open(f'{input_folder}/generation_availability.csv', 'w+') as f:
        f.write('\n'.join(generation_av) + '\n')


    # Generation
    generation = ["technology,location,investment_cost,variable_cost,unit_capacity,ramping_rate"]

    for location in range(total_locations):
        generation.append(f"Gas,l{location},23.33333333,0.05,250,0.75")

    with open(f'{input_folder}/generation.csv', 'w+') as f:
        f.write('\n'.join(generation) + '\n')

    # transmission_lines
    transmission_lines = ["from,to,capacity"]
    for i in range(1, degrees, chain_length):
        transmission_lines.append(
            f"l{0},l{i},{random.randint(1, 20) * 10}"
        )
    for chain in chains:
        for i in range(len(chain)-1):
            transmission_lines.append(
                f"l{i},l{i+1},{random.randint(1, 20) * 10}"
            )

    with open(f'{input_folder}/transmission_lines2.csv', 'w+') as f:
        f.write("\n".join(transmission_lines))

    with open(f'{input_folder}/scalars.toml', 'w+') as f:
        f.write("""# Value of lost load (cost of not supplying energy) [kEUR/MWh]
value_of_lost_load = 3.0
# If true, an LP relaxation of the problem will be solved
relaxation = false
    """)

    with open(f'{folder}/config.toml', 'w+') as f:
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
    
chain_length = 2
degrees = 4
create_star_case_study(f"{chain_length}_{degrees}_star", chain_length, degrees, 100)
