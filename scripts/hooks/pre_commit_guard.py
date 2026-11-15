#!/usr/bin/env python3
import sys, subprocess, re

# Bloquea commits con API keys o archivos pesados (>10MB)
MAX_BYTES = 10 * 1024 * 1024
SECRET_PATTERNS = [
    r"NASA_API_KEY\s*=\s*['\"][A-Za-z0-9]{20,}['\"]",
    r"EARTHDATA_TOKEN\s*=\s*['\"][A-Za-z0-9\._\-]{20,}['\"]",
    r"sk-[A-Za-z0-9]{32,}",
    r"ghp_[A-Za-z0-9]{36}"
]

def main():
    try:
        staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True, stderr=subprocess.DEVNULL).splitlines()
    except Exception:
        sys.exit(0)
    for filepath in staged:
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            if len(data) > MAX_BYTES:
                print(f"[BLOCKED] {filepath} supera 10MB. Usa .gitignore o filtra el dataset.", file=sys.stderr)
                sys.exit(2)
            text = data.decode("utf-8", errors="ignore")
            for pat in SECRET_PATTERNS:
                if re.search(pat, text):
                    print(f"[BLOCKED] Secreto/API Key detectado en {filepath}. Muévelo a .env", file=sys.stderr)
                    sys.exit(2)
        except FileNotFoundError:
            continue
    sys.exit(0)

if __name__ == "__main__":
    main()
