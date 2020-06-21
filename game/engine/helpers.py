
from game.engine.constants import *

def merge_into_list_dict(*args):
    # This function merges two dicts of the schema: {key: [value1, ...], ...} or
    # {key: value3, ...} into {key: [value1, ..., value3, ...], ...}
    # so that the list is being appended upon instead of replaced

    assert len(args) >= 2, "Expected at least 2 dicts to be merged"

    existing_dict, new_dict = args[0], args[1]

    for key in new_dict:
        if new_dict[key] is not None:
            # Modify new value to also be a list
            if isinstance(new_dict[key], tuple):
                new_dict[key] = list(new_dict[key])
            elif not isinstance(new_dict[key], list):
                new_dict[key] = [new_dict[key]]

            if key not in existing_dict or existing_dict[key] is None:
                existing_dict[key] = new_dict[key]
            else:
                if isinstance(existing_dict[key], tuple):
                    existing_dict[key] = list(existing_dict[key]) + new_dict[key]
                elif not isinstance(existing_dict[key], list):
                    existing_dict[key] = [existing_dict[key]] + new_dict[key]
                else:
                    existing_dict[key] += new_dict[key]

    # Recursively merge all given dicts
    if len(args) > 2:
        existing_dict = merge_into_list_dict(existing_dict, *(args[2:]))

    return existing_dict

def reduce_to_relevant_collisions(
        all_collisions,
        sides=('FLOOR', 'CEILING', 'LEFT_WALL', 'RIGHT_WALL'),
):
    reduced_collisions = {}

    for side in all_collisions:
        if (side in sides) and isinstance(all_collisions[side], list) or isinstance(all_collisions[side], tuple):
            collisions_count = len(all_collisions[side])
            if collisions_count > 0:
                if collisions_count > 1:
                    all_collisions[side] = list(sorted(
                        all_collisions[side], reverse=side in ('FLOOR', 'LEFT_WALL')
                    ))
                reduced_collisions[side] = all_collisions[side][0]
            else:
                reduced_collisions[side] = None
        else:
            reduced_collisions[side] = all_collisions[side]

    return reduced_collisions


def get_collision(barrier, moving_object, combat_collision=False, stacked_collision=False):

    assert not(combat_collision and player_collision), "Only one type of collision possible"
    dx_min = moving_object.size[0]/2 + barrier.size[0]/2
    dy_min = moving_object.size[1]/2 + barrier.size[1]/2

    dx = moving_object.position[0] - barrier.position[0]  # dx > 0 = other player is right from this player
    dy = moving_object.position[1] - barrier.position[1]  # dy > 0 = other player is above this player

    horizontal_overlap = (dx_min - abs(dx))
    vertical_overlap = (dy_min - abs(dy))

    collision = {}

    if vertical_overlap > 0 and horizontal_overlap > 0:

        if combat_collision:
            if vertical_overlap < horizontal_overlap and dy > 0:
                collision["BARRIER_KILLED"] = barrier
            else:
                collision["MOVING_OBJECT_KILLED"] = barrier
        else:
            if vertical_overlap < (3 * horizontal_overlap):
                if dy > 0:
                    if not stacked_collision or barrier.velocity[1] > -ERROR_MARGIN:
                        collision["FLOOR"] = barrier.position[1] + barrier.size[1]/2
                else:
                    if stacked_collision:
                        collision["OBJECT_ON_TOP"] = barrier
                    else:
                        collision["CEILING"] = barrier.position[1] - barrier.size[1]/2
            else:
                if dx > 0:
                    collision["LEFT_WALL"] = barrier.position[0] + barrier.size[0]/2
                else:
                    collision["RIGHT_WALL"] = barrier.position[0] - barrier.size[0]/2

    return collision


if __name__ == '__main__':
    a = {"a": [1, 2]}
    b = {"b": 3, "a": 5}
    c = {"b": [1, 2], "c": 3}

    print(merge_into_list_dict(a, b, c))
