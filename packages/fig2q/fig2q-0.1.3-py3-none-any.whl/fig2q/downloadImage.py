# %%
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import os
from fig2q.helpers import get_yaml



FIGMA_TOKEN = os.getenv('FIGMA_TOKEN')  # Get token from environment variable
if not FIGMA_TOKEN:
    raise ValueError("FIGMA_TOKEN environment variable is not set")


example = 'https://www.figma.com/design/qiY7mWWSxQjrSG2d50wxFv/WI-Schweiz-Deutschland-Import%2FExport-(joe)?node-id=45-11&t=zd5V2pw1gLGsrwCv-11'

# %%
def get_file_id(link):
    return re.search(r'/design/(.+?)/', link).group(1)

get_file_id(example)

# %%
def get_artboard_url_id(link):
    return re.search(r'node-id=(.+?)&', link).group(1)

get_artboard_url_id(example)
# %%
def get_artboard_id(link):
    return str.replace(re.search(r'node-id=(.+?)&', link).group(1), '-', ':')

get_artboard_id(example)

# %%
def image_url(file_id, artboard_id, scale=3):
    scale = str(scale)
    api = 'https://api.figma.com/v1/images/'
    return api + file_id + '?ids=' + artboard_id + '&scale=' + scale

# %% Create folder if it doesn't exist
def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
# %%
def download_image(link, name='mw', folder='pngs', max_retries=3):
    if not ('https://www.figma.com' in link):
        return None

    # Setup retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    _headers = {
        'X-FIGMA-TOKEN': FIGMA_TOKEN
    }

    img_url = image_url(get_file_id(link), get_artboard_url_id(link), 3)
    print(img_url)

    try:
        where_img = session.get(img_url, headers=_headers)
        where_img.raise_for_status()
    except Exception as e:
        raise Exception(f'Link zum Artboard funktioniert nicht: {str(e)}')

    img = where_img.json()['images'][get_artboard_id(link)]

    # Download the actual image with retry logic
    for attempt in range(max_retries):
        try:
            ensure_folder(folder)
            response = session.get(img, stream=True)
            response.raise_for_status()

            with open(name, 'wb') as file:
                # Download in chunks
                chunk_size = 8192
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
            return True

        except requests.exceptions.ChunkedEncodingError as e:
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed to download after {max_retries} attempts: {str(e)}")
            print(f"Download attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

#download_image(example, 'cw')
