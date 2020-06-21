
def merge_into_list_dicts(list_dict, value_dict):
    # This function merges two dicts of the schema: {key: [value1, ...], ...} and
    # {key: value3, ...} into {key: [value1, ..., value3, ...], ...}
    # so that the list is being appended upon instead of replaced

    for key in value_dict:
        if key not in list_dict:
            list_dict[key] = [value_dict[key]]
        else:
            list_dict[key].append(value_dict[key])

    return list_dict

def reduce_to_relevant_collisions(
        all_collisions,
        fixed_collisions=None,
        sides=('FLOOR', 'CEILING', 'LEFT_WALL', 'RIGHT_WALL')
):
    if fixed_collisions is None:
        fixed_collisions = {}

    for side in sides:
        collisions_count = len(all_collisions[side])
        if collisions_count > 0:
            if collisions_count > 1:
                all_collisions[side] = list(sorted(
                    all_collisions[side], reverse=side in ('FLOOR', 'LEFT_WALL')
                ))
            fixed_collisions[side] = all_collisions[side][0]
    return fixed_collisions
