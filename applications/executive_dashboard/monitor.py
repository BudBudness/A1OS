import os, json

def get_org_status():
    pending = len(os.listdir("/data/data/com.termux/files/home/A1OS/data/tasks/pending/"))
    archive = len(os.listdir("/data/data/com.termux/files/home/A1OS/data/tasks/archive/"))
    return {"pending_tasks": pending, "archived_tasks": archive}

if __name__ == "__main__":
    print(json.dumps(get_org_status(), indent=2))
