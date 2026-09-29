"""Aplica sobre el código de keiyoushi los PRs abiertos listados en parches.txt.

Uso: python aplicar_parches.py <parches.txt> <carpeta de extensions-source>

Un PR fusionado o cerrado se omite (upstream ya trae el cambio o lo descartó) y uno que ya no
aplica limpio solo avisa, para que una extensión no bloquee la compilación de las demás.
"""

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

UPSTREAM = "keiyoushi/extensions-source"

parches_file, source_dir = Path(sys.argv[1]), Path(sys.argv[2])
summary = Path(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull))


def fetch(url: str, accept: str) -> bytes:
    headers = {"Accept": accept, "User-Agent": "extensiones-manga"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
        return r.read()


lines = ["## Parches", ""]
for raw in parches_file.read_text(encoding="utf-8").splitlines():
    number = raw.split("#", 1)[0].strip()
    if not number:
        continue
    api = f"https://api.github.com/repos/{UPSTREAM}/pulls/{number}"
    pr = json.loads(fetch(api, "application/vnd.github+json"))
    if pr["merged"] or pr["state"] != "open":
        estado = "fusionado" if pr["merged"] else "cerrado"
        lines.append(f"- #{number} {estado} en upstream: omitido, se puede quitar de parches.txt")
        continue

    diff = fetch(api, "application/vnd.github.diff")
    check = subprocess.run(["git", "apply", "--check", "-"], input=diff, cwd=source_dir)
    if check.returncode != 0:
        lines.append(f"- ⚠️ #{number} ya no aplica limpio: se compila sin él ({pr['title']})")
        continue
    subprocess.run(["git", "apply", "-"], input=diff, cwd=source_dir, check=True)
    lines.append(f"- #{number} aplicado ({pr['head']['sha'][:7]}): {pr['title']}")

text = "\n".join(lines) + "\n"
print(text)
with summary.open("a", encoding="utf-8") as f:
    f.write(text)
