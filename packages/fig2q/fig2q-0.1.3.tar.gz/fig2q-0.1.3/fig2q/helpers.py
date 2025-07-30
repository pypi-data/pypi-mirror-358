import yaml
import re

# %%
def id_from_q_link(q_link):
    return re.search(r'/editor/.+?/(.+)', q_link).group(1)

id_from_q_link('https://qv2.st.nzz.ch/editor/infographic/2692908262fab35efab20e308b280b5a')

# %%
def get_yaml(file='q.yaml'):
    with open('q.yaml', 'r') as file:
        config = yaml.safe_load(file)

    print(config)
    for item in config:
        item['q'] = id_from_q_link(item['q'])
        if('staging' in item.keys()):
            item['staging'] = id_from_q_link(item['staging'])
    return config
