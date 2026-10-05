import glob
import os

files = glob.glob("frontend/dist/assets/*.js")
for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    print("FILE:", file_path)
    if "https://" in content or "http://" in content or "/api" in content:
        for chunk in content.split('"'):
            if "http" in chunk or "/api" in chunk:
                print("  FOUND:", chunk[:100])
