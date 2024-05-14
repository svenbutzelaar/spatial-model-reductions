export relaxation_iteration


function relaxation_iteration(data::ExperimentData)::ExperimentData
    loactions_to_merge = decide_locations_to_merge(data)
    return merge_locations(data, loactions_to_merge)
end

function decide_locations_to_merge(data::ExperimentData)::Set{Symbol}
    # TODO build decider on which locations to merge
    return Set([:NED, :BEL])
end

function merge_locations(data::ExperimentData, loactions_to_merge::Set{Symbol})::ExperimentData
    merged_location_symbol = Symbol(join(map(String, collect(loactions_to_merge)), "_"))
    set_dict = get_merged_set_dict(data, loactions_to_merge, merged_location_symbol)
    data_dict = get_merged_data_dict(data, loactions_to_merge, merged_location_symbol)
    scalars_dict = dict("value_of_lost_load" => data.value_of_lost_load, "relaxation" => data.relaxation)
    relaxed_data = ExperimentData(Dict(
        "sets" => set_dict,
        "data" => data_dict,
        "scalars" => scalars_dict
    ))

    return relaxed_data
end

function get_merged_set_dict(data::ExperimentData, loactions_to_merge::Set{Symbol}, merged_location_symbol::Symbol)::Dict
    N = data.locations
    G = data.generation_technologies
    NG = data.generators
    T = data.time_steps
    L = data.transmission_lines

    # Merge locations
    N = [n for n ∈ N if n ∉ loactions_to_merge]
    push!(N, merged_location_symbol)

    # Merge transmission_lines
    L_prime = Vector{Tuple}()
    for (a, b) in L
        if a ∈ loactions_to_merge && b ∈ loactions_to_merge
            continue
        elseif  a ∈ loactions_to_merge
            push_if_transmission_not_exists(L_prime, merged_location_symbol, b)
        elseif  b ∈ loactions_to_merge
            push_if_transmission_not_exists(L_prime, a, merged_location_symbol)
        else
            push!(L_prime, (a, b))
        end
    end
    L = L_prime

    # Mrge generators 
    NG_prime = Vector{Tuple}()
    for (location, generator) in NG
        if location ∈ loactions_to_merge
            if (merged_location_symbol, generator) ∉ NG_prime
                push!(NG_prime, (merged_location_symbol, generator))
            end
        else
            push!(NG_prime, (location, generator))
        end
    end
    NG = NG_prime

    return Dict(
        "time_steps" => T,
        "locations" => N,
        "transmission_lines" => L,
        "generators" => NG,
        "generation_technologies" => G,
    )
end

function get_merged_data_dict(data::ExperimentData, loactions_to_merge::Set{Symbol}, merged_location_symbol::Symbol)::Dict
    # TODO merge data
    return Dict()

function push_if_transmission_not_exists(L::Vector{Tuple}, a::Symbol, b::Symbol)
    if (a, b) ∉ L && (b, a) ∉ L
        push!(L, (a, b))
    end
end
