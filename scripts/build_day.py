#!/usr/bin/env python3
"""Convierte un borrador de día (drafts/<V>/<YYYY-MM-DD>.txt) en data/<V>/<YYYY-MM-DD>.json,
lo valida contra data/plan.json, baraja las opciones (semilla fija) y actualiza data/index.json.

Uso:
  python3 scripts/build_day.py A 2026-11-15      # un día
  python3 scripts/build_day.py --all             # todos los borradores existentes
  python3 scripts/build_day.py --index           # solo regenerar data/index.json

Formato del borrador (texto plano, UTF-8):
  ## <topic-id tal cual aparece en plan.json>
  Q: enunciado (puede ocupar varias líneas; también se admite "C:" para un contexto/caso previo)
  + opción CORRECTA (siempre exactamente una, con '+')
  - distractor
  - distractor
  E: explicación (por qué la correcta lo es y por qué fallan los distractores)
  (línea en blanco entre preguntas)
Reglas que valida: exactamente N preguntas por tema (plan.meta.questions_per_topic), 3 opciones distintas,
1 correcta, explicación no vacía, sin preguntas repetidas en el día.
"""
import json, sys, random, pathlib, hashlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "data/plan.json").read_text())

def parse(text):
    topics, cur, q = [], None, None
    def flush():
        nonlocal q
        if q: cur["questions"].append(q); q = None
    last = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            flush(); cur = {"id": line[3:].strip(), "questions": []}; topics.append(cur); last = None; continue
        if not line.strip():
            last = None if last != "q" else last; continue
        tag, _, rest = line.partition(" ")
        if line.startswith("C:"):
            flush(); q = {"c": line[2:].strip(), "q": "", "o": [], "ok": None, "e": ""}; last = "c"
        elif line.startswith("Q:"):
            if q is None or q["q"] or q["o"]:
                flush(); q = {"c": "", "q": "", "o": [], "ok": None, "e": ""}
            q["q"] = line[2:].strip(); last = "q"
        elif tag in ("+", "-") and q is not None:
            if tag == "+": q["ok"] = len(q["o"])
            q["o"].append(rest.strip()); last = "o"
        elif line.startswith("E:") and q is not None:
            q["e"] = line[2:].strip(); last = "e"
        else:  # continuación
            if q is None: raise SystemExit(f"Línea huérfana: {line!r}")
            key = {"c": "c", "q": "q", "e": "e"}.get(last)
            if key is None: raise SystemExit(f"Continuación inesperada: {line!r}")
            q[key] += "\n" + line.rstrip()  # se conserva la sangría (útil para código)
    flush()
    return topics

def build(v, date):
    days = {d["date"]: d for d in PLAN["versions"][v]["days"]}
    if date not in days: raise SystemExit(f"{date} no está en el plan de {v}")
    day = days[date]; N = PLAN["meta"]["questions_per_topic"]
    src = ROOT / "drafts" / v / f"{date}.txt"
    topics = parse(src.read_text(encoding="utf-8"))
    plan_ids = [t["id"] for t in day["topics"]]
    got_ids = [t["id"] for t in topics]
    if got_ids != plan_ids: raise SystemExit(f"{v} {date}: temas {got_ids} != plan {plan_ids}")
    out_topics, seen = [], set()
    for pt, t in zip(day["topics"], topics):
        qs = t["questions"]
        if len(qs) != N: raise SystemExit(f"{v} {date} {t['id']}: {len(qs)} preguntas (se esperan {N})")
        out_q = []
        trng = random.Random(int(hashlib.sha1(f"{v}|{date}|{t['id']}".encode()).hexdigest(), 16))
        slots = ([0, 1, 2] * ((len(qs) + 2) // 3))[:len(qs)]; trng.shuffle(slots)  # posiciones balanceadas
        for i, q in enumerate(qs):
            where = f"{v} {date} {t['id']} #{i+1}"
            if not q["q"] or not q["e"]: raise SystemExit(f"{where}: falta enunciado o explicación")
            if len(q["o"]) != 3 or len(set(q["o"])) != 3: raise SystemExit(f"{where}: se requieren 3 opciones distintas")
            if q["ok"] is None: raise SystemExit(f"{where}: falta la opción correcta (+)")
            key = re.sub(r"\W+", "", q["q"].lower())
            if key in seen: raise SystemExit(f"{where}: pregunta repetida")
            seen.add(key)
            rng = random.Random(int(hashlib.sha1(f"{v}|{date}|{t['id']}|{i}".encode()).hexdigest(), 16))
            wrong = [k for k in range(3) if k != q["ok"]]; rng.shuffle(wrong)
            order = wrong[:]; order.insert(slots[i], q["ok"])
            opts = [q["o"][k] for k in order]; ans = slots[i]
            item = {"q": q["q"], "options": opts, "answer": ans, "explanation": q["e"]}
            if q["c"]: item["context"] = q["c"]
            out_q.append(item)
        out_topics.append({"id": pt["id"], "title": pt["title"], "track": pt["track"], "questions": out_q})
    out = {"version": v, "date": date, "n": day["n"], "kind": day["kind"], "difficulty": day["difficulty"], "topics": out_topics}
    dst = ROOT / "data" / v / f"{date}.json"; dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    dist = [0, 0, 0]
    for t in out_topics:
        for q in t["questions"]: dist[q["answer"]] += 1
    print(f"OK {dst.relative_to(ROOT)}: {len(out_topics)} temas x {N} preguntas; respuestas A/B/C = {dist}")

def index():
    idx = {v: sorted(p.stem for p in (ROOT / "data" / v).glob("*.json")) for v in PLAN["versions"]}
    (ROOT / "data/index.json").write_text(json.dumps(idx, indent=1))
    print("index.json:", {k: len(x) for k, x in idx.items()})

if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--index"]: pass
    elif a == ["--all"]:
        for v in PLAN["versions"]:
            for f in sorted((ROOT / "drafts" / v).glob("*.txt")): build(v, f.stem)
    elif len(a) == 2: build(a[0], a[1])
    else: raise SystemExit(__doc__)
    index()
