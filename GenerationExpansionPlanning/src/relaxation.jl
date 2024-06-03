using DataStructures
export relaxation_iteration
"""
    relaxation_iteration(data::ExperimentData, k=2)::(ExperimentData, Vector{Set{Symbol}})

    Create clusters and returns merged Dataframes
"""
function relaxation_iteration(data::ExperimentData, dendrogram::Vector, data_og::ExperimentData)::Tuple{ExperimentData, Vector{Set{Symbol}}, Union{Nothing, Vector}}
    # Create k clusters
    clusters, dendrogram_new = create_clusters(data, dendrogram)
    @info ("CLUSTERS are made; ", clusters)
    return (merge_within_clusters(data_og, clusters), clusters, dendrogram_new)
end

# function create_clusters(data::ExperimentData, dendrogram::Hclust, k::Integer)::Vector{Set{Symbol}}
#     # Cut the dendrogram to obtain k clusters
#     cluster_assignments = cutree(dendrogram, k=k)
#     clusters = [Set{Symbol}() for _ ∈ 1:k]
#     indices_location = Dict(i => location for (i, location) ∈ enumerate(data.locations))

#     @info cluster_assignments, data.locations


#     for (i, assignment) ∈ enumerate(cluster_assignments)
#         push!(clusters[assignment], indices_location[i])
#     end

#     println("created clusters: $clusters")

#     return clusters
# end

function create_clusters(data::ExperimentData, dendrogram::Vector)
    # # Cut the dendrogram to obtain k clusters
    # clusters = []
    # indices_location = Dict(i => location for (i, location) ∈ enumerate(data.locations))

    # @info cluster_assignments, data.locations
    # assignment staat voor nummer van cluster die gemaakt wordt
    # indices_location[i] pakt de location die hoort bij index i
    @info "dendrogram", dendrogram
    if (depth(dendrogram) > 2)
        dendrogram_new = flatten_innermost_layer(dendrogram)
    else 
        dendrogram_new = nothing
    end
    clusters = create_clusters_merging_last_layer_rec(dendrogram)


    # layer_queue = Queue{Any}()
    # enqueue!(layer_queue,vec(dendrogram))
    # j = 1
    # while length(layer_queue) > 0
    #     layer = dequeue!(layer_queue)
    #     @info ("47", layer)
    #     if !(layer isa Vector{Vector{Symbol}})
    #         push!(clusters, Set{Symbol}())
    #         l = length(layer)
    #         for i ∈ 1:l
    #             @assert !(layer[i] isa Vector{Any}) "Depth of layers is not equal to each other, create a tree with equal depth"
                
    #             push!(clusters[j], layer[i])
    #         end
    #         j = j + 1
    #     else
    #         @info (52,layer)
    #         for i ∈ 1:size(layer)[1]
    #             enqueue!(layer_queue, layer[i])
    #         end
    #     end
    # end

    println("created clusters: $clusters")
    println("Dendrogram old: $dendrogram")
    println("dendrogram new: $dendrogram_new")
    return (clusters, dendrogram_new)
end

function create_clusters_merging_last_layer_rec(dendrogram :: Vector) :: Vector{Set{Symbol}}
    if depth(dendrogram) == 1
        return [Set(dendrogram)]
    end

    clusters = []
    for vect in dendrogram
        append!(clusters, create_clusters_merging_last_layer_rec(vect))
    end
    return clusters
end

function depth(arr)::Int64
    if (arr isa Symbol)
        return 0
    else
        return 1 + depth(arr[1])
    end
end

function flatten_innermost_layer(arr)
    if arr isa Symbol
        return nothing
    end
    if arr isa Vector{Symbol}
        return nothing
    end

    result = Vector{Any}()
    # Base case
    if arr isa Vector{Vector{Symbol}}
        for vect in arr
            append!(result, vect)
        end
        return result
    end

    # recursive case
    for vect in arr
        n = flatten_innermost_layer(vect)
        if isnothing(n)
            return n 
        end
        append!(result, n)
    end

    return result
end

function merge_within_clusters(data::ExperimentData, clusters::Vector{Set{Symbol}})::ExperimentData
    
    # Create a node to cluster dict
    cluster_symbols = [Symbol(join(map(String, collect(cluster)), "_")) for cluster in clusters]
    symbol_cluster_dict = Dict{Symbol, Symbol}()
    
    for (index, cluster) ∈ enumerate(clusters)
        for node ∈ cluster
            symbol_cluster_dict[node] = cluster_symbols[index]
        end
    end
    
    # Get aggregated set and data dicts
    set_dict = get_merged_set_dict(data, cluster_symbols, symbol_cluster_dict, clusters)
    # @info set_dict
    data_dict = get_merged_data_dict(data, clusters, cluster_symbols)
    # @info data_dict
    scalars_dict = Dict(:value_of_lost_load => data.value_of_lost_load, :relaxation => data.relaxation)

    @info "Dataframes of clusters merged"

    relaxed_data = ExperimentData(Dict(
        :sets => set_dict,
        :data => data_dict,
        :scalars => scalars_dict
    ))

    return relaxed_data
end

function get_merged_set_dict(data::ExperimentData, cluster_symbols::Vector{Symbol}, symbol_cluster_dict::Dict{Symbol, Symbol}, clusters::Vector{Set{Symbol}})::Dict
    # All sets:
    N = data.locations
    G = data.generation_technologies
    NG = data.generators
    T = data.time_steps
    L = data.transmission_lines

    # Nodes corresponding to clusters
    N = cluster_symbols

    # Transmission lines between clusters
    L_prime = Vector{Tuple}()


    for (a, b) ∈ L
        a_cluster = symbol_cluster_dict[a]
        b_cluster = symbol_cluster_dict[b]

        if a_cluster != b_cluster
            push!(L_prime, (a_cluster, b_cluster))
        end
    end
    L = L_prime

    # Generator technologies for the clusters
    NG_prime_set = Set{Tuple}()
    for (location, generator) ∈ NG
        push!(NG_prime_set, (symbol_cluster_dict[location], generator))
    end
    NG = collect(NG_prime_set)

    return Dict(
        :time_steps => T,
        :locations => N,
        :transmission_lines => L,
        :generators => NG,
        :generation_technologies => G,
    )
end

function get_merged_data_dict(data::ExperimentData, clusters::Vector{Set{Symbol}}, cluster_symbols::Vector{Symbol})::Dict
    D = data.demand
    A = data.generation_availability
    G = data.generation
    T = data.transmission_capacities

    D_prime = DataFrame(location = Symbol[], time_step = Int64[], demand = Float64[])
    A_prime = DataFrame(location = Symbol[], technology = Symbol[], time_step = Int64[], availability = Float64[])
    G_prime = DataFrame(technology = Symbol[], location = Symbol[], investment_cost = Float64[], variable_cost = Float64[], unit_capacity = Int64[], ramping_rate = Float64[])
    # T_prime = DataFrame(from = Symbol[], to = Symbol[], export_capacity = Float64[], import_capacity = Float64[])
    T_prime = DataFrame(from = Symbol[], to = Symbol[], capacity = Float64[])
    
    for (index, cluster) ∈ enumerate(clusters)
        cluster_symbol = cluster_symbols[index]
        
        # Sum the demands in each cluster per time_step
        cluster_df = filter(row -> row.location in cluster, D)
        for group ∈ groupby(cluster_df, :time_step) 
            push!(D_prime, (cluster_symbol, group[1, :time_step], sum(group[:, :demand])))
        end
        
        # Take the average availability in each cluster per technology and time_step
        cluster_df = filter(row -> row.location in cluster, A)
        for group ∈ groupby(cluster_df, [:technology, :time_step])
            push!(A_prime, (cluster_symbol, group[1, :technology], group[1, :time_step], mean(group[:, :availability])))
        end

        # Take the mean values for investment_cost, variable_cost, unit_capacity, ramping_rate in each cluster per technology
        cluster_df = filter(row -> row.location in cluster, G)
        for group ∈ groupby(cluster_df, [:technology])
            push!(G_prime, (group[1, :technology], cluster_symbol, mean(group[:, :investment_cost]), mean(group[:, :variable_cost]), mean(group[:, :unit_capacity]), mean(group[:, :ramping_rate])))
        end
    end

    # Sum the export_capacity and import_capacity between every pair of clusters
    for i ∈ 1:(length(clusters))
        for j ∈ 1:(length(clusters))
            if i != j
                cluster_df = filter(row -> (row.from ∈ clusters[i] && row.to ∈ clusters[j]), T)
                push!(T_prime, (cluster_symbols[i], cluster_symbols[j], sum(cluster_df[:, :capacity])))
            end
        end
    end

    D = D_prime
    A = A_prime
    G = G_prime
    T = T_prime

    return Dict(
        :demand => D, 
        :generation_availability => A,
        :generation => G,
        :transmission_lines => T,
        :scalars => Dict(:value_of_lost_load => data.value_of_lost_load, :relaxation => data.relaxation),
    )
end

