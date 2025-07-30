# ✅ Plugin Definition Guide

## 📦 Overview

All Hookline-compatible plugins **must include**:

* `config.json` — Plugin metadata and user-configurable schema
* `execution.py` — Defines a class-based plugin implementation using the `hookline-sdk`

---

## 📁 Files Required

### 1. `config.json`

Defines plugin metadata and config schema.

✅ **Example:**

```json
{
  "name": "Email Sender",
  "slug": "email_sender",
  "description": "Sends an email notification to a specified address.",
  "version": "1.0",
  "author": "Hookline",
  "icon": "https://yourdomain.com/assets/email_icon.png",
  "config_schema": {
    "to": {
      "type": "string",
      "required": true,
      "description": "Recipient email address"
    },
    "subject": {
      "type": "string",
      "required": true,
      "description": "Email subject"
    },
    "body": {
      "type": "string",
      "required": true,
      "description": "Email body. Supports placeholders like {event_type}, {task_id}"
    }
  }
}
```

---

## 2. `execution.py`

Defines plugin logic using the `hookline-sdk`.

### ✅ Structure Requirements:

* You must **subclass `HooklinePlugin`** from `hookline_sdk.base`.
* Define your execution methods inside the class.
* Each versioned method must be decorated with `@plugin_version("x.y.z")`.
* The method name can be anything, but it **must accept** two arguments:

  * `payload: dict`
  * `config: dict`

---

## 🧩 Example Plugin Code (`execution.py`)

```python
from hookline_sdk.base import HooklinePlugin
from hookline_sdk.registry import plugin_version

class EmailSenderPlugin(HooklinePlugin):

    @plugin_version("1.0")
    def send_email_v1(self, payload: dict, config: dict) -> dict:
        try:
            # Simulate email sending logic
            email_id = "email_abc123"
            timestamp = "2025-06-24T10:30:00Z"

            return {
                "status": "success",
                "message": "Email sent successfully.",
                "status_code": 200,
                "output": {
                    "email_id": email_id,
                    "sent_at": timestamp
                }
            }

        except Exception as e:
            return {
                "status": "failed",
                "message": f"Error: {str(e)}",
                "status_code": 500,
                "output": None
            }
```

---

## 🛠 Version Management

To support backward compatibility:

* Every plugin function should be versioned using the `@plugin_version("x.y.z")` decorator.
* When a plugin is upgraded, the old version's logic can still be retained using version-specific methods.

---

## ✅ Return Value Requirements

Each versioned function must return a dictionary in the following format:

```json
{
  "status": "success" | "failed",
  "message": "Human-readable status",
  "status_code": 200,
  "output": { ... }  // Optional
}
```

| Field         | Required | Description                                       |
| ------------- | -------- | ------------------------------------------------- |
| `status`      | ✅        | `"success"` or `"failed"`                         |
| `message`     | ✅        | Short explanation of the outcome                  |
| `status_code` | ✅        | Valid HTTP status code                            |
| `output`      | ❌        | Dictionary containing plugin-specific result info |

---

## 🔄 Lifecycle Flow

1. **User installs the plugin** via Hookline's frontend (from the plugin marketplace).
2. **User provides configuration** (as per `config_schema` in `config.json`).
3. **Workflow is triggered**, and the plugin is invoked with the relevant:

   * `payload` (from the triggering event)
   * `config` (from user-specified settings)
4. **The matching versioned method** is looked up from the class and executed.

---

## ⏱ Execution Constraints

| Constraint         | Limit                            |
| ------------------ | -------------------------------- |
| **Max Duration**   | 60 seconds                       |
| **Timeout Action** | Plugin will return timeout error |
| **Retries**        | Managed by workflow engine       |

---

## 📦 How to Use Hookline SDK

* Add `hookline-sdk` as a dependency in your `requirements.txt`
* To install from GitHub (for example):

```bash
pip install git+https://github.com/your-org/hookline-sdk.git
```