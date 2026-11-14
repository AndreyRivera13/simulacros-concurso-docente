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
SB_URL = "https://ggcgbjonlxxcmegknfxi.supabase.co/rest/v1/quiz_attempts"
SB_KEY = "sb_publishable_TY2maiftFyPDWj_SovDXCQ_7kUE5Lbq"   # clave pública (la misma del sitio)
TEST_IDS = []   # intentos creados por la prueba; se borran después vía SQL (MCP/consola de Supabase)

def sb_get(page, attempt_id):
    r = page.request.get(f"{SB_URL}?id=eq.{attempt_id}&select=id,quiz_date,version,person,topic_scores,answered,total_correct,total_questions,percentage,completed",
                         headers={"apikey": SB_KEY})
    return r.json()

def check_cloud(page, v, date, exp_total, n_total, exp_topic, errs):
    """Guardado en Supabase al completar + lectura de vuelta."""
    page.wait_for_selector('#results .save-status[data-state="ok"]', timeout=20000)
    aid = page.locator("#results").get_attribute("data-attempt-id")
    TEST_IDS.append(aid)
    rows = sb_get(page, aid)
    out = {"attempt_id": aid, "rows": len(rows)}
    if len(rows) != 1: errs.append(f"Supabase: {len(rows)} filas para el intento {aid}"); return out
    r = rows[0]
    exp = {"quiz_date": date, "version": v, "person": {"A": "Yazmín", "B": "Andrey"}[v], "answered": n_total, "total_correct": exp_total, "total_questions": n_total, "completed": True}
    for k, val in exp.items():
        if r[k] != val: errs.append(f"Supabase {k}: {r[k]!r} != {val!r}")
    if abs(float(r["percentage"]) - round(exp_total * 100 / n_total, 2)) > 0.01: errs.append(f"Supabase percentage {r['percentage']}")
    got = [(t["correct"], t["total"]) for t in r["topic_scores"]]
    if got != list(exp_topic): errs.append(f"Supabase topic_scores {got} != {exp_topic}")
    out.update({"readback": {k: r[k] for k in ("total_correct", "total_questions", "percentage", "completed")}, "topic_scores": got})
    return out

def check_offline_partial(browser, v, date):
    """Sin conexión: guarda local y queda pendiente; al volver la conexión se sube como intento PARCIAL (misma fila)."""
    errs = []
    ctx = browser.new_context(timezone_id="America/Bogota"); page = ctx.new_page()
    page.goto(BASE + f"?v={v}&d={date}#quiz", wait_until="networkidle"); page.wait_for_selector(".q .option")
    ctx.set_offline(True)
    page.locator('[data-q="0-0"] .option').first.click()
    page.locator('[data-q="0-1"] .option').first.click()
    page.wait_for_selector('#scorebar .save-status[data-state="pending"]', timeout=10000)
    att = page.evaluate(f"JSON.parse(localStorage.getItem('scd.att.{v}.{date}'))")
    if not att or not att.get("dirty"): errs.append("offline: no quedó pendiente en localStorage")
    ctx.set_offline(False)
    ok = page.evaluate("window.__scdSync()")
    page.wait_for_selector('#scorebar .save-status[data-state="ok"]', timeout=15000)
    TEST_IDS.append(att["id"])
    rows = sb_get(page, att["id"])
    if len(rows) != 1 or rows[0]["answered"] != 2 or rows[0]["completed"]: errs.append(f"offline->online: fila {rows}")
    # un tercer answer actualiza la MISMA fila (guardado parcial)
    page.locator('[data-q="0-2"] .option').first.click()
    page.wait_for_function(f"(() => {{ const a = JSON.parse(localStorage.getItem('scd.att.{v}.{date}')); return a && !a.dirty && a.rev >= 3; }})()", timeout=15000)
    rows = sb_get(page, att["id"])
    if len(rows) != 1 or rows[0]["answered"] != 3: errs.append(f"guardado parcial no actualizó la fila: {rows}")
    ctx.close()
    return {"attempt_id": att["id"], "synced": ok, "answered_after": rows[0]["answered"] if rows else None, "errors": errs, "pass": not errs}

def check_progress(browser, ids_by_v):
    errs = []
    ctx = browser.new_context(viewport={"width": 1100, "height": 1000}, timezone_id="America/Bogota"); page = ctx.new_page()
    page.goto(BASE + "#progreso", wait_until="networkidle")
    page.wait_for_selector('#progreso[data-loaded="cloud"]', timeout=20000)
    if page.locator('nav.views a[href="#progreso"]').count() != 1: errs.append("falta pestaña Progreso")
    for v, (aid, tot) in ids_by_v.items():
        row = page.locator(f'#prog-table tr[data-attempt="{aid}"]')
        if row.count() != 1: errs.append(f"progreso: no aparece el intento {v} {aid}"); continue
        if row.locator(".tot").inner_text().strip() != tot: errs.append(f"progreso: total {v} {row.locator('.tot').inner_text()} != {tot}")
    if page.locator("#trend circle").count() < 2: errs.append("progreso: gráfica sin puntos")
    if page.locator("#avg-A").inner_text() == "—" or page.locator("#avg-B").inner_text() == "—": errs.append("progreso: promedio vacío")
    page.screenshot(path=str(OUT / "test-progreso.png"), full_page=True)
    page.locator('.fbtn[data-filter="B"]').click(); page.wait_for_selector('.fbtn.on[data-filter="B"]')
    if page.locator('#prog-table tr[data-version="A"]').count() != 0: errs.append("filtro B muestra filas de A")
    if page.locator('#prog-table tr[data-version="B"]').count() < 1: errs.append("filtro B sin filas")
    ctx.close()
    return {"errors": errs, "pass": not errs}

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
    cloud = check_cloud(page, v, date, exp_total, n_total, exp_topic, errs)
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
    gres = check_guide(page, v, date, errs)
    if console_errors: errs.append("errores JS: " + "; ".join(console_errors))
    ctx.close()
    return {"version": v, "date": date, "questions": n_total, "expected_correct": exp_total, "shown": total_txt,
            "per_topic": [f"{a}/{b}" for a, b in exp_topic], "plan_rows": rows, "today_highlight": today_rows == 1, "start_banner": banner,
            "checks": checks, "cloud": cloud, "guide": gres, "errors": errs, "pass": not errs, "screenshot": str(shot)}

OFFICIAL = ("cnsc.gov.co", "mineducacion.gov.co", "funcionpublica.gov.co", "colombiaaprende.edu.co", "minambiente.gov.co", "secretariasenado.gov.co")

def check_guide(page, v, date, errs):
    """Guía de estudio: enlace desde el inicio y desde el simulacro, contenido oficial y cruce con el plan."""
    g = json.loads(page.request.get(BASE + "data/guia.json").text())
    plan = json.loads(page.request.get(BASE + "data/plan.json").text())
    out = {}
    # 1) enlace en la navegación del inicio
    page.goto(BASE + f"?v={v}&d={date}#quiz", wait_until="networkidle"); page.wait_for_selector(".q .option")
    if page.locator('nav.views a[href="#guia"]').count() != 1: errs.append("falta pestaña 'Guía de estudio' en el inicio")
    # 2) enlaces por tema en el encabezado del simulacro
    pd = next(d for d in plan["versions"][v]["days"] if d["date"] == date)
    links = page.locator("#day-guide-links a")
    out["day_links"] = [links.nth(i).inner_text() for i in range(links.count())]
    if links.count() != len(pd["topics"]): errs.append(f"encabezado: {links.count()} enlaces a la guía, esperados {len(pd['topics'])}")
    if page.locator(".topic .track a.glink").count() != len(pd["topics"]): errs.append("faltan enlaces a la guía en los temas")
    first = next((t for t in pd["topics"] if t.get("eje") and t["eje"] != "repaso"), None)
    if first:
        b = re.sub(r"-v\d+$", "", first["id"])
        page.locator(f'#day-guide-links a[data-topic="{b}"]').first.click()
        page.wait_for_selector("#tema-body h4")
        if not page.url.endswith(f"#guia-t-{b}"): errs.append(f"enlace del tema no lleva a #guia-t-{b} ({page.url})")
        body = page.locator("#tema-body").inner_text()
        for k in ("Puntos clave", "Trampas frecuentes"):
            if k not in body: errs.append(f"la página del tema {b} no tiene '{k}'")
        if len(body) < 800: errs.append(f"contenido del tema {b} demasiado corto ({len(body)})")
        if page.locator("#tema-refs a").count() == 0: errs.append(f"tema {b} sin fuentes oficiales")
        out["topic_link_target"] = f"#guia-t-{b}"; out["topic_chars"] = len(body)
        page.screenshot(path=str(OUT / f"test-{v}-tema.png"), full_page=False)
        if page.locator("#tema-next").count():
            page.locator("#tema-next").click(); page.wait_for_function(f"document.querySelector('#tema') && document.querySelector('#tema').dataset.topic !== '{b}'")
        page.locator("#tema-index").click(); page.wait_for_selector("#sec-ejes")
    # todos los temas del plan tienen contenido de estudio (verificado sobre los datos publicados)
    tm = json.loads(page.request.get(BASE + "data/temas.json").text())
    bases = {re.sub(r"-v\d+$", "", t["id"]) for d in plan["versions"][v]["days"] for t in d["topics"] if t.get("eje") not in (None, "repaso")}
    sin = [b2 for b2 in bases if b2 not in tm["map"] or "Puntos clave" not in tm["content"][tm["map"][b2]]["html"]]
    if sin: errs.append(f"temas sin contenido de estudio: {sin}")
    out["temas_con_contenido"] = len(bases) - len(sin)
    # 3) contenido de la guía
    page.goto(BASE + f"?v={v}#guia", wait_until="networkidle"); page.wait_for_selector(".guia")
    if "NO ha publicado" not in page.locator("#estado-ejes").inner_text(): errs.append("la guía no aclara el estado de los ejes 2026-2027")
    rows = page.locator("#tabla-pruebas tbody tr"); txt = page.locator("#tabla-pruebas").inner_text()
    if rows.count() != 4 or "55 %" not in txt or "60/100" not in txt or "30 %" not in txt: errs.append("tabla de pruebas incompleta")
    ejes = g["versiones"][v]["ejes"]
    if page.locator(".guia .eje").count() != len(ejes): errs.append("número de ejes distinto al de guia.json")
    nt = page.locator(".guia ol.temas a.tlink").count()
    if nt != sum(len(e["temas"]) for e in ejes): errs.append(f"índice: {nt} enlaces a temas")
    out["indice_temas"] = nt
    for e in ejes:
        n = page.locator(f'#eje-{e["id"]} .chips a').count()
        if n == 0 or n != len(e["dias"]): errs.append(f"eje {e['id']}: {n} días enlazados")
    hrefs = page.locator("#tabla-docs a").evaluate_all("els => els.map(e => e.href)")
    ndocs = len([d for d in g["documentos"] if v in d["versiones"]])
    if len(hrefs) != ndocs: errs.append(f"tabla de documentos: {len(hrefs)} != {ndocs}")
    bad = [h for h in hrefs if not any(dom in h for dom in OFFICIAL)]
    if bad: errs.append(f"enlaces no oficiales en la guía: {bad}")
    # todos los ejes usados por el plan existen en la guía
    used = {t.get("eje") for d in plan["versions"][v]["days"] for t in d["topics"]} - {"repaso", None}
    miss = used - {e["id"] for e in ejes}
    if miss: errs.append(f"ejes del plan sin sección en la guía: {miss}")
    page.screenshot(path=str(OUT / f"test-{v}-guia.png"), full_page=False)
    out.update({"ejes": len(ejes), "docs": len(hrefs), "pass": True})
    return out

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
    for r in results:
        idx = json.loads(b.new_context().request.get(BASE + "data/index.json").text())[r["version"]]
        other = next(d for d in idx if d != r["date"])
        off = check_offline_partial(b, r["version"], other); r["offline_partial"] = off
        if not off["pass"]: r["errors"] += off["errors"]; r["pass"] = False
    prog = check_progress(b, {r["version"]: (r["cloud"]["attempt_id"], r["shown"].replace(" ", "")) for r in results})
    for r in results:
        r["progress_page"] = prog
        if not prog["pass"]: r["errors"] += prog["errors"]; r["pass"] = False
    b.close()
print(json.dumps(results, ensure_ascii=False, indent=1))
print("TEST_ATTEMPT_IDS=" + ",".join(TEST_IDS))
pathlib.Path("/tmp/scd_test_ids.txt").write_text("\n".join(TEST_IDS))
sys.exit(0 if all(r["pass"] for r in results) else 1)
