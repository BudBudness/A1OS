import re

file_path = "~/A1OS/core/api.py"
with open(file_path, 'r') as f:
    content = f.read()

# Check if StaticFiles is already imported
if "StaticFiles" not in content:
    # Add import
    content = content.replace(
        "from fastapi import FastAPI", 
        "from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles"
    )
    
    # Add mount point before the main startup logic or at the end of app initialization
    if 'app.mount("/pos"' not in content:
        content += '\napp.mount("/pos", StaticFiles(directory="web/pos", html=True), name="pos")\n'

with open(file_path, 'w') as f:
    f.write(content)

print("✅ API patched to serve static POS files.")
