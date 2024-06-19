
import numpy as np
import pandas as pd



def add_generation_and_generation_availability(locations, name, time_steps, gas_only):
    """
    generates the generation_availability.csv and the generation.csv in file location: case_studies/{name}/inputs

    inputs:
        locations: [str]    list of locations
        name:   [string]    name of the case study (also the place where data is stored)
        time_steps [int]    number of hours
        gas_only [bool]     whether only gas is available or all technologies are available
    """
    
    folder = f'case_studies/{name}'
    input_folder = f'{folder}/inputs'

    # Generation availability
    generation_av = ["location,technology,time_step,availability"]
    
    technologies = [] if gas_only else [
        ('WindOff', 0.5, 0.27, 16/20),
        ('WindOn', 0.3, 0.2, 1),
        ('SunPV', 0.3, 0.2, 1),
    ]

    df_sun_distributions = pd.read_csv('sun_distribution.csv')

    for tech, mean, std, p in technologies:
        add_gen_av(time_steps, generation_av, mean, std, tech, p, df_sun_distributions, locations)


    with open(f'{input_folder}/generation_availability.csv', 'w+') as f:
        f.write('\n'.join(generation_av) + '\n')


    # Generation
    generation = ["technology,location,investment_cost,variable_cost,unit_capacity,ramping_rate"]
    investment_factor = time_steps / 8760
    technologies = [
        ("Gas", f"{investment_factor * 23.33333333},0.05,250,0.75", 20/20),
    ]
    if not gas_only:
        technologies.extend([
            ("Coal", f"{investment_factor * 33.75},0.15,400,0.4", 4/20),
            ("Lignite", f"{investment_factor * 38.75},0.1,400,0.5", 19/20),
            ("Nuclear", f"{investment_factor * 68.66666667},0.01,1000,0.2", 9/20),
            ("Oil", f"{investment_factor * 24.16666667},0.2,100,0.9", 10/20),
            ("SunPV", f"{investment_factor * 24},1.00E-04,50,1.0", 20/20),
            ("WindOff", f"{investment_factor * 88.33333333},0.005,100,1.0", 16/20),
            ("WindOn", f"{investment_factor * 48.4},0.0025,100,1.0", 20/20),
        ])
    for name, costs, p in technologies:
        add_technoligy(name, generation, costs, p, locations)

    
    with open(f'{input_folder}/generation.csv', 'w+') as f:
        f.write('\n'.join(generation) + '\n')


def get_list_technologies_distribution(n, p):
    "generates a list of random ones and zeros for length n where chance of being one is p"
    return np.random.binomial(1, p, size=n)


def add_gen_av(time_steps, generation_av, mean, std, tech, p, df, locations):
    n = len(locations)
    prob = get_list_technologies_distribution(n, p)
    for i in range(n):
        for time_step in range(1, time_steps + 1):
            if prob[i]:
                if tech == 'SunPV':
                    mean = df.iloc[[time_step % 24]]["mean"].item()
                    std = df.iloc[[time_step % 24]]["std"].item()
                synthetic_availability = round(min(1, max(0, np.random.normal(loc=mean, scale=std))), 4)
            else:
                synthetic_availability = 0
            generation_av.append(f"{locations[i]},{tech},{time_step},{synthetic_availability}")


def add_technoligy(name, generation, costs, p, locations):
    n = len(locations)
    prob = get_list_technologies_distribution(n, p)
    for i in range(n):
        if prob[i]:
            generation.append(f"{name},{locations[i]},{costs}")
