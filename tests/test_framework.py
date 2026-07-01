from organization.departments.base_department import BaseDepartment
from sdk.worker_sdk import WorkerSDK

# 1. Setup Department
eng_dept = BaseDepartment("Engineering", "Eddie Billions")

# 2. Setup Worker
dev_ai = WorkerSDK("DevBot_01", "Junior Engineer", "Engineering")
eng_dept.register_worker(dev_ai)

# 3. Perform a task
def cloudflare_check():
    return "Cloudflare API Connection: OK"

result = dev_ai.perform_task("Health Check", cloudflare_check)

print(f"Department: {eng_dept.name}")
print(f"Worker: {dev_ai.name} | Status: {dev_ai.get_status()['status']}")
print(f"Task Result: {result}")
