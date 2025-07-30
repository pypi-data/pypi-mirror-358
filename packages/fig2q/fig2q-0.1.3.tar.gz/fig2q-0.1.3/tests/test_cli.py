import pytest
import os
from pathlib import Path
from fig2q.cli import main

def test_infographic_integration():
    # Get paths
    fixture_dir = Path(__file__).parent / 'fixtures' / 'infographic'
    q_yaml = fixture_dir / 'q.yaml'
    png_dir = fixture_dir / 'pngs'
    config_file = fixture_dir / 'q.config.json'

    # Remove existing files if they exist
    if png_dir.exists():
        for file in png_dir.glob('*'):
            file.unlink()
        png_dir.rmdir()
    if config_file.exists():
        config_file.unlink()

    # Store original directory
    original_dir = os.getcwd()
    os.chdir(fixture_dir)

    try:
        # Run CLI
        main([q_yaml])

        # Verify q.config.json was created
        assert config_file.exists()

        # Verify expected PNG files were created
        expected_files = [
            'pngs/2692908262fab35efab20e308b280b5a_mw.png',
            'pngs/2692908262fab35efab20e308b280b5a_cw.png',
            'pngs/2692908262fab35efab20e308b280b5a_kw.png'
        ]

        for file in expected_files:
            assert (fixture_dir / file).exists()

    finally:
        # Cleanup: restore original directory
        os.chdir(original_dir)
