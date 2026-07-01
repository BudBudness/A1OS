class DocumentationValidator:
    def __init__(self, min_chars=10):
        self.min_chars = min_chars

    def assert_documented(self, docstring):
        if not docstring or len(docstring) < self.min_chars:
            return False, "insufficient_documentation_blueprint"
        return True, "documentation_standards_met"