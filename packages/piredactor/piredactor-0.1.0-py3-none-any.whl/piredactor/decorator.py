from functools import wraps
from .config import get_config_block
from .redactor import redact_by_schema


def redact_pii(config_key, config_path=None, placeholder="***", partial_match=False, strict_validation=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            global_conf, key_conf = get_config_block(config_key, config_path)
            schema = key_conf.get("schema", {})
            pii_keys = global_conf.get("pii_keys", [])
            regex_keys = global_conf.get("regex_keys", [])
            return redact_by_schema(result, schema, pii_keys, regex_keys, placeholder, partial_match, strict_validation)
        return wrapper
    return decorator