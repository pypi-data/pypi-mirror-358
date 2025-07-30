from fig2q.helpers import id_from_q_link

def get_images(item):
    _snip = []
    if 'mw' in item.keys():
        _snip.append(image_config(item, 'mw', 0))
    if 'cw' in item.keys():
        _snip.append(image_config(item, 'cw', 540))
    if ('kw' in item.keys()) & (not('fw' in item.keys())):
        _snip.append(image_config(item, 'kw', 830))
    if ('kw' in item.keys()) & ('fw' in item.keys()):
        _snip.append(image_config(item, 'kw', 1000))
        _snip.append(image_config(item, 'fw', 1600))
    return _snip

def image_config(item, size, minWidth):
    if('figma.com' in item['mw']):
        return {'images': [{'path': f'pngs/{item["q"]}_{size}.png'}], 'minWidth': minWidth}
    else:
        return {'images': [{'path': item[size]}], 'minWidth': minWidth}


# %% Modify q-config
def q_config(item):
    _snip = {
            'environments': [{
                'name': 'production',
                'id': item['q'],
            }],
            'item': {
                'images': {
                    'variants': get_images(item),
                }
            }
        }
    if('staging' in item.keys()):
        _snip['environments'].append({
            'name': 'staging',
            'id': item['staging'],
        })
    return _snip


# %% Write json-file

def infographic_config(item):
    return q_config(item)
