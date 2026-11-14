#!/usr/bin/env python3
"""Verifica que los enlaces oficiales de data/guia.json (y fuentes de plan.json) respondan 200.
Uso: python3 scripts/check_links.py   -> imprime código HTTP por enlace; sale con 1 si alguno falla.
Nota: cnsc.gov.co presenta una cadena de certificados incompleta para algunos clientes; se usa curl -k (solo lectura de documentos públicos).
"""
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
g = json.loads((ROOT / "data" / "guia.json").read_text())
urls = [(d["id"], d["url"]) for d in g["documentos"]]
urls += [("plan-src", u) for u in json.loads((ROOT / "data" / "plan.json").read_text())["meta"]["sources"]]
bad = 0
for i, u in urls:
    code = "000"
    for _ in range(3):
        r = subprocess.run(["curl", "-skL", "-A", "Mozilla/5.0", "--max-time", "90", "-o", "/dev/null", "-w", "%{http_code}", u], capture_output=True, text=True)
        code = r.stdout.strip() or "000"
        if code == "200": break
    print(f"{code}  {i:14s} {u}")
    bad += code != "200"
print("FALLAN:", bad); sys.exit(1 if bad else 0)
