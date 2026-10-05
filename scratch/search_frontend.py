import os
import glob

print("--- Searching frontend source files for localhost / 8000 / fallback strings ---")
frontend_files = glob.glob('frontend/src/**/*', recursive=True)
for file_path in frontend_files:
    if os.path.isfile(file_path) and file_path.endswith(('.js', '.jsx', '.html', '.json', '.css')):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for term in ['localhost', '127.0.0.1', '8000', 'FastAPI']:
            if term in content:
                print(f'FOUND "{term}" in {file_path}')
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    if term in line:
                        print(f'  L{idx+1}: {line.strip()}')
