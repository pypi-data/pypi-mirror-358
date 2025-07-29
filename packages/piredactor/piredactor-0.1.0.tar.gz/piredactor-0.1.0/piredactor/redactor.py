from .config import compile_regex_list


def is_pii_key(key, pii_keys, regex_keys, partial_match=False):
    if key in pii_keys:
        return True
    if any(rx.match(key) for rx in regex_keys):
        return True
    if partial_match and any(base in key for base in pii_keys):
        return True
    return False


def redact_by_schema(data, schema, pii_keys, regex_keys, placeholder, partial_match=False, strict=False):
    if isinstance(schema, dict) and isinstance(data, dict):
        local_regex = compile_regex_list(schema.get(
            "__regex_keys__", []), context="local") if "__regex_keys__" in schema else regex_keys
        result = {}
        for key, value in data.items():
            if key == "__regex_keys__":
                continue
            field_schema = schema.get(key)

            if field_schema == "no_redact":
                result[key] = value
            elif field_schema == "pii":
                result[key] = placeholder
            elif isinstance(field_schema, dict) and "pii" in field_schema:
                result[key] = field_schema["pii"]
            elif isinstance(field_schema, dict):
                if isinstance(value, dict):
                    result[key] = redact_by_schema(
                        value, field_schema, pii_keys, local_regex, placeholder, partial_match, strict)
                elif strict:
                    raise TypeError(
                        f"Expected dict for key '{key}' but got {type(value).__name__}")
                else:
                    result[key] = value
            elif isinstance(field_schema, list) and isinstance(value, list):
                item_schema = field_schema[0]
                result[key] = [
                    redact_by_schema(
                        item, item_schema, pii_keys, local_regex, placeholder, partial_match, strict)
                    for item in value
                ]
            elif is_pii_key(key, pii_keys, local_regex, partial_match):
                result[key] = placeholder
            else:
                result[key] = value
        return result

    elif isinstance(schema, list) and isinstance(data, list):
        return [
            redact_by_schema(
                item, schema[0], pii_keys, regex_keys, placeholder, partial_match, strict)
            for item in data
        ]

    if strict and type(schema) != type(data):
        raise TypeError(
            f"Schema/data type mismatch: {type(schema).__name__} vs {type(data).__name__}")
    return data