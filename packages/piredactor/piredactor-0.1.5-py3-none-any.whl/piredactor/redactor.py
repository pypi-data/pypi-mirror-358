import re
from .config import compile_regex_list

def redact_by_key_lookup(data, pii_keys, placeholder):
    """(Automatic Mode) Recursively redacts data based only on an exact key lookup in pii_keys."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in pii_keys:
                result[key] = placeholder
            elif isinstance(value, (dict, list)):
                result[key] = redact_by_key_lookup(value, pii_keys, placeholder)
            else:
                result[key] = value
        return result
    if isinstance(data, list):
        return [redact_by_key_lookup(item, pii_keys, placeholder) for item in data]
    return data

def is_pii_key(key, pii_keys, regex_keys, partial_match=False):
    """(Helper) Checks if a key should be considered PII based on global rules."""
    if key in pii_keys:
        return True
    if regex_keys and any(rx.match(key) for rx in regex_keys):
        return True
    if partial_match and any(base in key for base in pii_keys):
        return True
    return False

def redact_by_schema(data, schema, pii_keys, regex_keys, placeholder, partial_match=False, strict=False):
    """(Schema-based Mode) Recursively redacts data based on a guiding schema."""
    # Base case for recursion: if data is not a dict or list, return it as is.
    if not isinstance(data, (dict, list)):
        return data

    # Handle top-level list case
    if isinstance(data, list):
        item_schema_container = schema[0] if isinstance(schema, list) and schema else {}
        item_schema = item_schema_container.get("schema", {})
        return [redact_by_schema(item, item_schema, pii_keys, regex_keys, placeholder, partial_match, strict) for item in data]

    # Main logic for dictionaries
    if isinstance(data, dict) and isinstance(schema, dict):
        result = {}
        for key, value in data.items():
            field_schema = None
            if key in schema:
                field_schema = schema[key]
            else:
                for schema_key, schema_value in schema.items():
                    try:
                        if re.match(schema_key, key):
                            field_schema = schema_value
                            break
                    except re.error:
                        continue

            # --- A rule was found in the schema ---
            if field_schema is not None:
                if isinstance(field_schema, dict) and "__match_value__" in field_schema:
                    rule_processed = False
                    if isinstance(value, str):
                        rules_dict = field_schema["__match_value__"]
                        for pattern, rule in rules_dict.items():
                            if re.match(pattern, value):
                                if rule == "no_redact": result[key] = value
                                elif rule == "pii": result[key] = placeholder
                                else: result[key] = rule
                                rule_processed = True
                                break
                    if not rule_processed: result[key] = value
                elif field_schema == "no_redact":
                    result[key] = value
                elif field_schema == "pii":
                    result[key] = placeholder
                elif isinstance(field_schema, dict) and "pii" in field_schema:
                    result[key] = field_schema["pii"]
                elif isinstance(field_schema, dict) and isinstance(value, dict):
                    result[key] = redact_by_schema(value, field_schema, pii_keys, regex_keys, placeholder, partial_match, strict)
                elif isinstance(field_schema, list) and isinstance(value, list):
                    item_schema_container = field_schema[0] if field_schema else {}
                    item_schema = item_schema_container.get("schema", {})
                    result[key] = [redact_by_schema(item, item_schema, pii_keys, regex_keys, placeholder, partial_match, strict) for item in value]
                else:
                    if strict:
                        raise TypeError(f"Schema/data type mismatch for key '{key}'. Schema expects {type(field_schema).__name__}, but data is {type(value).__name__}.")
                    result[key] = value # A rule existed, but didn't apply due to a type mismatch. Keep the original value.

            # --- No rule found in schema, fallback to global ---
            else:
                if is_pii_key(key, pii_keys, regex_keys, partial_match):
                    result[key] = placeholder
                else:
                    result[key] = value
        return result

    # Fallback if data is a dict but schema is not (or vice-versa)
    if strict:
        raise TypeError(f"Top-level schema/data type mismatch: Schema is {type(schema).__name__}, data is {type(data).__name__}")
    return data