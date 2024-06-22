using GenerationExpansionPlanning
using Revise
using DataFrames
using Gurobi
using CSV
using Dates

num_runs = 2
experiments = [
    # "case_studies/grid_42/50_steps/config.toml",
    # "case_studies/grid_42/100_steps/config.toml",
    # "case_studies/grid_42/150_steps/config.toml",
    # "case_studies/grid_42/200_steps/config.toml",
    # "case_studies/grid_42/250_steps/config.toml",
    # "case_studies/grid_42/300_steps/config.toml",
    # "case_studies/grid_42/350_steps/config.toml",
    # "case_studies/grid_42/400_steps/config.toml",
    "case_studies/3_10_star_1_tech_1.0/24_steps/config.toml",
    "case_studies/3_10_star_1_tech_1.0/168_steps/config.toml",
    "case_studies/3_10_star_1_tech_1.0/720_steps/config.toml",
    "case_studies/3_10_star_1_tech_1.0/2160_steps/config.toml",
    "case_studies/5_6_star_1_tech_1.0/24_steps/config.toml",
    "case_studies/5_6_star_1_tech_1.0/168_steps/config.toml",
    "case_studies/5_6_star_1_tech_1.0/720_steps/config.toml",
    "case_studies/5_6_star_1_tech_1.0/2160_steps/config.toml",
    "case_studies/10_3_star_1_tech_1.0/24_steps/config.toml",
    "case_studies/10_3_star_1_tech_1.0/168_steps/config.toml",
    "case_studies/10_3_star_1_tech_1.0/720_steps/config.toml",
    "case_studies/10_3_star_1_tech_1.0/2160_steps/config.toml",
    # "case_studies/3_10_star_all_tech_0.9/24_steps/config.toml",
    # "case_studies/3_10_star_all_tech_0.9/168_steps/config.toml",
    # "case_studies/3_10_star_all_tech_0.9/720_steps/config.toml",
    # "case_studies/3_10_star_all_tech_0.9/2160_steps/config.toml",
    # "case_studies/5_6_star_all_tech_0.9/24_steps/config.toml",
    # "case_studies/5_6_star_all_tech_0.9/168_steps/config.toml",
    # "case_studies/5_6_star_all_tech_0.9/720_steps/config.toml",
    # "case_studies/5_6_star_all_tech_0.9/2160_steps/config.toml",
    # "case_studies/10_3_star_all_tech_0.9/24_steps/config.toml",
    # "case_studies/10_3_star_all_tech_0.9/168_steps/config.toml",
    # "case_studies/10_3_star_all_tech_0.9/720_steps/config.toml",
    # "case_studies/10_3_star_all_tech_0.9/2160_steps/config.toml",
    ]

# "case_studies/stylized_EU/config.toml"
# "case_studies/8_locations/config.toml"
# "case_studies/stylized_EU_directional/config.toml"
# "case_studies/cliques_10_5/config.toml"

# Run multiple experiments
for experiment ∈ experiments
    # Step 1: Read the experiment config
    @info "Reading the config"
    config = read_config(experiment)
    # Step 2: Parse the data
    @info "Parsing the config data"
    experiment_data = ExperimentData(config[:input])

    # Make a new results folder for this experiment
    results_folder = "results"
    now = Dates.now()
    experiment_name = join(split(experiment, "/")[2:end-1], "_")
    prefix = Dates.format(now, "yyyymmddHHMMSS")
    experiment_folder = joinpath(results_folder, "$prefix-$experiment_name")
    mkpath(experiment_folder)

    # Step 3: Run the experiments
    @info "Running experiment: $experiment"
    output_config = config[:output]
    results_df = DataFrame(run=Int16[], reduction=Bool[], objective=Float64[], runtime=Float64[], n=Int16[], time_steps=Int16[], bound_alpha_factor=Float16[])
    
    # Repeat the experiment num_runs
    for run in 1:num_runs
        @info "Executing run: $run"
        time_steps = length(config[:input][:sets][:time_steps])
        experiment_result = run_experiment(experiment_data, Gurobi.Optimizer, config[:line_capacities_bidirectional], config[:cluster_tree], config[:bound_alpha_factor], output_config, results_df, run, time_steps)
        # Save decision outputs (get overwritten for now)
        save_result(experiment_result, output_config)
    end
    # Step 4: Save the results
    CSV.write(joinpath(experiment_folder, "results.csv"), results_df)
    @info "Exported results to: $experiment_folder"  
end 
