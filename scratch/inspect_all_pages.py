import os
import glob

print("--- Deep Inspecting all Frontend files ---")
files = glob.glob('frontend/src/**/*', recursive=True)
for f in files:
    if os.path.isfile(f) and f.endswith(('.js', '.jsx')):
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            text = fp.read()
        for kw in ['localhost', '127.0.0.1', '8000', 'http://', 'https://', 'API_BASE_URL']:
            if kw in text:
                print(f"File: {f} -> matched '{kw}'")
                for i, line in enumerate(text.splitlines()):
                    if kw in line:
                        print(f"  L{i+1}: {line.strip()}")
