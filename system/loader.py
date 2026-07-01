import os
import importlib.util
import inspect
from organization.departments.base_department import BaseDepartment

class PluginLoader:
    @staticmethod
    def load_plugins(directory):
        print(f"--- Marketplace: Scanning {directory} ---")
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(directory, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Scan module for subclasses of BaseDepartment
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseDepartment) and obj is not BaseDepartment:
                        # Instantiate and register automatically
                        instance = obj()
                        print(f"Marketplace: Registered {instance.name} from {filename}")
