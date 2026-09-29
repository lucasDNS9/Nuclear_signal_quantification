# -*- coding: utf-8 -*-
"""
Created on Wed Sept 2026

@author: Lucas Denis
"""
from pathlib import Path
import yaml


def load_config():

    config_path = Path(__file__).parent.parent / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)