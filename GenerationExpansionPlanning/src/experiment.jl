export run_experiment


function run_experiment(data::ExperimentData, optimizer_factory, line_capacities_bidirectional::Bool, dendrogram::Vector)::ExperimentResult
    @assert line_capacities_bidirectional == false "TODO relaxations are only possible with directional line capacities right now. try running case_studies/stylized_EU_directional"
    @info "doing experiments"

    results_df = DataFrame(relaxation=Bool[], objective=Float64[], runtime=Float64[])
    # removed as we first start to work with our own clustering objectives
    # dendrogram = create_clusters_hierarchy(data)
    relaxed_result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, dendrogram)
    objective = relaxed_result.total_investment_cost + relaxed_result.total_operational_cost
    push!(results_df,  (true, objective, relaxed_result.runtime))
    
    # relaxed_result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, dendrogram)
    # objective = relaxed_result.total_investment_cost + relaxed_result.total_operational_cost
    # push!(results_df,  (true, objective, relaxed_result.runtime))

    # result = run_optimisation(data, optimizer_factory, line_capacities_bidirectional, nothing)
    # objective = result.total_investment_cost + result.total_operational_cost
    # push!(results_df,  (false, objective, result.runtime))

    @info "finished benchmarks"
    
    # write DataFrame out to CSV file
    CSV.write("results.csv", results_df)

    return relaxed_result
end

# removed as we first start to work with our own clustering objectives
# function create_clusters_hierarchy(data::ExperimentData)::Hclust
#     edges = []
#     capacities = []
#     location_indices = Dict(location => i for (i, location) ∈ enumerate(data.locations))

#     for line in eachrow(data.transmission_capacities)
#         source = location_indices[line.from]
#         dest = location_indices[line.to]
#         # capacity = mean([line.export_capacity, line.import_capacity])  # Use average capacity from both ways
#         capacity = line.capacity
#         push!(edges, (source, dest))
#         push!(capacities, capacity)
#     end

#     # Create a distance matrix where the distance is inversely related to capacity
#     n = length(data.locations)
#     dist_matrix = fill(Inf, n, n)

#     for (i, edge) in enumerate(edges)
#         source, dest = edge
#         dist = 1 / capacities[i]
#         dist_matrix[source, dest] = dist
#         dist_matrix[dest, source] = dist  # Assuming undirected graph
#     end 

#     # Perform hierarchical clustering using single linkage
#     return hclust(dist_matrix, linkage=:single)
# end
