export run_experiment

function run_experiment(data::ExperimentData, optimizer_factory, line_capacities_bidirectional::Bool)::ExperimentResult
    benchmark_relaxations(data, optimizer_factory, line_capacities_bidirectional)

    return run_optimisation(data, optimizer_factory, line_capacities_bidirectional, nothing)
end

function benchmark_relaxations(data::ExperimentData, optimizer_factory, line_capacities_bidirectional::Bool)
    @assert line_capacities_bidirectional == false "TODO relaxations are only possible with directional line capacities right now. try running case_studies/stylized_EU_directional"
    @info "doing experiments"
    results_df = DataFrame(n_clusters=Int[], clusters=Vector{Set{Symbol}}[], objective=Float64[], runtime=Float64[])
    for i in [4]
    # for i = length(data.locations)-1:-1:2
        data_relaxed, clusters = relaxation_iteration(data, i)
        # store_relaxed_data(data_relaxed)
        relaxed_experiment_result = run_optimisation(data_relaxed, optimizer_factory, line_capacities_bidirectional, nothing)
        objective = relaxed_experiment_result.total_investment_cost + relaxed_experiment_result.total_operational_cost
        push!(results_df,  (i, clusters, objective, relaxed_experiment_result.runtime))
    end

    @info "finished benchmarks"
    
    # write DataFrame out to CSV file
    CSV.write("results.csv", results_df)
end