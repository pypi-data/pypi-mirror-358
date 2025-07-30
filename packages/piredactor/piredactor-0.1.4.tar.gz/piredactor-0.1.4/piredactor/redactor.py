import re
from .config import compile_regex_list

def redact_by_key_lookup(data, pii_keys, placeholder):
    """
    (Automatic Mode) Recursively redacts data based only on an exact key lookup in pii_keys.
    """
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
    # The regex_keys might be None if the global config is minimal
    if regex_keys and any(rx.match(key) for rx in regex_keys):
        return True
    if partial_match and any(base in key for base in pii_keys):
        return True
    return False

def redact_by_schema(data, schema, pii_keys, regex_keys, placeholder, partial_match=False, strict=False):
    """(Schema-based Mode) Recursively redacts data based on a guiding schema."""
    if isinstance(schema, dict) and isinstance(data, dict):
        result = {}
        for key, value in data.items():
            field_schema = None
            # Priority 1: Check for an exact key match first.
            if key in schema:
                field_schema = schema[key]
            else:
                # Priority 2: If no exact match, iterate schema keys to find a regex match.
                for schema_key, schema_value in schema.items():
                    try:
                        if re.match(schema_key, key):
                            field_schema = schema_value
                            break # Use the first matching regex
                    except re.error:
                        continue
            
            # --- Apply the found rule (if any) ---
            if isinstance(field_schema, dict) and "__match_value__" in field_schema:
                rule_processed = False
                if isinstance(value, str):
                    rules_dict = field_schema["__match_value__"]
                    for pattern, rule in rules_dict.items():
                        if re.match(pattern, value):
                            if rule == "no_redact":
                                result[key] = value
                            elif rule == "pii":
                                result[key] = placeholder
                            else:
                                result[key] = rule
                            rule_processed = True
                            break
                if not rule_processed:
                    result[key] = value
            elif field_schema == "no_redact":
                result[key] = value
            elif field_schema == "pii":
                result[key] = placeholder
            elif isinstance(field_schema, dict) and "pii" in field_schema:
                result[key] = field_schema["pii"]
            elif isinstance(field_schema, dict):
                if isinstance(value, dict):
                    result[key] = redact_by_schema(value, field_schema, pii_keys, regex_keys, placeholder, partial_match, strict)
                elif strict:
                    raise TypeError(f"Expected dict for key '{key}' but got {type(value).__name__}")
                else:
                    result[key] = value
            
            # --- THIS IS THE CORRECTED LOGIC FOR LISTS ---
            elif isinstance(field_schema, list) and isinstance(value, list):
                # Safely get the schema for list items. If the schema list is empty, use an empty dict.
                item_schema = field_schema[0] if field_schema else {}
                result[key] = [redact_by_schema(item, item_schema, pii_keys, regex_keys, placeholder, partial_match, strict) for item in value]
            
            # Priority 3: Fallback to global rules if no schema rule matched.
            elif is_pii_key(key, pii_keys, regex_keys, partial_match):
                result[key] = placeholder
            else:
                result[key] = value
        return result

    # This handles the case where the top-level data is a list
    elif isinstance(schema, list) and isinstance(data, list):
        item_schema = schema[0] if schema else {}
        return [redact_by_schema(item, item_schema, pii_keys, regex_keys, placeholder, partial_match, strict) for item in data]

    if strict and schema and not isinstance(data, type(schema)):
        raise TypeError(f"Schema/data type mismatch: Schema is {type(schema).__name__} but data is {type(data).__name__}")
    return data