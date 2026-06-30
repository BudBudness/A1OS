import os
import json
from pathlib import Path
from generators.core.context import GenerationContext
from generators.core.artifact_writer import ArtifactWriter
from generators.registry import GeneratorRegistry

class SovereignRuntimeEngine:
    def __init__(self, root_dir):
        self.root = Path(root_dir).resolve()
        self.writer = ArtifactWriter(self.root)
        self.registry = GeneratorRegistry(self.root)

    def run(self):
        print("⚡ Orchestrating System Framework Generation Sequence...")
        
        # Load system base declarations
        cfg_file = self.root / "config/settings.json"
        schema_data = json.loads(cfg_file.read_text()) if cfg_file.exists() else {}

        context = GenerationContext(schema_data, self.root)
        self.registry.discover()
        
        try:
            execution_order = self.registry.resolve_order()
            print(f"📊 Resolved Module Pipeline Dependency Graph: {' -> '.join(execution_order)}")
        except Exception as e:
            print(f"❌ Dependency resolution breakdown: {e}")
            return

        for name in execution_order:
            gen = self.registry.generators[name]
            print(f"⚙️ Running Engine Node: [{name}]")
            try:
                gen.generate(context, self.writer)
            except Exception as e:
                print(f"❌ Runtime crash on node layer [{name}]: {e}")
                return
                
        print("✅ Core Framework Lifecycle Complete. Manifest updated.")

if __name__ == "__main__":
    SovereignRuntimeEngine(Path(__file__).parent.parent).run()
