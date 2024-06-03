
import os

def create_clusters(n, clique_size):
    input_list = list(range(n))
    return [input_list[i:i + clique_size] for i in range(0, n, clique_size)]

def create_clique_case_study(name, n, clique_size, time_steps):
    folder = f'case_studies/{name}'
    input_folder = f'{folder}/inputs'

    # Create folders
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    

    assert n % clique_size == 0

    # Demands
    demands = ["location,time_step,demand"]
    for location in range(n):
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

    for location in range(n):
        generation.append(f"Gas,l{location},23.33333333,0.05,250,0.75")

    with open(f'{input_folder}/generation.csv', 'w+') as f:
        f.write('\n'.join(generation) + '\n')

    # transmission_lines
    transmission_lines = ["from,to,capacity"]
    for clique in range(n // clique_size):
        clique_iterator = range(clique * clique_size, (clique + 1) * clique_size)
        transmission_lines.extend(
            f"l{i},l{j},4000"
            for i in clique_iterator
            for j in clique_iterator
            if i != j
        )

    clique_connector_iterator = range(0, n, clique_size)
    transmission_lines.extend(
            f"l{i},l{j},3000"
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


create_clique_case_study(name='cliques_16_4',n=16,clique_size=4,time_steps=100)