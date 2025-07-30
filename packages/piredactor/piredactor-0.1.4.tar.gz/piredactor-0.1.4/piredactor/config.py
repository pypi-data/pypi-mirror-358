import json
import re
import os
import yaml
from functools import lru_cache
from copy import deepcopy

def compile_regex_list(raw_patterns, context="global"):
    """Compiles a list of raw string regex patterns into regex objects."""
    compiled = []
    for pattern in raw_patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error as e:
            raise ValueError(f"Invalid regex '{pattern}' in '{context}': {e}")
    return compiled

def _load_config_from_path(path):
    """Helper to load a single config file from a given path."""
    if not os.path.exists(path):
        return None
    
    ext = os.path.splitext(path)[-1].lower()
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) if ext in [".yaml", ".yml"] else json.load(f)
    except (IOError, yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load or parse config file at {path}. Error: {e}")
        return None

def _merge_configs(base_config, user_config):
    """
    Merges the user config on top of the base config. The user's 'global' block
    will intelligently update the base 'global' block.
    """
    final_config = deepcopy(base_config)
    
    if "global" in user_config:
        final_config.setdefault("global", {}).update(user_config["global"])

    for key, value in user_config.items():
        if key != "global":
            final_config[key] = value

    return final_config

@lru_cache(maxsize=32)
def load_config(config_path=None):
    """
    Loads configuration with a priority-based search and merging strategy.
    """
    default_path = os.path.join(os.path.dirname(__file__), "pii_config.json")
    final_config = _load_config_from_path(default_path) or {}

    user_config = None
    if config_path:
        user_config = _load_config_from_path(config_path)
        if user_config is None:
            raise FileNotFoundError(f"Config file explicitly passed but not found at: {config_path}")
    else:
        project_config_names = ['piredactor.yaml', 'piredactor.json', 'pii_config.yaml', 'pii_config.json']
        for name in project_config_names:
            path = os.path.join(os.getcwd(), name)
            user_config = _load_config_from_path(path)
            if user_config:
                break
    
    if user_config:
        final_config = _merge_configs(final_config, user_config)

    global_block = final_config.get("global", {})
    if "regex_keys" in global_block and isinstance(global_block["regex_keys"], list):
        global_block["regex_keys"] = compile_regex_list(
            global_block["regex_keys"], "global")
    final_config["global"] = global_block
    
    return final_config

def get_config_block(config_key, config_path=None):
    """
    Retrieves the global and a specific key's configuration block using the new loading logic.
    """
    config = load_config(config_path)
    if config_key not in config:
        raise ValueError(f"Config key '{config_key}' not found. Available keys: {list(config.keys())}")
    return config.get("global", {}), config[config_key]