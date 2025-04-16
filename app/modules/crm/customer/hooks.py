from pathlib import Path
import importlib.util
import os
from fastapi import APIRouter
from core.doctype.router import build_router
from core.doctype.pydantic_gen import generate_model_and_schema

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

            # Check if hooks.py exists and load it dynamically
            if os.path.isfile(hooks_path):
                module_name = f"{module}_{submodule}_hooks"  # Create a unique name for the hooks module
                spec = importlib.util.spec_from_file_location(module_name, hooks_path)
                hooks_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(hooks_mod)
                hooks = hooks_mod

            # Process doctype.json if exists
            if os.path.isfile(doctype_file):
                model_code, schema_code = generate_model_and_schema(Path(doctype_file))
                namespace = {}

                try:
                    exec(model_code, namespace)
                    exec(schema_code, namespace)
                except Exception as e:
                    raise RuntimeError(f"Error executing generated code for {module}/{submodule}: {e}")

                # Extract the generated model and schemas from the namespace
                try:
                    model = namespace[module.capitalize()]
                    create_schema = namespace[f"{module.capitalize()}Create"]
                    read_schema = namespace[f"{module.capitalize()}Read"]
                except KeyError as e:
                    raise RuntimeError(f"Expected schema '{e.args[0]}' not found in namespace.")

                # Build the router and include it
                router = build_router(model, create_schema, read_schema, hooks)
                master_router.include_router(router, prefix=f"/{module.lower()}")

    return master_router
