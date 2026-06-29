from generators.core.base_gen import BaseGenerator
from pathlib import Path

class DocsGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "docs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Automated API Blueprint and Docstring Extractor
        compiler_code = '''import inspect

class ApiBlueprintCompiler:
    def __init__(self):
        self.blueprints = {}

    def extract_blueprint(self, target_module):
        docstring = inspect.getdoc(target_module)
        module_name = getattr(target_module, "__name__", "unknown_module")
        self.blueprints[module_name] = docstring
        print(f"[DOCS-COMPILER] Extracted blueprint schema for module: {module_name}")
        return docstring
'''

        # 2. Structural Documentation Renderer
        renderer_code = '''class DocumentationRenderer:
    @staticmethod
    def render_markdown(module_name, docstring):
        return f"# Module: {module_name}\\n\\n## Overview\\n{docstring}\\n"
'''

        # 3. Documentation Completeness Linter
        validator_code = '''class DocumentationValidator:
    def __init__(self, min_chars=10):
        self.min_chars = min_chars

    def assert_documented(self, docstring):
        if not docstring or len(docstring) < self.min_chars:
            return False, "insufficient_documentation_blueprint"
        return True, "documentation_standards_met"
'''

        # 4. Documentation Compiler Verification Test Suite
        test_code = '''from .compiler import ApiBlueprintCompiler
from .renderer import DocumentationRenderer
from .validator import DocumentationValidator

# Mock a target module for blueprint extraction testing
import sys
mock_module = sys.modules[__name__]
mock_module.__doc__ = "A1OS Sovereign Core Runtime Documentation Blueprint."

def test_docs_subsystem():
    compiler = ApiBlueprintCompiler()
    renderer = DocumentationRenderer()
    validator = DocumentationValidator(min_chars=15)
    
    # 1. Blueprint extraction assertion
    doc = compiler.extract_blueprint(mock_module)
    assert doc == "A1OS Sovereign Core Runtime Documentation Blueprint."
    
    # 2. Markdown rendering check
    markdown = renderer.render_markdown("mock_module", doc)
    assert "# Module: mock_module" in markdown
    
    # 3. Documentation quality linter check
    is_compliant, reason = validator.assert_documented(doc)
    assert is_compliant is True
    assert reason == "documentation_standards_met"
    
    print("✅ Automated Internal API Documentation Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_docs_subsystem()
'''

        # Write out the full structural docs modules atomically
        with open(output_dir / "compiler.py", "w") as f: f.write(compiler_code.strip())
        with open(output_dir / "renderer.py", "w") as f: f.write(renderer_code.strip())
        with open(output_dir / "validator.py", "w") as f: f.write(validator_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] docs_gen.py has compiled v1 Docs Subsystem inside {output_dir}")
