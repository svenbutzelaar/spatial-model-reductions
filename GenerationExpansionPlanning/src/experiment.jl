export run_experiment


function run_experiment(data::ExperimentData, optimizer_factory, line_capacities_bidirectional::Bool, dendrogram::Vector, bound_alpha_factor::Float64, config::Dict{Symbol,Any}, results_df::DataFrame, run::Int64, time_steps::Int64)::ExperimentResult
    @assert line_capacities_bidirectional == false "TODO reductions are only possible with directional line capacities right now. try running case_studies/stylized_EU_directional"
    
    # Use debug = true if you want every intermediate step to be written to your output file
    debug = false

    @info "Running reduced instance"
    time = @elapsed begin
        @info dendrogram
        reduced_result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, dendrogram, bound_alpha_factor, data, config, debug)
    end
    objective = reduced_result.total_investment_cost + reduced_result.total_operational_cost
    push!(results_df,  (run, true, objective, time, length(data.locations), time_steps, bound_alpha_factor))

    @info "Running original instance"
    time = @elapsed begin
        result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, nothing, 0.0, data, config, false)
    end
    objective = result.total_investment_cost + result.total_operational_cost
    push!(results_df,  (run, false, objective, time, length(data.locations), time_steps, 0.0))
    return reduced_result
end