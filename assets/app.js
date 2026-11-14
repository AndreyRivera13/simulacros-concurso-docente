/* Simulacros Concurso Docente 2027 — app estática (sin backend). */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const LETTERS = ["A", "B", "C", "D"];
  const params = new URLSearchParams(location.search);
  const state = { v: params.get("v") || localStorage.getItem("scd.v") || "A", date: params.get("d"), plan: null, index: null, day: null, answers: {}, guia: null };
  if (!["A", "B"].includes(state.v)) state.v = "A";

  const todayBogota = () => new Intl.DateTimeFormat("en-CA", { timeZone: "America/Bogota", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  const fmtDate = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  const daysBetween = (a, b) => Math.round((new Date(b + "T00:00:00") - new Date(a + "T00:00:00")) / 86400000);
  const fetchJSON = (u) => fetch(u, { cache: "no-cache" }).then((r) => { if (!r.ok) throw new Error(u + " " + r.status); return r.json(); });

  function updateURL() {
    const p = new URLSearchParams(); p.set("v", state.v); if (state.date) p.set("d", state.date);
    history.replaceState(null, "", "?" + p.toString() + location.hash);
  }
  const vplan = () => state.plan.versions[state.v];
  const available = () => state.index[state.v] || [];

  function defaultDate() {
    const t = todayBogota(), days = vplan().days.map((d) => d.date);
    if (t < days[0]) return days[0];
    if (t > days[days.length - 1]) return available().slice(-1)[0] || days[days.length - 1];
    return t;
  }

  const VIEWS = ["quiz", "plan", "guia", "progreso"];
  function currentView() {
    const h = location.hash.replace(/^#/, "");
    const base = h.split("-")[0];
    return VIEWS.includes(base) && base !== "quiz" ? base : "quiz";
  }
  const ejeOf = (id) => state.guia && state.guia.versiones[state.v].ejes.find((e) => e.id === id);
  const guideLink = (t, cls = "glink") => {
    if (!t || !t.eje) return "";
    if (t.eje === "repaso") return `<a class="${cls}" href="#guia">📘 Guía de estudio</a>`;
    const e = ejeOf(t.eje);
    return `<a class="${cls}" href="#guia-${esc(t.eje)}" data-guide="${esc(t.eje)}">📘 Guía: ${esc(e ? e.nombre : t.eje)}</a>`;
  };

  function renderHeader() {
    document.querySelectorAll(".vbtn").forEach((b) => b.classList.toggle("on", b.dataset.v === state.v));
    const view = currentView();
    document.querySelectorAll(".vlink").forEach((a) => a.classList.toggle("on", a.dataset.view === view));
    VIEWS.forEach((x) => { $("#view-" + x).hidden = view !== x; });
    $("#scorebar").hidden = view !== "quiz" || !state.day;
    const m = state.plan.meta, t = todayBogota(), left = daysBetween(t, m.inscription_estimate);
    $("#countdown").innerHTML = `📅 Inscripciones generales (vacantes sin reserva): <b>${left > 0 ? "faltan " + left + " días" : "en curso o pasadas"}</b> — fecha objetivo ${fmtDate(m.inscription_estimate)} <em>(estimada)</em>. <a href="#plan">Ver plan</a> · <a href="#guia">Guía de estudio (fuentes oficiales)</a>`;
    document.title = `Simulacros ${state.v === "A" ? "Ciencias Naturales" : "Tecnología e Informática"} · Concurso Docente 2027`;
  }

  // ---------- Resultados en la nube (Supabase; clave pública + RLS) ----------
  const SB_URL = "https://ggcgbjonlxxcmegknfxi.supabase.co/rest/v1/quiz_attempts";
  const SB_KEY = "sb_publishable_TY2maiftFyPDWj_SovDXCQ_7kUE5Lbq";
  const ATT_PREFIX = "scd.att.";
  const PEOPLE = { A: "Yasmin", B: "Andrey" };
  const uuid = () => (crypto.randomUUID ? crypto.randomUUID() : "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (c) => (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)));
  const attKey = () => `${ATT_PREFIX}${state.v}.${state.date}`;
  const readAtt = (k) => { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch { return null; } };
  const writeAtt = (k, a) => localStorage.setItem(k, JSON.stringify(a));
  let saveTimer = null, syncing = false;
  function setSaveStatus(kind, msg) {
    document.querySelectorAll(".save-status").forEach((el) => { el.dataset.state = kind; el.textContent = msg; });
  }
  function attemptPayload(per, totOk, tot, answered) {
    return { quiz_date: state.date, version: state.v, person: PEOPLE[state.v],
      topic_scores: per.map((p) => ({ id: p.id, title: p.title, correct: p.ok, total: p.n, answered: p.a })),
      answered, total_correct: totOk, total_questions: tot, percentage: Math.round((totOk / tot) * 10000) / 100, completed: answered === tot };
  }
  function queueSave(payload, immediate) {
    const k = attKey(); let a = readAtt(k);
    if (!a) a = { id: uuid(), token: uuid(), inserted: false, rev: 0 };
    a.payload = payload; a.rev = (a.rev || 0) + 1; a.dirty = true; writeAtt(k, a);
    setSaveStatus("saving", "⏳ Guardando…");
    clearTimeout(saveTimer); saveTimer = setTimeout(syncAll, immediate ? 0 : 1200);
  }
  async function pushAttempt(k) {
    const a = readAtt(k); if (!a || !a.dirty) return true;
    const rev = a.rev, h = { apikey: SB_KEY, "Content-Type": "application/json", "x-owner-token": a.token };
    if (!a.inserted) {
      const r = await fetch(SB_URL, { method: "POST", headers: { ...h, Prefer: "return=minimal" }, body: JSON.stringify({ id: a.id, owner_token: a.token, ...a.payload }) });
      if (r.status === 201) { const cur = readAtt(k); cur.inserted = true; if (cur.rev === rev) cur.dirty = false; writeAtt(k, cur); return !cur.dirty || pushAttempt(k); }
      if (r.status !== 409) throw new Error("POST " + r.status);
      const cur = readAtt(k); cur.inserted = true; writeAtt(k, cur);
    }
    const { quiz_date, version, person, ...upd } = readAtt(k).payload;
    const r = await fetch(`${SB_URL}?id=eq.${a.id}`, { method: "PATCH", headers: { ...h, Prefer: "return=minimal,count=exact" }, body: JSON.stringify(upd) });
    const range = r.headers.get("content-range") || "";
    if (!r.ok || !/\/1$/.test(range)) throw new Error("PATCH " + r.status + " " + range);
    const cur = readAtt(k); if (cur.rev === rev) { cur.dirty = false; writeAtt(k, cur); }
    return !cur.dirty;
  }
  async function syncAll() {
    if (syncing) { clearTimeout(saveTimer); saveTimer = setTimeout(syncAll, 800); return; }
    syncing = true; let fail = 0;
    const keys = Object.keys(localStorage).filter((k) => k.startsWith(ATT_PREFIX) && (readAtt(k) || {}).dirty);
    for (const k of keys) { try { await pushAttempt(k); } catch (e) { fail++; console.warn("No se pudo guardar", k, e.message); } }
    syncing = false;
    const cur = readAtt(attKey());
    if (fail) setSaveStatus("pending", "📴 Sin conexión con la nube: guardado en este navegador; se reintentará");
    else if (cur && !cur.dirty) setSaveStatus("ok", "☁️ Guardado en la nube");
    if (fail) { clearTimeout(saveTimer); saveTimer = setTimeout(syncAll, 30000); }
    const el = document.querySelector("#results"); if (el && cur) el.dataset.attemptId = cur.id;
    return fail === 0;
  }
  window.addEventListener("online", syncAll);
  window.__scdSync = syncAll; // usado por las pruebas E2E

  // ---------- Quiz ----------
  const storeKey = () => `scd.ans.${state.v}.${state.date}`;
  function loadAnswers() { try { state.answers = JSON.parse(localStorage.getItem(storeKey()) || "{}"); } catch { state.answers = {}; } }
  function saveAnswers() { localStorage.setItem(storeKey(), JSON.stringify(state.answers)); }

  async function renderQuiz() {
    const days = vplan().days, pd = days.find((d) => d.date === state.date);
    const avail = available(), i = avail.indexOf(state.date);
    $("#prev").disabled = !(avail.length && (i > 0 || (i === -1 && avail[0] < state.date)));
    $("#next").disabled = !(avail.length && ((i >= 0 && i < avail.length - 1) || (i === -1 && avail[avail.length - 1] > state.date)));
    $("#results").hidden = true; $("#quiz").innerHTML = ""; state.day = null;
    if (!pd) { $("#dayinfo").innerHTML = `<div class="dayinfo"><h2>${esc(state.date)}</h2><div class="meta">Fuera del plan</div></div>`; $("#quiz").innerHTML = `<div class="empty">Esta fecha está fuera del plan (${days[0].date} a ${days[days.length - 1].date}).</div>`; renderHeader(); return; }
    $("#dayinfo").innerHTML = `<div class="dayinfo"><h2>Día ${pd.n} · ${esc(fmtDate(pd.date))}</h2><div class="meta">${pd.kind === "repaso" ? "Repaso semanal" : "Estudio"} · Dificultad ${esc(pd.difficulty)} · ${pd.topics.length} temas × ${state.plan.meta.questions_per_topic} preguntas</div>
      <div class="glinks" id="day-guide-links">${pd.topics.map((t) => guideLink(t)).join(" · ")}</div></div>`;
    if (!avail.includes(state.date)) {
      const last = avail.filter((d) => d <= state.date).slice(-1)[0] || avail[0];
      $("#quiz").innerHTML = `<div class="empty"><p>El simulacro de este día aún no se ha generado.</p><p>Temas previstos: <b>${pd.topics.map((t) => esc(t.title)).join("</b> y <b>")}</b>.</p>${last ? `<p><a href="?v=${state.v}&d=${last}#quiz">Ir al último simulacro disponible (${last})</a></p>` : ""}</div>`;
      renderHeader(); return;
    }
    let day;
    try { day = await fetchJSON(`data/${state.v}/${state.date}.json`); } catch (e) { $("#quiz").innerHTML = `<div class="empty">No se pudo cargar el simulacro (${esc(e.message)}).</div>`; return; }
    state.day = day; loadAnswers();
    const html = day.topics.map((t, ti) => `
      <section class="topic" data-topic="${ti}">
        <h3>Tema ${ti + 1}: ${esc(t.title)}</h3>
        <div class="track">${esc(t.track)} · <span class="tscore" data-topic-score="${ti}"></span>${guideLink(pd.topics.find((x) => x.id === t.id) || pd.topics[ti])}</div>
        ${t.questions.map((q, qi) => renderQuestion(t, ti, q, qi)).join("")}
      </section>`).join("");
    $("#quiz").innerHTML = html + `<p style="text-align:center"><button class="btn ghost" id="reset">Reiniciar este simulacro</button></p>`;
    $("#reset").onclick = () => { if (confirm("¿Borrar tus respuestas de este día?")) { state.answers = {}; saveAnswers(); localStorage.removeItem(attKey()); renderQuiz(); scrollTo(0, 0); } };
    Object.entries(state.answers).forEach(([k, choice]) => { const [ti, qi] = k.split("-").map(Number); applyAnswer(ti, qi, choice, false); });
    updateScores(); renderHeader();
  }

  function renderQuestion(t, ti, q, qi) {
    const lines = q.q.split("\n"), stem = lines[0], code = lines.slice(1).join("\n");
    return `<article class="q" data-q="${ti}-${qi}">
      <div class="num">Pregunta ${qi + 1} de ${t.questions.length}</div>
      ${q.context ? `<div class="ctx">${esc(q.context)}</div>` : ""}
      <p class="stem">${esc(stem)}</p>${code ? `<pre><code>${esc(code)}</code></pre>` : ""}
      <div class="opts">${q.options.map((o, oi) => `<button class="option" data-opt="${oi}"><span class="l">${LETTERS[oi]}.</span><span>${esc(o)}</span></button>`).join("")}</div>
      <div class="feedback" hidden></div>
    </article>`;
  }

  function applyAnswer(ti, qi, choice, persist) {
    const q = state.day.topics[ti].questions[qi], card = document.querySelector(`[data-q="${ti}-${qi}"]`);
    if (!card || card.dataset.answered) return;
    card.dataset.answered = "1";
    const ok = choice === q.answer;
    card.querySelectorAll(".option").forEach((b) => {
      const oi = Number(b.dataset.opt); b.disabled = true;
      if (oi === q.answer) b.classList.add("correct");
      if (oi === choice) { b.classList.add("chosen"); if (!ok) b.classList.add("incorrect"); }
    });
    card.dataset.result = ok ? "correct" : "incorrect";
    const fb = card.querySelector(".feedback");
    fb.className = "feedback " + (ok ? "ok" : "bad");
    fb.innerHTML = `<b>${ok ? "✅ ¡Correcto!" : `❌ Incorrecto. La respuesta correcta es la ${LETTERS[q.answer]}.`}</b>${esc(q.explanation)}`;
    fb.hidden = false;
    if (persist) { state.answers[`${ti}-${qi}`] = choice; saveAnswers(); const s = updateScores(); if (s) queueSave(attemptPayload(s.per, s.totOk, s.tot, s.answered), s.answered === s.tot); }
  }

  function updateScores() {
    const day = state.day; if (!day) return;
    let tot = 0, totOk = 0, answered = 0;
    const per = day.topics.map((t, ti) => {
      let a = 0, ok = 0;
      t.questions.forEach((q, qi) => { const c = state.answers[`${ti}-${qi}`]; if (c !== undefined) { a++; if (c === q.answer) ok++; } });
      tot += t.questions.length; totOk += ok; answered += a;
      const el = document.querySelector(`[data-topic-score="${ti}"]`); if (el) el.textContent = `${a}/${t.questions.length} respondidas · ${ok} correctas`;
      return { id: t.id, title: t.title, n: t.questions.length, a, ok };
    });
    const sb = $("#scorebar"); sb.hidden = currentView() !== "quiz";
    const att = readAtt(attKey());
    const st = !att ? ["", ""] : att.dirty ? ["pending", "⏳ Pendiente de guardar en la nube"] : ["ok", "☁️ Guardado en la nube"];
    sb.innerHTML = `Respondidas <b id="answered-count">${answered}</b>/${tot} · Correctas <b id="correct-count">${totOk}</b> <span class="save-status" data-state="${st[0]}">${st[1]}</span>`;
    const res = $("#results");
    if (answered === tot) {
      const pct = Math.round((totOk / tot) * 100);
      res.innerHTML = `<h2>Resultado final del día</h2>
        <p class="big" id="total-score">${totOk} / ${tot}</p>
        <p>Porcentaje: <b id="total-pct">${pct}%</b> · <span class="${pct >= 60 ? "pass" : "fail"}">${pct >= 60 ? "Por encima" : "Por debajo"} del mínimo aprobatorio de referencia (60/100)</span></p>
        <table><thead><tr><th>Tema</th><th>Correctas</th><th>%</th></tr></thead><tbody>
        ${per.map((p, i) => `<tr data-result-topic="${i}"><td>${esc(p.title)}</td><td class="rt-score">${p.ok} / ${p.n}</td><td>${Math.round((p.ok / p.n) * 100)}%</td></tr>`).join("")}
        </tbody></table>
        <p class="save-line"><span class="save-status" id="save-status" data-state="${st[0]}">${st[1]}</span></p>
        <p style="margin-top:14px"><button class="btn" id="reset2">Volver a intentar</button> <a class="btn" style="text-decoration:none;background:#1f3a5f" href="#progreso">Ver mi progreso</a> <a class="btn" style="text-decoration:none;background:#1f3a5f" href="#plan">Ver plan de estudio</a></p>`;
      if (att) res.dataset.attemptId = att.id;
      res.hidden = false;
      $("#reset2").onclick = () => { state.answers = {}; saveAnswers(); localStorage.removeItem(attKey()); renderQuiz(); scrollTo(0, 0); };
    } else res.hidden = true;
    return { per, totOk, tot, answered };
  }

  // ---------- Plan ----------
  function renderPlan() {
    const vp = vplan(), m = state.plan.meta, t = todayBogota(), avail = new Set(available());
    const study = vp.days.filter((d) => d.kind === "estudio").length;
    let info = `<div class="planinfo"><b>Versión ${state.v}: ${esc(vp.name)}</b> (${esc(vp.person)}) · ${vp.days.length} días, del ${fmtDate(m.start)} al ${fmtDate(m.end)} ·
      ${study} días de estudio con 2 temas diarios (${esc(vp.tracks.join(" + "))}) y ${vp.days.length - study} días de repaso semanal · ${m.questions_per_topic} preguntas por tema.<br>
      <small>${esc(m.inscription_note)} Fuentes: ${m.sources.map((s, i) => `<a href="${esc(s)}" target="_blank" rel="noopener">[${i + 1}]</a>`).join(" ")}</small>`;
    if (t < m.start) info += `<br><b>El plan inicia mañana (${fmtDate(m.start)}).</b>`;
    info += `</div>`;
    const rows = vp.days.map((d) => `<tr class="${d.date === t ? "today " : ""}${d.kind}" data-date="${d.date}">
      <td><b>${d.n}</b></td><td>${esc(new Date(d.date + "T12:00:00").toLocaleDateString("es-CO", { weekday: "short", day: "numeric", month: "short" }))}${d.date === t ? '<span class="tag">HOY</span>' : ""}</td>
      <td>${esc(d.difficulty)}</td>
      <td><ul>${d.topics.map((x) => `<li>${esc(x.title)}${x.review ? '<span class="tag">repaso</span>' : ""}${x.eje && x.eje !== "repaso" ? ` <a class="glink" href="#guia-${esc(x.eje)}" title="Ver en la Guía de estudio">📘</a>` : ""}</li>`).join("")}</ul></td>
      <td class="st">${avail.has(d.date) ? `<a href="?v=${state.v}&d=${d.date}#quiz">Practicar ▶</a>` : '<span class="pend">pendiente</span>'}</td></tr>`).join("");
    $("#plan").innerHTML = `<div class="plan">${info}<table><thead><tr><th>Día</th><th>Fecha</th><th>Nivel</th><th>Temas</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`;
    const tr = document.querySelector("tr.today"); if (tr) setTimeout(() => tr.scrollIntoView({ block: "center" }), 50);
  }

  // ---------- Guía de estudio ----------
  function renderGuide() {
    const g = state.guia, c = g.concurso, vp = vplan(), ejes = g.versiones[state.v].ejes, t = todayBogota(), avail = new Set(available());
    const doc = Object.fromEntries(g.documentos.map((d) => [d.id, d]));
    const dlink = (id) => { const d = doc[id]; return d ? `<a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.nombre)}</a> <span class="src">(${esc(d.emisor)}, ${d.anio})</span>` : esc(id); };
    const src = (ids) => `<div class="src">Fuente: ${[].concat(ids).map((i) => { const d = doc[i]; return d ? `<a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.nombre)}</a>` : esc(i); }).join(" · ")}</div>`;
    const docs = g.documentos.filter((d) => d.versiones.includes(state.v));
    const html = `<div class="guia">
      <div class="planinfo"><b>Guía de estudio · Versión ${state.v}: ${esc(vp.name)}</b> (${esc(vp.person)}). Construida solo con documentos oficiales (CNSC, MEN, Función Pública); cada eje enlaza su fuente y los días del plan que lo trabajan. Actualizada: ${esc(g.updated)}.
        <div class="toc">Ir a: <a href="#guia-concurso">Cómo funciona el concurso</a> <a href="#guia-ejes">Ejes y qué estudiar</a> <a href="#guia-documentos">Documentos oficiales</a></div></div>
      <div class="warn" id="estado-ejes">⚠️ <b>Estado de los ejes temáticos 2026-2027:</b> ${esc(c.estado_ejes)}</div>

      <h2 id="sec-concurso">1. Cómo funciona el concurso (Procesos de Selección 2917 a 3006 de 2026)</h2>
      <p><b>Etapas</b> (en este orden):</p><ol>${c.etapas.map((e) => `<li>${esc(e)}</li>`).join("")}</ol>${src(c.etapas_fuente)}
      <p><b>Pruebas, carácter, mínimos y pesos</b></p>
      <table id="tabla-pruebas"><thead><tr><th>Prueba</th><th>Carácter</th><th>Mínimo aprobatorio</th><th>Peso docente</th><th>Peso directivo</th><th>Qué evalúa</th></tr></thead><tbody>
      ${c.pruebas.map((p) => `<tr><td><b>${esc(p.prueba)}</b></td><td>${esc(p.caracter)}</td><td>${esc(p.minimo)}</td><td><b>${esc(p.peso_docente)}</b></td><td>${esc(p.peso_directivo)}</td><td>${esc(p.evalua)}</td></tr>`).join("")}
      </tbody></table>${src(c.pruebas_fuente)}
      <p>${esc(c.pesos_componentes)}</p>${src(["cnsc-anexo", "d574"])}
      <p><b>Valoración de antecedentes – docente de aula (100 puntos)</b></p>
      <table><thead><tr><th>Factor</th><th>Criterio</th><th>Máximo</th></tr></thead><tbody>${c.antecedentes_docente_aula.map((r) => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td>${esc(r[2])}</td></tr>`).join("")}</tbody></table>${src(c.antecedentes_fuente)}
      <p><b>Referencia del concurso anterior (2022):</b> ${esc(c.referencia_2022)}</p>${src(c.referencia_2022_fuentes)}

      <h2 id="sec-ejes">2. Ejes oficiales y qué estudiar</h2>
      <p class="src">Cada eje corresponde a un componente oficial de la prueba (Anexo técnico 2026, num. 2.1), a la psicotécnica/entrevista o al marco normativo que exige el Manual de Funciones. Los días en verde ya tienen simulacro.</p>
      ${ejes.map((e) => `<article class="eje" id="eje-${esc(e.id)}" data-eje="${esc(e.id)}">
        <h3>${esc(e.nombre)}</h3><span class="comp">${esc(e.componente)}</span>
        <p class="ofi"><b>Base oficial:</b> ${esc(e.oficial)}</p>
        <b>Qué estudiar</b><ul>${e.estudiar.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
        <b>Documentos</b><ul class="docs">${e.docs.map((i) => `<li>${dlink(i)}</li>`).join("")}</ul>
        <details ${e.dias.some((d) => d.date === t) ? "open" : ""}><summary>Días del plan que lo cubren (${e.dias.length})</summary><div class="chips">
          ${e.dias.map((d) => `<a class="${avail.has(d.date) ? "done" : ""}" href="?v=${state.v}&d=${d.date}#quiz" title="${esc(d.title)}">Día ${d.n} · ${esc(d.date.slice(5))}</a>`).join("")}</div></details>
      </article>`).join("")}

      <h2 id="sec-documentos">3. Documentos oficiales (${docs.length})</h2>
      <table id="tabla-docs"><thead><tr><th>Documento</th><th>Emisor</th><th>Año</th><th>Por qué importa</th></tr></thead><tbody>
      ${docs.map((d) => `<tr><td><a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.nombre)}</a></td><td>${esc(d.emisor)}</td><td>${d.anio}</td><td>${esc(d.por_que)}</td></tr>`).join("")}
      </tbody></table>
      <p class="src">Enlaces verificados el ${esc(g.updated)}. Esta guía no reemplaza la Guía de orientación oficial: cuando la CNSC/ICFES la publique, se actualizará con sus ejes.</p>
    </div>`;
    $("#guia").innerHTML = html;
    const h = location.hash.replace(/^#guia-?/, "");
    const target = { concurso: "sec-concurso", ejes: "sec-ejes", documentos: "sec-documentos" }[h] || (h ? "eje-" + h : "");
    const el = target && document.getElementById(target);
    if (el) { el.classList.add("hl"); setTimeout(() => el.scrollIntoView({ block: "start" }), 30); } else scrollTo(0, 0);
  }

  // ---------- Progreso ----------
  const fmtShort = (iso) => new Date(iso + "T12:00:00").toLocaleDateString("es-CO", { day: "numeric", month: "short" });
  function trendSVG(rows) {
    const W = 860, H = 240, L = 40, R = 34, T = 12, B = 34;
    const dates = [...new Set(rows.filter((r) => r.completed).map((r) => r.quiz_date))].sort();
    if (!dates.length) return "";
    const x = (d) => L + (dates.length === 1 ? (W - L - R) / 2 : (dates.indexOf(d) * (W - L - R)) / (dates.length - 1));
    const y = (p) => T + (1 - p / 100) * (H - T - B);
    const COL = { A: "#1e7d32", B: "#2f6fdf" };
    let g = `<line x1="${L}" x2="${W - R}" y1="${y(60)}" y2="${y(60)}" stroke="#b3261e" stroke-dasharray="5 4"/><text x="${W - R}" y="${y(60) - 4}" font-size="11" text-anchor="end" fill="#b3261e">mínimo de referencia 60 %</text>`;
    [0, 25, 50, 75, 100].forEach((p) => { g += `<line x1="${L}" x2="${W - R}" y1="${y(p)}" y2="${y(p)}" stroke="#eef1f6"/><text x="${L - 6}" y="${y(p) + 4}" font-size="11" text-anchor="end" fill="#5f6b7a">${p}</text>`; });
    dates.forEach((d, i) => { if (dates.length <= 12 || i % Math.ceil(dates.length / 12) === 0) g += `<text x="${x(d)}" y="${H - 12}" font-size="11" text-anchor="middle" fill="#5f6b7a">${fmtShort(d)}</text>`; });
    ["A", "B"].forEach((v) => {
      // por fecha: mejor intento COMPLETO (los parciales se ven en la tabla, no en la tendencia)
      const pts = dates.map((d) => { const c = rows.filter((r) => r.version === v && r.quiz_date === d && r.completed); return c.length ? [d, Math.max(...c.map((r) => Number(r.percentage)))] : null; }).filter(Boolean);
      if (!pts.length) return;
      g += `<polyline fill="none" stroke="${COL[v]}" stroke-width="2.5" points="${pts.map(([d, p]) => `${x(d)},${y(p)}`).join(" ")}"/>`;
      g += pts.map(([d, p]) => `<circle cx="${x(d)}" cy="${y(p)}" r="4" fill="${COL[v]}"><title>${PEOPLE[v]} · ${d}: ${p}%</title></circle>`).join("");
    });
    return `<svg id="trend" viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Tendencia del porcentaje por fecha">${g}</svg>
      <div class="legend"><span style="color:${COL.A}">● Yasmin (A)</span> <span style="color:${COL.B}">● Andrey (B)</span></div>`;
  }
  async function renderProgress() {
    const box = $("#progreso"); const filt = state.progFilter || "todas";
    box.innerHTML = `<div class="empty">Cargando historial…</div>`;
    await syncAll().catch(() => {});
    let rows, err = "";
    try {
      const r = await fetch(`${SB_URL}?select=id,created_at,updated_at,quiz_date,version,person,topic_scores,answered,total_correct,total_questions,percentage,completed&order=quiz_date.desc,updated_at.desc&limit=1000`, { headers: { apikey: SB_KEY }, cache: "no-store" });
      if (!r.ok) throw new Error("HTTP " + r.status); rows = await r.json();
    } catch (e) {
      err = e.message;
      rows = Object.keys(localStorage).filter((k) => k.startsWith(ATT_PREFIX)).map((k) => { const a = readAtt(k); return a && a.payload ? { id: a.id, updated_at: "", ...a.payload } : null; }).filter(Boolean);
    }
    const shown = rows.filter((r) => filt === "todas" || r.version === filt);
    const stats = (v) => {
      const rs = rows.filter((r) => r.version === v), c = rs.filter((r) => r.completed);
      const avg = c.length ? c.reduce((s, r) => s + Number(r.percentage), 0) / c.length : null;
      const last = c.slice().sort((a, b) => (a.quiz_date + a.updated_at < b.quiz_date + b.updated_at ? 1 : -1))[0];
      return `<div class="pcard" data-person="${v}"><b>${PEOPLE[v]}</b> <span class="src">Versión ${v}</span>
        <div class="big" id="avg-${v}">${avg === null ? "—" : avg.toFixed(1) + "%"}</div><div class="src">promedio de simulacros completos</div>
        <div>${c.length} completos · ${rs.length - c.length} parciales${last ? ` · último: ${fmtShort(last.quiz_date)} (${Number(last.percentage)}%)` : ""}</div></div>`;
    };
    box.innerHTML = `<div class="prog">
      <div class="planinfo"><b>Progreso</b> · historial compartido de Yasmin y Andrey (se guarda en la nube al responder; si no hay conexión, queda en este navegador y se reintenta).
        ${err ? `<br><span class="fail">No se pudo leer la nube (${esc(err)}); se muestran solo los intentos de este navegador.</span>` : ""}
        <div class="filter">Ver: ${["todas", "A", "B"].map((f) => `<button class="ghost fbtn${f === filt ? " on" : ""}" data-filter="${f}">${f === "todas" ? "Ambas versiones" : f + " · " + PEOPLE[f]}</button>`).join(" ")}</div></div>
      <div class="pcards">${["A", "B"].filter((v) => filt === "todas" || v === filt).map(stats).join("")}</div>
      <h3>Tendencia (% por fecha, simulacros completos)</h3>${shown.some((r) => r.completed) ? trendSVG(shown) : `<div class="empty">Aún no hay simulacros completos guardados.</div>`}
      <h3>Historial por fecha</h3>
      <table id="prog-table"><thead><tr><th>Fecha</th><th>Persona</th><th>Por tema</th><th>Total</th><th>%</th><th>Estado</th></tr></thead><tbody>
      ${shown.map((r) => `<tr data-attempt="${esc(r.id || "")}" data-version="${esc(r.version)}"><td>${esc(r.quiz_date)}</td><td>${esc(r.person)} (${esc(r.version)})</td>
        <td><ul>${(r.topic_scores || []).map((t) => `<li>${esc(t.title)}: <b>${t.correct}/${t.total}</b>${t.answered < t.total ? ` <span class="src">(${t.answered} resp.)</span>` : ""}</li>`).join("")}</ul></td>
        <td class="tot">${r.total_correct}/${r.total_questions}</td><td class="pct">${Number(r.percentage)}%</td>
        <td>${r.completed ? "Completo" : `Parcial (${r.answered}/${r.total_questions})`}</td></tr>`).join("")}
      </tbody></table></div>`;
    box.querySelectorAll(".fbtn").forEach((b) => (b.onclick = () => { state.progFilter = b.dataset.filter; renderProgress(); }));
    box.dataset.loaded = err ? "local" : "cloud";
  }

  // ---------- Router ----------
  async function route() {
    renderHeader(); updateURL();
    const view = currentView();
    if (view === "plan") { renderPlan(); $("#scorebar").hidden = true; }
    else if (view === "guia") { renderGuide(); $("#scorebar").hidden = true; }
    else if (view === "progreso") { $("#scorebar").hidden = true; await renderProgress(); }
    else { await renderQuiz(); }
  }
  document.addEventListener("click", (e) => {
    const opt = e.target.closest(".option");
    if (opt && !opt.disabled) { const card = opt.closest(".q"); const [ti, qi] = card.dataset.q.split("-").map(Number); applyAnswer(ti, qi, Number(opt.dataset.opt), true); return; }
    const vb = e.target.closest(".vbtn");
    if (vb) { state.v = vb.dataset.v; localStorage.setItem("scd.v", state.v); state.date = defaultDate(); route(); }
  });
  $("#prev").onclick = () => { const a = available(), i = a.indexOf(state.date); state.date = i > 0 ? a[i - 1] : a.filter((d) => d < state.date).slice(-1)[0]; route(); scrollTo(0, 0); };
  $("#next").onclick = () => { const a = available(), i = a.indexOf(state.date); state.date = i >= 0 ? a[i + 1] : a.find((d) => d > state.date); route(); scrollTo(0, 0); };
  window.addEventListener("hashchange", route);

  Promise.all([fetchJSON("data/plan.json"), fetchJSON("data/index.json"), fetchJSON("data/guia.json").catch(() => null)]).then(([plan, index, guia]) => {
    state.plan = plan; state.index = index; state.guia = guia; if (!state.date) state.date = defaultDate(); route();
    setTimeout(() => syncAll().catch(() => {}), 1500); // reintenta guardados pendientes
  }).catch((e) => { document.querySelector("main").innerHTML = `<div class="empty">Error cargando datos: ${esc(e.message)}</div>`; });
})();
