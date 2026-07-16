import re

with open('/data/data/com.termux/files/home/A1OS/core/api.py', 'r') as f:
    content = f.read()

# Fix the broken import line
content = content.replace(
    "from fastapi.staticfiles import StaticFiles, HTTPException, Request",
    "from fastapi import HTTPException, Request\nfrom fastapi.staticfiles import StaticFiles"
)

# Ensure mount is present only once
if 'app.mount("/pos"' not in content:
    content += '\napp.mount("/pos", StaticFiles(directory="web/pos", html=True), name="pos")\n'

with open('/data/data/com.termux/files/home/A1OS/core/api.py', 'w') as f:
    f.write(content)

print("✅ API imports fixed.")
