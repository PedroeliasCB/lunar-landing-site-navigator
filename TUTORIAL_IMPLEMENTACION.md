# Guía Rápida de Implementación Multi-Agente — NASA Space Apps Challenge

Descomprime este paquete directamente en la **raíz de tu repositorio Git** y sigue las instrucciones según la herramienta de IA que utilices:

---

## 1. Claude Code (Terminal / VS Code)
1. Copia las carpetas `.claude/` y `scripts/` en la raíz de tu proyecto.
2. Enlaza o copia las skills dentro de `.claude/skills/`:
   - En Linux/Mac: `ln -s ../.agents/skills .claude/skills`
   - En Windows (PowerShell): `Copy-Item -Recurse .agents/skills .claude/skills`
3. Inicia `claude` en la terminal. Los hooks (`PreToolUse`, `PostToolUse`, `Stop`) y las 4 skills se activarán automáticamente.

---

## 2. Google Antigravity (IDE y CLI)
1. Antigravity lee de forma nativa la carpeta `.agents/skills/` y el archivo `.agents/hooks.json`.
2. Asegúrate de tener `.agents/` y `scripts/` en la raíz de tu workspace.
3. Para conectar los servidores MCP (Context7 y Playwright), importa el contenido de `mcp_config.json` en `~/.gemini/antigravity/mcp_config.json` (o desde el panel *MCP Servers* en la UI).
4. Invoca cualquier skill en el chat escribiendo `/demo-first-ideation` o `/nasa-data-pipeline`.

---

## 3. Hermes Agent (Nous Research)
1. Copia las skills compatibles a tu directorio global de Hermes:
   ```bash
   cp -r .agents/skills/* ~/.hermes/skills/
   ```
2. Copia el hook de auditoría de NASA a Hermes:
   ```bash
   cp -r hermes_hooks/nasa_audit ~/.hermes/hooks/
   ```
3. Reinicia Hermes (`hermes gateway restart` o inicia nueva sesión). El hook registrará automáticamente en `AI_USAGE_LOG.md` cada vez que invoques una skill o cierres sesión.

---

## 4. DeepSeek (Web / API / Cline / Roo Code)
* **Si usas DeepSeek en Web (chat.deepseek.com):** Crea un nuevo chat y pega como primer mensaje el contenido completo de `AGENTS.md` + el `SKILL.md` que necesites en ese momento (ej. `nasa-data-pipeline/SKILL.md`).
* **Si usas DeepSeek R1/V3 vía API en VS Code (Cline / Roo Code):** Copia `AGENTS.md` como `.clinerules` o `.roorules` en la raíz del proyecto; el agente seguirá exactamente las mismas reglas de validación científica y manejo de datos NASA.

---

## 5. ChatGPT (Projects / Custom GPTs)
1. En ChatGPT, crea un **Proyecto** nuevo para tu equipo de NASA Space Apps.
2. En **Instrucciones del Proyecto**, pega el contenido de `AGENTS.md`.
3. En **Archivos del Proyecto**, sube los 4 archivos `SKILL.md` y `requirements-nasa.txt`. Así ChatGPT tendrá acceso permanente al protocolo científico y de ingesta de datos.

---

## 6. Gemini (Web / Gems / Gemini CLI)
* **En Gemini Web (Gems):** Crea un Gem llamado *NASA Space Apps Architect*, pega `AGENTS.md` en las instrucciones y adjunta los archivos `SKILL.md` como conocimiento base.
* **En Gemini CLI:** Copia `AGENTS.md` como `GEMINI.md` en la raíz de tu repositorio; Gemini CLI lo cargará automáticamente en cada sesión.
