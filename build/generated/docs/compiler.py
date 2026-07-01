import inspect

class ApiBlueprintCompiler:
    def __init__(self):
        self.blueprints = {}

    def extract_blueprint(self, target_module):
        docstring = inspect.getdoc(target_module)
        module_name = getattr(target_module, "__name__", "unknown_module")
        self.blueprints[module_name] = docstring
        print(f"[DOCS-COMPILER] Extracted blueprint schema for module: {module_name}")
        return docstring