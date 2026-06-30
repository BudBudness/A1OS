import sys
import importlib
from pathlib import Path

# Fix module resolution paths
sys.path.insert(0, str(Path(".").resolve()))
sys.path.insert(0, str(Path("generators/core").resolve()))

from generators.core.schema_loader import SchemaLoader
from generators.core.artifact_writer import ArtifactWriter

def run_orchestrated_generation():
    print("==================================================")
    # Define execution context with base required keys
    context = {
        "build_dir": "build/generated",
        "root": "/data/data/com.termux/files/home/A1OS",
        "port": 8086
    }

    try:
        schema = SchemaLoader("schema/platform.json")
        context["schema"] = schema
        context["port"] = schema.get_runtime().get("port", 8086) if hasattr(schema, 'get_runtime') else 8086
    except Exception as e:
        print(f"[COMPILER-WARN] Missing schema map configuration ({e}). Using core fallback context.")

    # Instantiate the authoritative Class-based writer
    writer = ArtifactWriter(".")
    
    # Discover and execute all functional module generators dynamically
    modules_dir = Path("generators/modules")
    generator_files = sorted(modules_dir.glob("*_gen.py"))
    
    print(f"Discovered {len(generator_files)} structural generator modules.")
    print("==================================================")

    for gen_file in generator_files:
        mod_name = f"generators.modules.{gen_file.stem}"
        try:
            module = importlib.import_module(mod_name)
            klass = None
            for attr in dir(module):
                if attr.endswith("Generator") and attr != "BaseGenerator":
                    klass = getattr(module, attr)
                    break
            
            if klass:
                gen_instance = klass(context)
                gen_instance.generate()
            else:
                print(f"[COMPILER-SKIP] No valid Generator class found in {gen_file.name}")
        except Exception as e:
            print(f"[COMPILER-ERROR] Failed executing module {gen_file.name}: {e}")

    print("==================================================")
    print("✅ Comprehensive Platform Generation Complete.")
    print("==================================================")

if __name__ == "__main__":
    run_orchestrated_generation()
