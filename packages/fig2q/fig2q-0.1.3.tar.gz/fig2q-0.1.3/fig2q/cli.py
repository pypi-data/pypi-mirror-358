# %%
import json
import sys
import os


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # If args provided, use first arg as yaml path
    if args:
        yaml_path = os.path.abspath(args[0])
        working_dir = os.path.dirname(yaml_path)
    else:
        working_dir = os.getcwd()
        yaml_path = os.path.join(working_dir, 'q.yaml')

    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML file not found at: {yaml_path}")

    os.chdir(working_dir)

    from fig2q.downloadImage import download_image
    from fig2q.infographic_config import infographic_config
    from fig2q.scroll_graphic_config import scroll_graphic_config
    from fig2q.helpers import get_yaml

    config = get_yaml()

    # First download all the images
    for item in config:
        if(item['type'] == 'infographic'):
            download_image(item['mw'], f'pngs/{item["q"]}_mw.png')
            download_image(item['cw'], f'pngs/{item["q"]}_cw.png')
            if 'kw' in item.keys():
                download_image(item['kw'], f'pngs/{item["q"]}_kw.png')
            if 'fw' in item.keys():
                download_image(item['fw'], f'pngs/{item["q"]}_fw.png')
        elif(item['type'] == 'scroll_graphic'):
            for index, step in enumerate(item['steps']):
                download_image(step['mw'], f'pngs/{item["q"]}_step{index}_mw.png')
                download_image(step['cw'], f'pngs/{item["q"]}_step{index}_cw.png')
                if 'kw' in step.keys():
                    download_image(step['kw'], f'pngs/{item["q"]}_step{index}_kw.png')
                if 'fw' in step.keys():
                    download_image(step['fw'], f'pngs/{item["q"]}_step{index}_fw.png')


    # Then, create the q.config.json file
    jsonConfig = {'items': []}
    for item in config:
        if item['type'] == 'infographic':
            jsonConfig['items'].append(infographic_config(item))
        elif item['type'] == 'scroll_graphic':
            jsonConfig['items'].append(scroll_graphic_config(item))


    with open('q.config.json', 'w') as f:
        json.dump(jsonConfig, f, indent=4)

    # Finally, execute the q cli command
    import subprocess
    p = subprocess.run(['npx', '@nzz/q-cli', 'update-item'])

if __name__ == '__main__':
    main()
