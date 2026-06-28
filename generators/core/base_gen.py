import os

class BaseGenerator:
    def __init__(self, context):
        self.context = context
        self.name = "base"
        self.dependencies = []

    def emit_file(self, module_dir, file_name, content_string):
        target_dir = os.path.join(self.context["root"], "build/src", module_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        init_file = os.path.join(target_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Generated Package Initialize Frame\n")
        
        filepath = os.path.join(target_dir, file_name)
        with open(filepath, "w") as f:
            f.write(content_string.strip() + "\n")
            
        return os.path.relpath(filepath, self.context["root"])

    def generate(self):
        raise NotImplementedError("Generation routine frames must override base execution structures.")
