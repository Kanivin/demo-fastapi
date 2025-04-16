import os
import json

TEMPLATE_JSON = {
    "name": "",
    "doctype": "DocType",
    "fields": [
        {"fieldname": "name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "email", "fieldtype": "Email"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Active\nInactive"}
    ]
}

TEMPLATE_HOOKS = '''def on_create(doc, db):
    print(f"[HOOK] Created {doc.__class__.__name__}:", doc.id)

def on_update(doc, db):
    print(f"[HOOK] Updated {doc.__class__.__name__}:", doc.id)

def on_delete(doc, db):
    print(f"[HOOK] Deleted {doc.__class__.__name__}:", doc.id)
'''

TEMPLATE_API = '''# Optional custom endpoints for this module
from fastapi import APIRouter

router = APIRouter()

@router.get("/custom-example")
def custom_logic():
    return {"message": "This is a custom endpoint"}
'''


def create_module(app_name: str, doctype_name: str):
    base_path = f"app/modules/{app_name}/{doctype_name}"
    os.makedirs(base_path, exist_ok=True)

    # Create doctype.json
    doc_json = TEMPLATE_JSON.copy()
    doc_json["name"] = doctype_name.capitalize()
    with open(f"{base_path}/doctype.json", "w") as f:
        json.dump(doc_json, f, indent=2)

    # Create hooks.py
    with open(f"{base_path}/hooks.py", "w") as f:
        f.write(TEMPLATE_HOOKS)

    # Create api.py
    with open(f"{base_path}/api.py", "w") as f:
        f.write(TEMPLATE_API)

    print(f"✅ Created new module: {base_path}")

# Example usage
# create_module("hr", "employee")
