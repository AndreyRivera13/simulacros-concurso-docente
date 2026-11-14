#!/usr/bin/env python3
"""Prueba E2E con Playwright (Chromium headless) contra una URL (local o pública).

Uso: python tests/e2e.py https://usuario.github.io/simulacros-concurso-docente/ [YYYY-MM-DD]
Sin fecha, abre la vista por defecto (simulacro de "hoy" según America/Bogota).
Para cada versión (A y B): responde TODAS las preguntas del día mezclando correctas e incorrectas,
verifica selección, retroalimentación inmediata (correcto/incorrecto + explicación), bloqueo de la pregunta,
puntaje por tema y total; guarda captura test-<V>.png de la pantalla de resultado final.
"""
import sys, json, re, pathlib
from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip("/") + "/"
DATE = sys.argv[2] if len(sys.argv) > 2 else None
OUT = pathlib.Path(__file__).resolve().parent.parent

def run_version(browser, v):
    errs, checks = [], 0
    ctx = browser.new_context(viewport={"width": 1100, "height": 900}, locale="es-CO", timezone_id="America/Bogota")
    page = ctx.new_page()
    console_errors = []
    page.on("pageerror", lambda e: console_errors.append(str(e)))
    url = BASE + f"?v={v}" + (f"&d={DATE}" if DATE else "") + "#quiz"
    page.goto(url, wait_until="networkidle")
    page.wait_for_selector(".q .option")
    date = re.search(r"[?&]d=(\d{4}-\d{2}-\d{2})", page.url).group(1)
    data = json.loads(page.request.get(BASE + f"data/{v}/{date}.json").text())
    exp_topic, exp_total, n_total = [], 0, 0
    gi = 0
    for ti, t in enumerate(data["topics"]):
        ok_t = 0
        for qi, q in enumerate(t["questions"]):
            want_correct = (gi % 3 != 0)  # 2 de cada 3 correctas; 1 de cada 3 incorrecta
            choice = q["answer"] if want_correct else (q["answer"] + 1) % len(q["options"])
            card = page.locator(f'[data-q="{ti}-{qi}"]')
            fb = card.locator(".feedback")
            if fb.is_visible(): errs.append(f"{ti}-{qi}: feedback visible antes de responder")
            card.locator(f'.option[data-opt="{choice}"]').click()
            checks += 1
            # retroalimentación inmediata
            fb.wait_for(state="visible", timeout=2000)
            txt = fb.inner_text()
            if want_correct and "Correcto" not in txt: errs.append(f"{ti}-{qi}: falta 'Correcto'")
            if not want_correct and "Incorrecto" not in txt: errs.append(f"{ti}-{qi}: falta 'Incorrecto'")
            if q["explanation"][:40] not in txt: errs.append(f"{ti}-{qi}: falta explicación")
            # marcado de opciones
            if "correct" not in (card.locator(f'.option[data-opt="{q["answer"]}"]').get_attribute("class") or ""): errs.append(f"{ti}-{qi}: no marca la correcta")
            if not want_correct and "incorrect" not in (card.locator(f'.option[data-opt="{choice}"]').get_attribute("class") or ""): errs.append(f"{ti}-{qi}: no marca la elegida incorrecta")
            # bloqueo
            disabled = card.locator(".option:disabled").count()
            if disabled != len(q["options"]): errs.append(f"{ti}-{qi}: opciones no bloqueadas ({disabled})")
            other = (choice + 1) % len(q["options"])
            card.locator(f'.option[data-opt="{other}"]').click(force=True)
            if card.get_attribute("data-result") != ("correct" if want_correct else "incorrect"): errs.append(f"{ti}-{qi}: la respuesta cambió tras bloquear")
            ok_t += want_correct; gi += 1; n_total += 1
        exp_topic.append((ok_t, len(t["questions"])))
        exp_total += ok_t
        ts = page.locator(f'[data-topic-score="{ti}"]').inner_text()
        if f"{len(t['questions'])}/{len(t['questions'])} respondidas · {ok_t} correctas" not in ts: errs.append(f"tema {ti}: marcador '{ts}'")
    res = page.locator("#results"); res.wait_for(state="visible", timeout=3000)
    total_txt = page.locator("#total-score").inner_text().strip()
    if total_txt != f"{exp_total} / {n_total}": errs.append(f"total mostrado '{total_txt}' != esperado '{exp_total} / {n_total}'")
    for ti, (ok_t, n) in enumerate(exp_topic):
        rt = page.locator(f'[data-result-topic="{ti}"] .rt-score').inner_text().strip()
        if rt != f"{ok_t} / {n}": errs.append(f"resultado tema {ti}: '{rt}' != '{ok_t} / {n}'")
    sb = page.locator("#scorebar").inner_text()
    if f"{n_total}/{n_total}" not in sb or f"Correctas {exp_total}" not in sb: errs.append(f"barra de puntaje: '{sb}'")
    res.scroll_into_view_if_needed(); page.wait_for_timeout(300)
    shot = OUT / f"test-{v}.png"
    page.screenshot(path=str(shot))
    # persistencia: recargar conserva respuestas y resultado
    page.reload(wait_until="networkidle"); page.wait_for_selector("#results:not([hidden])", timeout=4000)
    if page.locator("#total-score").inner_text().strip() != f"{exp_total} / {n_total}": errs.append("tras recargar no se conserva el puntaje")
    # plan de estudio
    page.goto(BASE + f"?v={v}#plan", wait_until="networkidle"); page.wait_for_selector(".plan table")
    rows = page.locator(".plan tbody tr").count()
    today_rows = page.locator(".plan tr.today").count()
    banner = "El plan inicia mañana" in page.locator(".planinfo").inner_text()
    if rows < 70: errs.append(f"plan con pocas filas ({rows})")
    if not (today_rows == 1 or banner): errs.append("plan sin día de hoy resaltado")
    page.screenshot(path=str(OUT / f"test-{v}-plan.png"))
    if console_errors: errs.append("errores JS: " + "; ".join(console_errors))
    ctx.close()
    return {"version": v, "date": date, "questions": n_total, "expected_correct": exp_total, "shown": total_txt,
            "per_topic": [f"{a}/{b}" for a, b in exp_topic], "plan_rows": rows, "today_highlight": today_rows == 1, "start_banner": banner,
            "checks": checks, "errors": errs, "pass": not errs, "screenshot": str(shot)}

def check_today(browser, v, fake="2026-11-17"):
    """Con el reloj fijado en una fecha del plan, el plan resalta ese día y el simulacro por defecto es el de ese día."""
    import datetime as dt
    ctx = browser.new_context(timezone_id="America/Bogota"); page = ctx.new_page()
    page.clock.set_fixed_time(dt.datetime.fromisoformat(fake + "T12:00:00-05:00"))
    page.goto(BASE + f"?v={v}#plan", wait_until="networkidle"); page.wait_for_selector(".plan table")
    hl = page.locator(".plan tr.today").get_attribute("data-date") if page.locator(".plan tr.today").count() else None
    page.goto(BASE + f"?v={v}#quiz", wait_until="networkidle"); page.wait_for_selector(".q .option")
    d = re.search(r"[?&]d=(\d{4}-\d{2}-\d{2})", page.url).group(1)
    ctx.close()
    return {"fake_today": fake, "highlighted": hl, "default_quiz": d, "pass": hl == fake and d == fake}

with sync_playwright() as p:
    b = p.chromium.launch()
    results = [run_version(b, v) for v in ("A", "B")]
    for r in results:
        t = check_today(b, r["version"]); r["today_check"] = t
        if not t["pass"]: r["errors"].append(f"resaltado de hoy: {t}"); r["pass"] = False
    b.close()
print(json.dumps(results, ensure_ascii=False, indent=1))
sys.exit(0 if all(r["pass"] for r in results) else 1)
