export relaxation_iteration

function relaxation_iteration(data::ExperimentData)::ExperimentData
    clusters = create_clusters(data)
    return merge_within_clusters(data, clusters)
end

function create_clusters(data::ExperimentData)::Vector{Set{Symbol}}
    return [Set([:NED, :BEL])]
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
    set_dict = get_merged_set_dict(data, cluster_symbols, symbol_cluster_dict)
    @error set_dict
    data_dict = get_merged_data_dict(data, clusters, cluster_symbols)
    @error data_dict

    relaxed_data = ExperimentData(Dict(
        :sets => set_dict,
        :data => data_dict,
    ))

    return relaxed_data
end

function get_merged_set_dict(data::ExperimentData, cluster_symbols::Vector{Symbol}, symbol_cluster_dict::Dict{Symbol, Symbol})::Dict
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
            push_if_transmission_not_exists(L_prime, a_cluster, b_cluster)
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
    T = data.transmission_lines

    D_prime = DataFrame(location = Symbol[], time_step = Int64[], demand = Float64[])
    A_prime = DataFrame(location = Symbol[], technology = Symbol[], time_step = Int64[], availability = Float64[])
    G_prime = DataFrame(technology = Symbol[], location = Symbol[], investment_cost = Float64[], variable_cost = Float64[], unit_capacity = Int64[], ramping_rate = Float64[])
    T_prime = DataFrame(from = Symbol[], to = Symbol[], export_capacity = Float64[], import_capacity = Float64[])
    
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

        # Sum the export_capacity and import_capacity between every pair of clusters
        for i ∈ 1:(length(clusters)-1)
            for j ∈ (i+1):length(clusters)
                cluster_df = filter(row -> (row.from ∈ clusters[i] ⩓ row.to ∈ clusters[j]) ⩔ (row.from ∈ clusters[j] ⩓ row.to ∈ clusters[i]), T)
                push!(T_prime, (cluster_symbols[i], cluster_symbols[j], sum(cluster_df[:, :export_capacity]), sum(cluster_df[:, :import_capacity])))
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

function push_if_transmission_not_exists(L::Vector{Tuple}, a::Symbol, b::Symbol)
    if (a, b) ∉ L && (b, a) ∉ L
        push!(L, (a, b))
    end
end
