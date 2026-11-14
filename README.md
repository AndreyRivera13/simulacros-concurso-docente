# Simulacros · Concurso Docente 2027 (CNSC)

Sitio estático con **plan de estudio** y **simulacros diarios** con retroalimentación inmediata para dos aspirantes:

| Versión | Empleo | Aspirante | Ejes diarios |
|---|---|---|---|
| **A** | Ciencias Naturales y Educación Ambiental | Yasmin | Disciplinar CN y Ed. Ambiental + conocimiento general del concurso |
| **B** | Tecnología e Informática | Andrey | Disciplinar Tecnología e Informática + leyes (desde lo básico) y conocimiento general |

- **Sitio:** https://andreyrivera13.github.io/simulacros-concurso-docente/
  (`?v=A|B`, `&d=AAAA-MM-DD`, `#quiz` o `#plan`)
- **Plan:** 15-nov-2026 → 31-ene-2027 (78 días). Cada día: 2 temas × 20 preguntas (40). Cada 7.º día es repaso semanal.
- **Fecha objetivo:** inicio de inscripciones generales **estimado** el 1-feb-2027 (la CNSC solo indica "febrero de 2027"
  en su cronograma preliminar; las vacantes reservadas para personas con discapacidad se inscriben del 23-nov-2026 al
  15-ene-2027, Resolución 11673 de 2026). Fuentes en `data/plan.json → meta.sources`.

Material de práctica **no oficial**.

## Estructura

```
index.html, assets/        # app estática (JS sin dependencias)
data/plan.json             # plan completo de ambas versiones (generado por scripts/build_plan.py)
data/index.json            # días disponibles por versión (lo actualiza build_day.py)
data/<V>/<AAAA-MM-DD>.json # simulacro de un día (lo produce build_day.py; no editar a mano)
drafts/<V>/<AAAA-MM-DD>.txt# borrador fuente del día (formato de texto, correcta primero)
scripts/build_plan.py      # (re)genera plan.json — temario, ejes, fechas, dificultad
scripts/next_day.py        # próximo día pendiente; encargo de generación (prompt); opcional --llm
scripts/build_day.py       # valida borrador, baraja opciones con balance, escribe JSON e index
scripts/daily.sh           # trabajo diario completo: generar → validar → commit → push
tests/e2e.py               # prueba E2E (Playwright/Chromium) contra cualquier URL
```

## Formato del borrador (`drafts/<V>/<fecha>.txt`)

```
## <id-del-tema-tal-cual-en-plan.json>
Q: Enunciado (las líneas siguientes, con sangría, se muestran como bloque de código)
+ opción correcta (siempre primero)
- distractor
- distractor
E: explicación breve (no mencionar letras A/B/C: las opciones se barajan)
```
`build_day.py` exige: temas en el mismo orden del plan, exactamente 20 preguntas por tema, 3 opciones distintas,
1 correcta, explicación, sin enunciados repetidos. Reparte la correcta de forma balanceada entre A/B/C.

## Procedimiento diario (agregar un día)

Hay 7 días pre-generados por versión (15 al 21 de nov). El trabajo diario mantiene ese colchón generando el
siguiente día pendiente de cada versión:

```bash
cd simulacros-concurso-docente
git pull --ff-only
python3 scripts/next_day.py                    # → "A 2026-11-22" / "B 2026-11-22"
python3 scripts/next_day.py A 2026-11-22       # escribe drafts/A/2026-11-22.prompt.md (encargo con temas y reglas)
#   Generar drafts/A/2026-11-22.txt siguiendo ese encargo (un agente lo escribe, o: añadir --llm con
#   LLM_API_KEY / LLM_BASE_URL / LLM_MODEL para usar una API compatible con OpenAI).
python3 scripts/build_day.py A 2026-11-22      # valida y crea data/A/2026-11-22.json + index.json
#   (repetir para B)
python3 -m http.server 8765 &                  # opcional: prueba local
python tests/e2e.py http://localhost:8765/ 2026-11-22
git add data drafts && git commit -m "Simulacro diario: A/B 2026-11-22" && git push
#   GitHub Pages redepliega en ~1 min; verificar:
python tests/e2e.py https://andreyrivera13.github.io/simulacros-concurso-docente/
```
O todo en uno (si ya existen los borradores o hay API de LLM configurada): `scripts/daily.sh`.

Para cambiar el plan (fechas, temas, 3 temas/día, etc.) edite `scripts/build_plan.py` y ejecútelo; los ids de los
temas ya generados no deben cambiar.

## Pruebas E2E

```bash
python3 -m venv ~/.venv-pw && ~/.venv-pw/bin/pip install playwright && ~/.venv-pw/bin/python -m playwright install chromium
~/.venv-pw/bin/python tests/e2e.py <URL> [AAAA-MM-DD]
```
Responde todas las preguntas del día (2 de cada 3 correctas), comprueba selección, retroalimentación inmediata con
explicación, bloqueo de la pregunta, puntaje por tema y total, persistencia al recargar y el plan con el día de hoy
resaltado; guarda `test-A.png` y `test-B.png`.
