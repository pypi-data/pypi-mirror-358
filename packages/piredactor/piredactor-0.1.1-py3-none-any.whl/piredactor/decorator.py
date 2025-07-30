from functools import wraps
from .config import get_config_block, load_config
from .redactor import redact_by_schema, redact_by_key_lookup

def redact_pii(config_key=None, config_path=None, placeholder="***", partial_match=False, strict_validation=False):
    """
    A decorator that redacts PII from the return value of a function.

    This decorator has three modes:
    1. Automatic (if `config_key` is None): Inspects data and redacts values if their key
       is an exact match in the `global.pii_keys` list. This is the simplest mode.
    2. Schema-based (if `config_key` is provided): Uses a specific schema from a
       configuration file for fine-grained control, including regex matches,
       value-based redaction, and other advanced features.
    3. Schema-less (Deprecated): The original functionality before schema implementation.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if config_key:
                # --- Mode 1: Schema-based Redaction ---
                global_conf, key_conf = get_config_block(config_key, config_path)
                
                schema = key_conf.get("schema", {})
                pii_keys = global_conf.get("pii_keys", [])
                regex_keys = global_conf.get("regex_keys", [])
                
                return redact_by_schema(result, schema, pii_keys, regex_keys, placeholder, partial_match, strict_validation)
            else:
                # --- Mode 2: Automatic, Key-Lookup Redaction ---
                config = load_config(config_path)
                global_conf = config.get("global", {})
                pii_keys = global_conf.get("pii_keys", [])

                return redact_by_key_lookup(result, pii_keys, placeholder)

        return wrapper
    return decorator