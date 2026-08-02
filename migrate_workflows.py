from pathlib import Path

BASE = Path("products/education-os/web")
LEGACY = BASE / "director-dashboard/index.html"
MODULES = BASE / "workflows"

MODULES.mkdir(parents=True, exist_ok=True)

src = LEGACY.read_text()

def extract(start, end):
    a = src.find(start)
    b = src.find(end, a)
    return src[a:b] if a != -1 and b != -1 else ""

workflows = {
    "students.js": (
        '<section id="students"',
        '<section id="admissions"'
    ),
    "admissions.js": (
        '<section id="admissions"',
        '<section id="attendance"'
    ),
    "attendance.js": (
        '<section id="attendance"',
        '<section id="fees"'
    ),
    "fees.js": (
        '<section id="fees"',
        '<section id="parents-guardians"'
    ),
    "academic.js": (
        '<section id="academic-operations-workflow"',
        '<section id="reports-workflow"'
    )
}

for name,(start,end) in workflows.items():
    body = extract(start,end)
    if body:
        body = body.replace("`","\\`")
        (MODULES/name).write_text(
f"""export function loadWorkflow(root){{
    root.innerHTML = `{body}`;
}}
"""
        )
        print(name,"CREATED")
    else:
        print(name,"NOT FOUND")

print("DONE")
