
import os

import numpy as np
import pandas as pd
import networkx as nx

from technologies_eu import add_generation_and_generation_availability

def create_eu_case_study(name, df, clustering, time_steps, bound_alpha_factor, gas_only):
    folder = f'case_studies/{name}'
    input_folder = f'{folder}/inputs'
    graph = nx.from_pandas_edgelist(df, 'from', 'to')
    locations = list(graph.nodes)
    
    np.random.seed(42)

    # Create folders
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    

    initial_demand = np.random.uniform(3000, 8000, size=len(locations))
    # Demands
    demands = ["location,time_step,demand"]
    for i, location in enumerate(locations):
        for time_step in range(1, time_steps + 1):
            change = np.random.uniform(-500, 500)
            demands.append(f"{location},{time_step},{initial_demand[i] + change}")

    with open(f'{input_folder}/demand.csv', 'w+') as f:
        f.write('\n'.join(demands) + '\n')


    add_generation_and_generation_availability(locations, name, time_steps, gas_only)

    # Transmission_lines
    transmission_lines = ["from,to,capacity"]

    for _, row in df.iterrows():
        max_cap = max(row['export_capacity'], row['import_capacity'])
        transmission_lines.append(f"{row['from']},{row['to']},{max_cap}")

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
clusters = {clustering}
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

df = pd.read_csv('case_studies/stylized_eu/inputs/transmission_lines.csv')


extra_reductions = {
    "CombiReduce[2]" : [[['BEL']],[['IRE']],[['POR'],['SPA']],[['GER','UKI','NED','NOR','DEN'],['FRA'],['SWI'],['BLK','ITA','AUS']],[['SKO','CZE','POL'],['FIN','BLT','SWE']]],
    "GridReduce[2]" : [[['SPA']],[['POR']],[['IRE']],[['ITA'],['FRA'],['SWI'],['AUS','BLK','SKO','CZE']],[['NOR'],['UKI'],['GER','DEN','NED','BEL'],['SWE','FIN','BLT','POL']]],
    "CliqueReduce[2]" : [[['SPA']],[['POR']],[['IRE']],[['FIN'],['SWE'],['BLT']],[['BLK'],['ITA','AUS','SWI'],['SKO','POL','CZE']],[['GER','UKI','NED','NOR','DEN'],['FRA'],['BEL']]],
    "CliqueReduce[3]" : [[[['SPA']]],[[['POR']]],[[['IRE']]],[[['GER','UKI','NED','NOR','DEN'],['FRA'],['BEL']],[['BLK'],['ITA','AUS','SWI'],['SKO','POL','CZE']],[['FIN'],['SWE'],['BLT']]]],
}

# configure the different reductions based on predefined clusterings
reductions = {
    "CombiReduce[1]" : [['SWI'],['BEL'],['FRA'],['IRE'],['GER','UKI','NED','NOR','DEN'],['BLK','ITA','AUS'],['SKO','CZE','POL'],['FIN','BLT','SWE'],['POR','SPA']],
    "GridReduce[1]" : [['ITA'],['SWI'],['FRA'],['SPA'],['POR'],['NOR'],['UKI'],['IRE'],['AUS','BLK','SKO','CZE'],['GER','DEN','NED','BEL'],['SWE','FIN','BLT','POL']],
    "CliqueReduce[1]" : [['BLK'],['BEL'],['FRA'],['SPA'],['POR'],['IRE'],['GER','UKI','NED','NOR','DEN'],['FIN','SWE','BLT'],['ITA','AUS','SWI'],['SKO','POL','CZE']],
    "ChainReduce[1]" : [['AUS'],['BLK'],['CZE'],['GER'],['ITA'],['SWI'],['BEL'],['FRA'],['NED'],['SKO'],['DEN'],['SWE'],['FIN'],['POL'],['NOR'],['UKI'],['IRE'],['BLT'],['POR','SPA']],
}

for reduction in reductions:
    clustering = reductions[reduction]
    for t in [168, 720, 2160]:
        for alpha in [0.9]: # , 0.9
            for gas_only in [True, False]:
                name = f"EU/{reduction}_{t}_{alpha}_{'gas' if gas_only else 'all'}"
                create_eu_case_study(name, df, clustering, t, alpha, gas_only)
                print(f'    "case_studies/{name}/config.toml",')