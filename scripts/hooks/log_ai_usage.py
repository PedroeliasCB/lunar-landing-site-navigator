#!/usr/bin/env python3
import datetime
import os

# Registra automáticamente sesiones de trabajo asistidas por IA para el reporte final de NASA Space Apps
LOG_FILE = "AI_USAGE_LOG.md"

def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# Registro de Uso de IA — NASA Space Apps Challenge\n\n")
            f.write("| Timestamp | Agente / Herramienta | Actividad / Validación Humana |\n")
            f.write("| :--- | :--- | :--- |\n")
    agent = os.environ.get("AGENT_NAME", "AI Coding Agent")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"| {now} | {agent} | Sesión de desarrollo registrada automáticamente (completar detalle de validación) |\n")

if __name__ == "__main__":
    main()
