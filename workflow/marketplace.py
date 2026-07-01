import importlib, os

class Marketplace:
    @staticmethod
    def load_app(app_name):
        try:
            return importlib.import_module(f"apps.{app_name}")
        except ImportError:
            return None
