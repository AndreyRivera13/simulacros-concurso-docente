#!/usr/bin/env python3
"""Prepara (y opcionalmente genera con un LLM) el borrador del siguiente día pendiente.

Uso:
  python3 scripts/next_day.py                 # muestra, por versión, el próximo día del plan sin JSON
  python3 scripts/next_day.py A 2026-11-22    # escribe drafts/A/2026-11-22.prompt.md con el encargo de generación
  python3 scripts/next_day.py A 2026-11-22 --llm
      # además llama a una API compatible con OpenAI (Chat Completions) y guarda drafts/A/2026-11-22.txt
      # Variables: LLM_API_KEY (obligatoria), LLM_BASE_URL (p. ej. https://api.x.ai/v1), LLM_MODEL
"""
import json, os, sys, pathlib, urllib.request, datetime as dt

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "data/plan.json").read_text())
N = PLAN["meta"]["questions_per_topic"]

def pending(v):
    have = {p.stem for p in (ROOT / "data" / v).glob("*.json")}
    return [d for d in PLAN["versions"][v]["days"] if d["date"] not in have]

def brief(v, date):
    vp = PLAN["versions"][v]; day = next(d for d in vp["days"] if d["date"] == date)
    done = [t["title"] for d in vp["days"] if d["date"] < date for t in d["topics"]]
    recent_q = []
    for p in sorted((ROOT / "data" / v).glob("*.json"))[-7:]:
        for t in json.loads(p.read_text())["topics"]:
            recent_q += [q["q"].split("\n")[0][:90] for q in t["questions"]]
    topics = "\n".join(f"## {t['id']}\n- Título: {t['title']}\n- Eje: {t['track']}\n- Enfoque: {t['focus']}" for t in day["topics"])
    return f"""Eres un experto en el concurso docente de Colombia (CNSC) y en {vp['name']}.
Genera el simulacro del día {day['n']} ({date}) para la versión {v} ({vp['name']}, aspirante: {vp['person']}).
Dificultad: {day['difficulty']}. Tipo de día: {day['kind']}.

TEMAS (usa EXACTAMENTE estos encabezados "## <id>" y en este orden):
{topics}

REGLAS
1. Exactamente {N} preguntas por tema, en español, originales, al estilo de la prueba de aptitudes y competencias básicas
   (casos de aula o situaciones, no solo memoria; ~40 % memoria/conceptos, ~60 % aplicación/análisis).
2. Única respuesta con 3 opciones. La opción correcta se escribe PRIMERO con "+ " y los dos distractores con "- ".
   (El script baraja las opciones; NO menciones letras A/B/C en enunciados ni explicaciones.)
3. Distractores plausibles (errores conceptuales frecuentes), de longitud similar a la correcta.
4. Cada pregunta lleva "E: " con explicación breve (1-3 frases): por qué la correcta y por qué fallan los distractores.
5. Exactitud normativa: cita norma y artículo solo si estás seguro. Nada de datos inventados. Cifras verificables.
6. Si hay código o pseudocódigo, escribe el enunciado en la línea "Q:" y el código en las líneas siguientes con su sangría.
7. No repitas preguntas ya usadas (lista abajo). En días de repaso, usa casos NUEVOS e integradores.

FORMATO (texto plano, sin Markdown adicional):
## <id-del-tema>
Q: enunciado
+ opción correcta
- distractor 1
- distractor 2
E: explicación

(línea en blanco entre preguntas)

Temas ya estudiados en el plan: {'; '.join(done[-40:]) or 'ninguno'}
Enunciados recientes que NO debes repetir:
""" + "\n".join("- " + q for q in recent_q[-200:]) + "\n"

def call_llm(prompt):
    key = os.environ["LLM_API_KEY"]; base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    body = {"model": os.environ.get("LLM_MODEL", "gpt-4o"), "temperature": 0.6,
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        for v in PLAN["versions"]:
            p = pending(v); print(v, p[0]["date"] if p else "plan completo")
        sys.exit()
    v, date = a[0], a[1]
    pr = brief(v, date)
    (ROOT / "drafts" / v / f"{date}.prompt.md").write_text(pr, encoding="utf-8")
    print("Encargo:", f"drafts/{v}/{date}.prompt.md")
    if "--llm" in a:
        txt = call_llm(pr).strip().strip("`")
        (ROOT / "drafts" / v / f"{date}.txt").write_text(txt + "\n", encoding="utf-8")
        print("Borrador:", f"drafts/{v}/{date}.txt  → ahora: python3 scripts/build_day.py {v} {date}")
