import importlib

def route_task(task):
    dept = task.get("department")
    if dept == "SYSTEM": return True
    
    # Try dynamic routing for new departments: OPS, DEV, MAINTENANCE
    try:
        module_path = f"company.workers.{dept.lower()}_worker"
        module = importlib.import_module(module_path)
        worker_class = getattr(module, f"{dept.capitalize()}Worker")
        return worker_class().execute(task)
    except (ImportError, AttributeError) as e:
        print(f"Routing Error: Worker for {dept} not found. {e}")
        return False
    except Exception as e:
        print(f"Execution Error: {e}")
        return False
