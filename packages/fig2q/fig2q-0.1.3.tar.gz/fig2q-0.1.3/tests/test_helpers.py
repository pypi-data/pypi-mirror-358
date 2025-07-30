import pytest
from fig2q.helpers import id_from_q_link, get_yaml
import os
import yaml

def test_id_from_q_link():
    test_url = "https://qv2.st.nzz.ch/editor/infographic/2692908262fab35efab20e308b280b5a"
    expected_id = "2692908262fab35efab20e308b280b5a"
    assert id_from_q_link(test_url) == expected_id

def test_get_yaml(tmp_path):
    # Create a temporary YAML file
    test_yaml = """
    - type: infographic
      q: https://qv2.st.nzz.ch/editor/infographic/test123
      mw: https://www.figma.com/test
      cw: https://www.figma.com/test
    """
    yaml_path = tmp_path / "q.yaml"
    yaml_path.write_text(test_yaml)

    # Change directory to tmp_path
    os.chdir(tmp_path)

    result = get_yaml()
    assert len(result) == 1
    assert result[0]['q'] == 'test123'
