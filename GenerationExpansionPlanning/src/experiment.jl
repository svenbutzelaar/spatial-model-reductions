export run_experiment

function run_experiment(data::ExperimentData, optimizer_factory)::ExperimentResult
    # 1. Extract data into local variables
    @info "Reading the sets"
    N = data.locations
    G = data.generation_technologies
    NG = data.generators
    T = data.time_steps
    L = data.transmission_lines

    @info "performing relaxation"
    data_relaxed = relaxation_iteration(data)
    relaxed_experiment_result = run_optimisation(data_relaxed, optimizer_factory)
    upperbound = relaxed_experiment_result.total_investment_cost + relaxed_experiment_result.total_operational_cost
    @info "relaxed result gave objective: $upperbound" 

    return run_optimisation(data, optimizer_factory, upperbound)
end
