class DocumentationRenderer:
    @staticmethod
    def render_markdown(module_name, docstring):
        return f"# Module: {module_name}\n\n## Overview\n{docstring}\n"