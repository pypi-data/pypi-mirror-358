def get_images(step, q, index):
    _variants = []
    if 'mw' in step.keys():
        _variants.append(image_config(step, index, q, 'mw', 0))
    if 'cw' in step.keys():
        _variants.append(image_config(step, index, q, 'cw', 540))
    if ('kw' in step.keys()) & (not('fw' in step.keys())):
        _variants.append(image_config(step, index, q, 'kw', 830))
    if ('kw' in step.keys()) & ('fw' in step.keys()):
        _variants.append(image_config(step, index, q, 'kw', 1000))
        _variants.append(image_config(step, index, q, 'fw', 1600))
    return _variants


def image_config(item, index, q, size, minWidth):
    print(q)
    if('figma.com' in item[size]):
        return {'asset': {'path': f'pngs/{q}_step{index}_{size}.png'}, 'minWidth': minWidth}
    else:
        return {'asset': {'path': item[size]}, 'minWidth': minWidth}


# %%
def get_step(step, q, index):
    return {
        'variants': get_images(step, q, index),
        'text': step['text']
    }

# %%
def get_steps(item):
    q = item['q']
    return [get_step(step, q, index) for index, step in enumerate(item['steps'])]



# %% Modify q-config
def q_config(item):
    _snip = {
            'environments': [{
                'name': 'production',
                'id': item['q'],
            }],
            'item': {'steps': get_steps(item)}
        }

    if('staging' in item.keys()):
        _snip['environments'].append({
            'name': 'staging',
            'id': item['staging'],
        })
    return _snip



# %% Write json-file

def scroll_graphic_config(item):
    return q_config(item)
