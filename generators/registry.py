import os
import importlib
import sys
import inspect
from pathlib import Path

class UnifiedGeneratorAdapter:
    """
    A unified execution proxy that safely adapts ANY module layout signature
    (legacy dictionary-based or new native Sovereign) at runtime.
    """
    def __init__(self, gen_cls, name, dependencies):
        self.gen_cls = gen_cls
        self.name = name
        self.dependencies = dependencies

    def generate(self, context, writer):
        # Step 1: Resilient Instantiation Engine
        try:
            # Try legacy instantiation first
            instance = self.gen_cls(context)
        except TypeError:
            # Fallback cleanly to modern zero-argument initialization
            instance = self.gen_cls()

        # Step 2: Resilient Execution Entry Point Routing
        if hasattr(instance, 'generate_all'):
            target_method = getattr(instance, 'generate_all')
        elif hasattr(instance, 'generate'):
            target_method = getattr(instance, 'generate')
        else:
            raise AttributeError(f"Module Engine [{self.name}] has no executable generation methods.")

        # Step 3: Argument Matrix Matching
        sig = inspect.signature(target_method)
        params = list(sig.parameters.keys())

        if 'context' in params and 'writer' in params:
            return target_method(context, writer)
        elif 'writer' in params:
            return target_method(writer)
        elif 'context' in params:
            return target_method(context)
        else:
            return target_method()

class GeneratorRegistry:
    def __init__(self, root_dir):
        self.root = Path(root_dir).resolve()
        self.modules_dir = self.root / "generators/modules"
        self.generators = {}

    def discover(self):
        sys.path.insert(0, str(self.root))
        if not self.modules_dir.exists():
            return

        for file in self.modules_dir.glob("*_gen.py"):
            if file.name.startswith("pre_deploy"):
                continue
                
            mod_name = f"generators.modules.{file.stem}"
            try:
                if mod_name in sys.modules:
                    importlib.reload(sys.modules[mod_name])
                else:
                    importlib.import_module(mod_name)
                
                module = sys.modules[mod_name]
                if hasattr(module, "Generator"):
                    gen_cls = getattr(module, "Generator")
                    
                    name = getattr(gen_cls, "name", file.stem.replace("_gen", ""))
                    dependencies = getattr(gen_cls, "dependencies", [])
                    
                    # Every module is wrapped in our unified proxy to guarantee runtime execution safety
                    self.generators[name] = UnifiedGeneratorAdapter(gen_cls, name, dependencies)
                    print(f"🔒 Bound Engine Node via Unified Adapter Proxy: [{name}]")
            except Exception as e:
                print(f"❌ Failed loading module generator {mod_name}: {e}")

    def resolve_order(self) -> list:
        ordered = []
        visited = {}
        
        def visit(node):
            if visited.get(node) == "visiting":
                raise RuntimeError(f"Circular dependency detected in structural layer: {node}")
            if visited.get(node) == "done":
                return
            
            visited[node] = "visiting"
            gen = self.generators.get(node)
            if gen and hasattr(gen, "dependencies"):
                for dep in gen.dependencies:
                    if dep in self.generators:
                        visit(dep)
            
            visited[node] = "done"
            ordered.append(node)

        for name in list(self.generators.keys()):
            if name not in visited:
                visit(name)
        return ordered
