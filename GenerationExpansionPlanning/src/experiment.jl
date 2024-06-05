export run_experiment


function run_experiment(data::ExperimentData, optimizer_factory, line_capacities_bidirectional::Bool, dendrogram::Vector, config::Dict{Symbol,Any})::ExperimentResult
    @assert line_capacities_bidirectional == false "TODO reductions are only possible with directional line capacities right now. try running case_studies/stylized_EU_directional"
    @info "doing experiments"
    
    # Use debug = true if you want every intermediate step to be written to your output file
    debug = false

    results_df = DataFrame(relaxation=Bool[], objective=Float64[], runtime=Float64[])
    # removed as we first start to work with our own clustering objectives
    # dendrogram = create_clusters_hierarchy(data)
    # relaxed_result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, dendrogram, data, config, debug)
    # objective = relaxed_result.total_investment_cost + relaxed_result.total_operational_cost
    # push!(results_df,  (true, objective, relaxed_result.runtime))
    time = @elapsed begin
        relaxed_result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, dendrogram, data, config, debug)
    end
    objective = relaxed_result.total_investment_cost + relaxed_result.total_operational_cost
    push!(results_df,  (true, objective, time))
    
    time = @elapsed begin
        result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, nothing, data, config, false)
    end
    results_df = DataFrame(reduction=Bool[], objective=Float64[], runtime=Float64[])
    reduced_result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, dendrogram, data, config, debug)
    objective = reduced_result.total_investment_cost + reduced_result.total_operational_cost
    
    time = @elapsed begin
        reduced_result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, dendrogram, data, config, debug)
    end
    objective = reduced_result.total_investment_cost + reduced_result.total_operational_cost
    push!(results_df,  (true, objective, time))

    time = @elapsed begin
        result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, nothing, data, config, false)
    end
    objective = result.total_investment_cost + result.total_operational_cost
    push!(results_df,  (false, objective, time))

    @info "finished benchmarks"
    
    # Exporting the result information
    results_folder = "results"
    now = Dates.now()
    prefix = Dates.format(now, "yyyyMMddHHmmss")
    filepath = joinpath(results_folder, "$prefix-experiment.csv")

    # write DataFrame out to CSV file
    CSV.write(filepath, results_df)

    @info "exported results to $filepath"
    return reduced_result
end