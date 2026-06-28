import os
import sys
import importlib.util
import json
import time

ROOT = os.path.expanduser("~/A1OS")
MODULES_DIR = os.path.join(ROOT, "generators/modules")
MANIFEST_DIR = os.path.join(ROOT, "system/manifests")
MANIFEST_PATH = os.path.join(MANIFEST_DIR, "build_manifest.json")

def topological_sort(source_modules):
    """Sorts modules deterministically based on their declared dependencies."""
    visited = {}
    order = []

    def dfs(node):
        if visited.get(node) == "VISITING":
            raise ValueError(f"CRITICAL: Circular dependency loop intercepted at module structural node: [{node}]")
        if visited.get(node) == "VISITED":
            return
        
        visited[node] = "VISITING"
        # Gather dependencies if the module exists in our local registry scan
        dependencies = source_modules.get(node, {}).get("dependencies", [])
        for dep in dependencies:
            if dep in source_modules:
                dfs(dep)
        
        visited[node] = "VISITED"
        order.append(node)

    for module in source_modules:
        if module not in visited:
            dfs(module)
    return order

def runtime_compiler_pipeline():
    print("[*] Scan Phase: Discovering architecture generation matrix frames...")
    if not os.path.exists(MODULES_DIR):
        os.makedirs(MODULES_DIR, exist_ok=True)
        print("[!] Notice: Created empty generators/modules tracking layout directory.")
        return

    # 1. Scan and load generator files dynamically
    discovered_registry = {}
    for file in os.listdir(MODULES_DIR):
        if file.endswith("_gen.py"):
            mod_name = file[:-7]  # Strips off '_gen.py' to get standard module name
            file_path = os.path.join(MODULES_DIR, file)
            
            # Dynamic script import
            spec = importlib.util.spec_from_file_location(f"gen_{mod_name}", file_path)
            module_obj = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module_obj)
            
            # Instantiate with minimal baseline context shell
            context_shell = {"root": ROOT}
            instance = module_obj.Generator(context_shell)
            
            discovered_registry[mod_name] = {
                "instance": instance,
                "dependencies": getattr(instance, "dependencies", [])
            }
            print(f"[✔] Registered structural module compiler frame: {mod_name}")

    if not discovered_registry:
        print("[!] Matrix Core: Zero operational generators found in scope. Standing by.")
        return

    # 2. Resolve Topological Matrix Order
    try:
        pipeline_order = topological_sort(discovered_registry)
        print(f"[*] Graph Phase: Dependency sorting resolved -> Matrix Order: [ {' -> '.join(pipeline_order)} ]")
    except ValueError as err:
        print(f"[✘] Dependency Graph Error: {str(err)}")
        sys.exit(1)

    # 3. Execution Compilation Loop Engine
    manifest_data = {
        "compiler_version": "2.0.0",
        "generation_version": int(time.time()),
        "modules": {}
    }

    for mod_name in pipeline_order:
        print(f"--- Compiling Module: {mod_name} ---")
        generator_instance = discovered_registry[mod_name]["instance"]
        
        try:
            emitted_files = generator_instance.generate()
            manifest_data["modules"][mod_name] = {
                "status": "COMPILED",
                "emitted_artifacts": emitted_files
            }
            print(f"[✔] Emitted framework frames: {emitted_files}")
        except Exception as e:
            print(f"[✘] Compilation Failed on module [{mod_name}]: {str(e)}")
            sys.exit(1)

    # 4. Atomic Serialization of the Build Manifest Layout
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest_data, f, indent=4)
    
    print("\n[✔] PIPELINE EXECUTION SUMMARY COMPILED AND SIGNED OFF.")

if __name__ == "__main__":
    runtime_compiler_pipeline()
