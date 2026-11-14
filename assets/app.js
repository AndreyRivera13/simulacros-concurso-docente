/* Simulacros Concurso Docente 2027 — app estática (sin backend). */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const LETTERS = ["A", "B", "C", "D"];
  const params = new URLSearchParams(location.search);
  const state = { v: params.get("v") || localStorage.getItem("scd.v") || "A", date: params.get("d"), plan: null, index: null, day: null, answers: {} };
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

  function renderHeader() {
    document.querySelectorAll(".vbtn").forEach((b) => b.classList.toggle("on", b.dataset.v === state.v));
    const view = location.hash === "#plan" ? "plan" : "quiz";
    document.querySelectorAll(".vlink").forEach((a) => a.classList.toggle("on", a.dataset.view === view));
    $("#view-quiz").hidden = view !== "quiz"; $("#view-plan").hidden = view !== "plan";
    $("#scorebar").hidden = view !== "quiz" || !state.day;
    const m = state.plan.meta, t = todayBogota(), left = daysBetween(t, m.inscription_estimate);
    $("#countdown").innerHTML = `📅 Inscripciones generales (vacantes sin reserva): <b>${left > 0 ? "faltan " + left + " días" : "en curso o pasadas"}</b> — fecha objetivo ${fmtDate(m.inscription_estimate)} <em>(estimada)</em>. <a href="#plan">Ver plan</a>`;
    document.title = `Simulacros ${state.v === "A" ? "Ciencias Naturales" : "Tecnología e Informática"} · Concurso Docente 2027`;
  }

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
    $("#dayinfo").innerHTML = `<div class="dayinfo"><h2>Día ${pd.n} · ${esc(fmtDate(pd.date))}</h2><div class="meta">${pd.kind === "repaso" ? "Repaso semanal" : "Estudio"} · Dificultad ${esc(pd.difficulty)} · ${pd.topics.length} temas × ${state.plan.meta.questions_per_topic} preguntas</div></div>`;
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
        <div class="track">${esc(t.track)} · <span class="tscore" data-topic-score="${ti}"></span></div>
        ${t.questions.map((q, qi) => renderQuestion(t, ti, q, qi)).join("")}
      </section>`).join("");
    $("#quiz").innerHTML = html + `<p style="text-align:center"><button class="btn ghost" id="reset">Reiniciar este simulacro</button></p>`;
    $("#reset").onclick = () => { if (confirm("¿Borrar tus respuestas de este día?")) { state.answers = {}; saveAnswers(); renderQuiz(); scrollTo(0, 0); } };
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
    if (persist) { state.answers[`${ti}-${qi}`] = choice; saveAnswers(); updateScores(); }
  }

  function updateScores() {
    const day = state.day; if (!day) return;
    let tot = 0, totOk = 0, answered = 0;
    const per = day.topics.map((t, ti) => {
      let a = 0, ok = 0;
      t.questions.forEach((q, qi) => { const c = state.answers[`${ti}-${qi}`]; if (c !== undefined) { a++; if (c === q.answer) ok++; } });
      tot += t.questions.length; totOk += ok; answered += a;
      const el = document.querySelector(`[data-topic-score="${ti}"]`); if (el) el.textContent = `${a}/${t.questions.length} respondidas · ${ok} correctas`;
      return { title: t.title, n: t.questions.length, a, ok };
    });
    const sb = $("#scorebar"); sb.hidden = location.hash === "#plan";
    sb.innerHTML = `Respondidas <b id="answered-count">${answered}</b>/${tot} · Correctas <b id="correct-count">${totOk}</b>`;
    const res = $("#results");
    if (answered === tot) {
      const pct = Math.round((totOk / tot) * 100);
      res.innerHTML = `<h2>Resultado final del día</h2>
        <p class="big" id="total-score">${totOk} / ${tot}</p>
        <p>Porcentaje: <b id="total-pct">${pct}%</b> · <span class="${pct >= 60 ? "pass" : "fail"}">${pct >= 60 ? "Por encima" : "Por debajo"} del mínimo aprobatorio de referencia (60/100)</span></p>
        <table><thead><tr><th>Tema</th><th>Correctas</th><th>%</th></tr></thead><tbody>
        ${per.map((p, i) => `<tr data-result-topic="${i}"><td>${esc(p.title)}</td><td class="rt-score">${p.ok} / ${p.n}</td><td>${Math.round((p.ok / p.n) * 100)}%</td></tr>`).join("")}
        </tbody></table>
        <p style="margin-top:14px"><button class="btn" id="reset2">Volver a intentar</button> <a class="btn" style="text-decoration:none;background:#1f3a5f" href="#plan">Ver plan de estudio</a></p>`;
      res.hidden = false;
      $("#reset2").onclick = () => { state.answers = {}; saveAnswers(); renderQuiz(); scrollTo(0, 0); };
    } else res.hidden = true;
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
      <td><ul>${d.topics.map((x) => `<li>${esc(x.title)}${x.review ? '<span class="tag">repaso</span>' : ""}</li>`).join("")}</ul></td>
      <td class="st">${avail.has(d.date) ? `<a href="?v=${state.v}&d=${d.date}#quiz">Practicar ▶</a>` : '<span class="pend">pendiente</span>'}</td></tr>`).join("");
    $("#plan").innerHTML = `<div class="plan">${info}<table><thead><tr><th>Día</th><th>Fecha</th><th>Nivel</th><th>Temas</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`;
    const tr = document.querySelector("tr.today"); if (tr) setTimeout(() => tr.scrollIntoView({ block: "center" }), 50);
  }

  // ---------- Router ----------
  async function route() {
    renderHeader(); updateURL();
    if (location.hash === "#plan") { renderPlan(); $("#scorebar").hidden = true; }
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

  Promise.all([fetchJSON("data/plan.json"), fetchJSON("data/index.json")]).then(([plan, index]) => {
    state.plan = plan; state.index = index; if (!state.date) state.date = defaultDate(); route();
  }).catch((e) => { document.querySelector("main").innerHTML = `<div class="empty">Error cargando datos: ${esc(e.message)}</div>`; });
})();
