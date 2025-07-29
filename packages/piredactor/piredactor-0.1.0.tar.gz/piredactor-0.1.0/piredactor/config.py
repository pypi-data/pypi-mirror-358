import json
import re
import os
import yaml
from functools import lru_cache


def compile_regex_list(raw_patterns, context="global"):
    compiled = []
    for pattern in raw_patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error as e:
            raise ValueError(f"Invalid regex '{pattern}' in '{context}': {e}")
    return compiled


@lru_cache(maxsize=32)
def load_config(config_path=None):
    path = config_path or os.path.join(
        os.path.dirname(__file__), "pii_config.json")
    ext = os.path.splitext(path)[-1].lower()
    with open(path, "r") as f:
        config = yaml.safe_load(f) if ext in [
            ".yaml", ".yml"] else json.load(f)

    global_block = config.get("global", {})
    if "regex_keys" in global_block:
        global_block["regex_keys"] = compile_regex_list(
            global_block["regex_keys"], "global")
    config["global"] = global_block
    return config


def get_config_block(config_key, config_path=None):
    config = load_config(config_path)
    if config_key not in config:
        raise ValueError(f"Config key '{config_key}' not found in config.")
    return config["global"], config[config_key]