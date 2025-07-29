# 📦 Piredactor

A lightweight, decorator-based Python package for redacting Personally Identifiable Information (PII) from function return values using a config-driven schema approach.

---

## ✅ Features

- 🔐 Redact sensitive fields like email, password, tokens, phone numbers, credit card info, etc.
- ⚙️ Configurable via JSON or YAML
- 🎯 Supports nested structures, lists, and schema-based rules
- 🧠 Supports exact, partial, and regex key matching
- 🚀 Fast with internal caching (no re-parsing config per call)
- 📌 Optional strict schema/data validation

---

## 📥 Installation

```bash
pip install piredactor  # after publishing
```

For development:

```bash
git clone <repo-url>
cd piredactor
pip install -e .
```

---

## 🚀 Usage

### Step 1: Add Config File (JSON or YAML)

```json
{
  "global": {
    "pii_keys": [
      "email", "phone", "mobile", "address", "name", "full_name", "dob",
      "birthdate", "ssn", "credit_card", "card_number", "cvv", "pan",
      "passport", "aadhaar", "zipcode", "zip", "pin", "ip", "location"
    ],
    "regex_keys": [
      "^.*token.*$", "^secret_.*$", "^auth_.*$", ".*_key$",
      "(?i)^.*credit.*card.*$", "(?i)^.*ssn.*$", "(?i)^.*dob.*$",
      "(?i)^.*ip(_address)?$", "(?i)^.*name.*$", "(?i)^.*phone.*$"
    ]
  },
  "user_data": {
    "schema": {
      "user": {
        "email": "pii",
        "password": { "pii": "HIDDEN" },
        "addresses": [
          {
            "zip": "pii",
            "city": "no_redact"
          }
        ]
      },
      "session": {
        "__regex_keys__": ["^auth_.*$"],
        "auth_token": "pii",
        "auth_key": "pii"
      }
    }
  }
}
```

### Step 2: Decorate Your Function

```python
from piredactor import redact_pii

@redact_pii(config_key="user_data", placeholder="REDACTED")
def get_user():
    return {
        "user": {
            "email": "test@example.com",
            "password": "mypassword",
            "addresses": [{"zip": "12345", "city": "Delhi"}]
        },
        "session": {
            "auth_token": "abcd1234",
            "auth_key": "mykey",
            "user_id": 42
        }
    }
```

---

## ⚙️ Options

| Param               | Type    | Default  | Description                           |
|---------------------|---------|----------|---------------------------------------|
| `config_key`        | str     | required | Which schema to use from config       |
| `config_path`       | str     | optional | Custom config file path               |
| `placeholder`       | str     | `***`    | Value to replace PII fields           |
| `partial_match`     | bool    | False    | Match fields partially                |
| `strict_validation` | bool    | False    | Raise if schema doesn't match payload |

---

## 📜 License

MIT © 2025 Piyush Chauhan