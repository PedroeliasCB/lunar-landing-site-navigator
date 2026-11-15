#!/usr/bin/env python3
import sys, subprocess, os, json

# Ejecuta verificación rápida de sintaxis tras ediciones de la IA
def get_target():
    if len(sys.argv) > 1:
        return sys.argv[1]
    try:
        data = json.load(sys.stdin)  # Claude Code envía el evento como JSON
        return data.get("tool_input", {}).get("file_path", "")
    except Exception:
        return os.environ.get("CLAUDE_FILE_PATH", "")

def main():
    target = get_target()
    if target.endswith(".py") and os.path.exists(target):
        res = subprocess.run([sys.executable, "-m", "py_compile", target], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[SYNTAX ERROR] {target}:\n{res.stderr}", file=sys.stderr)
            sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
