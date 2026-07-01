from .compiler import ApiBlueprintCompiler
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