
def test_keymap(keymap, sides=('UP', 'DOWN', 'LEFT', 'RIGHT')):
    assert \
        all([side in keymap.values() for side in sides]), \
        f'All keys {sides} required in keymap property'
