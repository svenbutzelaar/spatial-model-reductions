import os
from technologies import *
import numpy as np

def create_clusters(n, clique_size):
    input_list = list(f'l{i}' for i in range(n))
    return [input_list[i:i + clique_size] for i in range(0, n, clique_size)]

def create_clique_case_study(name, n, clique_size, time_steps, bound_alpha_factor):
    folder = f'case_studies/{name}'
    input_folder = f'{folder}/inputs'
    input_folder_extra = f'{folder}/inputs/config.toml'
    print(input_folder_extra)

    # Create folders
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    

    assert n % clique_size == 0
    initial_demand = np.random.uniform(3000, 8000, size=n)
    # Demands
    demands = ["location,time_step,demand"]
    for location in range(n):
        for time_step in range(1, time_steps + 1):
            change = np.random.uniform(-500, 500)
            demands.append(f"l{location},{time_step},{initial_demand[location] + change}")

    with open(f'{input_folder}/demand.csv', 'w+') as f:
        f.write('\n'.join(demands) + '\n')


    # Generation availability
    generation_av = ["location,technology,time_step,availability"]
    # TODO add generation availability
    with open(f'{input_folder}/generation_availability.csv', 'w+') as f:
        f.write('\n'.join(generation_av) + '\n')


    # Generation
    generation = ["technology,location,investment_cost,variable_cost,unit_capacity,ramping_rate"]

    for location in range(n):
        annual_inv = 23.33333 * time_steps / 8760
        generation.append(f"Gas,l{location},{annual_inv},0.05,250,0.75")
    # for location in range(0, n, clique_size):
    #     generation.append(f"Nuclear,l{location},68.66666667,0.01,1000,0.2")

    with open(f'{input_folder}/generation.csv', 'w+') as f:
        f.write('\n'.join(generation) + '\n')

    # add_generation_and_generation_availability(n, name, time_steps)

    # transmission_lines
    transmission_lines = ["from,to,capacity"]
    for clique in range(n // clique_size):
        clique_iterator = range(clique * clique_size, (clique + 1) * clique_size)
        transmission_lines.extend(
            f"l{i},l{j},{np.random.uniform(500,5000)}"
            for i in clique_iterator
            for j in clique_iterator
            if i != j
        )

    clique_connector_iterator = range(0, n, clique_size)
    transmission_lines.extend(
            f"l{i},l{j},{np.random.uniform(500,5000)}"
            for i in clique_connector_iterator
            for j in clique_connector_iterator
            if i != j
        )

    with open(f'{input_folder}/transmission_lines2.csv', 'w+') as f:
        f.write('\n'.join(transmission_lines) + '\n')

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
clusters = {create_clusters(n, clique_size)}
bound_alpha_factor = {bound_alpha_factor}

[input.sets]
time_steps = {list(range(1, time_steps + 1))}
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

np.random.seed(42)
time_steps = [24, 168, 720, 2160]
n = 64
clique_sizes = [4, 8, 16]
for t in time_steps:
    for clique_size in clique_sizes:
        name = f"cliques_s_size_{clique_size}_{t}_steps"
        create_clique_case_study(name,n,clique_size,t, 0.9)
