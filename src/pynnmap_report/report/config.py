"""
Specialized configuration parameters read from config.yaml
"""

from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

GNN_RELEASE_VERSION = config["release_version"]
FONTS = config["fonts"]
