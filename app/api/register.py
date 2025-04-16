import importlib.util
import os
import json
from fastapi import APIRouter
from pathlib import Path

from core.doctype.router import build_crud_router
from core.doctype.pydantic_gen import generate_model_and_schema
from core.registry import model_registry, schema_registry
from core.config import Base, engine

MODULES_PATH = "modules"

def load_dynamic_routes():
    master_router = APIRouter()

    for module in os.listdir(MODULES_PATH):
        module_path = os.path.join(MODULES_PATH, module)
        if not os.path.isdir(module_path):
            continue

        for submodule in os.listdir(module_path):
            sub_path = os.path.join(module_path, submodule)
            doctype_file = os.path.join(sub_path, "doctype.json")
            hooks_path = os.path.join(sub_path, "hooks.py")
            hooks = None

            if not os.path.isfile(doctype_file):
                continue

            # Load hooks if available
            if os.path.isfile(hooks_path):
                try:
                    module_name = f"{module}_{submodule}_hooks"
                    spec = importlib.util.spec_from_file_location(module_name, hooks_path)
                    hooks_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(hooks_mod)
                    hooks = hooks_mod
                except Exception as e:
                    print(f"⚠️ Failed to load hooks for {module}/{submodule}: {e}")

            try:
                with open(doctype_file, "r") as f:
                    doc_json = json.load(f)
                model_name = doc_json.get("name")
                if not model_name:
                    raise ValueError(f"Missing 'name' in {doctype_file}")
            except Exception as e:
                raise RuntimeError(f"❌ Error reading {doctype_file}: {e}")

            try:
                model_code, schema_code = generate_model_and_schema(Path(doctype_file))
            except Exception as e:
                raise RuntimeError(f"❌ Error generating model/schema for {doctype_file}: {e}")

            namespace = {}
            try:
                exec(model_code, namespace)
                exec(schema_code, namespace)
            except Exception as e:
                raise RuntimeError(f"❌ Error executing generated code for {module}/{submodule}: {e}")

            try:
                model = namespace[model_name]
                create_schema = namespace[f"{model_name}Create"]
                read_schema = namespace[f"{model_name}Read"]
            except KeyError as e:
                raise RuntimeError(f"❌ Expected schema '{e.args[0]}' not found in {module}/{submodule}.")

            # ✅ Register models/schemas
            model_key = f"{module}.{submodule}".lower()
            model_registry[model_key] = model
            schema_registry[f"{model_key}.create"] = create_schema
            schema_registry[f"{model_key}.read"] = read_schema

            try:
                router = build_crud_router(model_key, route_prefix=f"/{module.lower()}/{submodule.lower()}", hooks=hooks)
                master_router.include_router(router)
            except Exception as e:
                raise RuntimeError(f"❌ Error building or including router for {module}/{submodule}: {e}")

    # ✅ Create all tables at the end
    Base.metadata.create_all(bind=engine)

    print("\n📦 Registered Models:", list(model_registry.keys()))
    print("📦 Registered Schemas:", list(schema_registry.keys()))

    return master_router
