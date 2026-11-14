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
data/guia.json             # Guía de estudio: concurso, ejes oficiales, documentos y días del plan (build_guide.py)
data/temas.json            # Contenido de estudio por tema (HTML) generado desde content/temas/*.md
content/temas/*.md         # Contenido de estudio en Markdown (un archivo por tema)
data/<V>/<AAAA-MM-DD>.json # simulacro de un día (lo produce build_day.py; no editar a mano)
drafts/<V>/<AAAA-MM-DD>.txt# borrador fuente del día (formato de texto, correcta primero)
scripts/build_plan.py      # (re)genera plan.json — temario, ejes, fechas, dificultad
scripts/build_guide.py     # (re)genera guia.json desde fuentes oficiales y cruza cada eje con plan.json
scripts/check_links.py     # verifica que todos los enlaces oficiales respondan 200
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
temas ya generados no deben cambiar. Cada tema declara su `eje` oficial; después ejecute `python3 scripts/build_guide.py`
(falla si algún eje del plan no existe en la guía) y `python3 scripts/check_links.py`.

## Resultados en la nube y pestaña Progreso (`#progreso`)

Cada intento se guarda en Supabase (proyecto `simulacros-concurso-docente`, ref `ggcgbjonlxxcmegknfxi`), tabla
`public.quiz_attempts` (esquema y políticas en `supabase/schema.sql`). El navegador genera `id` y un `owner_token`
secreto; cada respuesta hace un guardado parcial (misma fila) y al completar el día se guarda de inmediato.
RLS: lectura pública (sin `owner_token`), inserción anónima, actualización solo con el encabezado `x-owner-token`
del intento, sin borrado. Si no hay conexión, el intento queda en `localStorage` (`scd.att.<V>.<fecha>`) y se
reintenta al cargar, al volver la conexión y cada 30 s. La pestaña Progreso muestra el historial de ambas personas,
puntaje por tema, totales, promedio y tendencia, con filtro por versión. Nota: los proyectos gratuitos de Supabase se
pausan tras ~7 días sin uso; si pasa, reactívelo desde el panel (los intentos siguen guardándose localmente).

Las pruebas E2E crean intentos reales; al final imprimen `TEST_ATTEMPT_IDS=...` para borrarlos con SQL.

## Guía de estudio (pestaña `#guia`)

Basada solo en documentos oficiales: Acuerdos de convocatoria y Anexo técnico CNSC 2026 (etapas, pruebas, mínimos, pesos,
antecedentes), Res. MEN 003842 de 2022 (competencias y requisitos), referentes del MEN (Estándares, Lineamientos y DBA de
Ciencias Naturales; PNEA; Guía 30 y Orientaciones Curriculares de T&I 2022; Competencias TIC 2013) y normas del Gestor
Normativo de Función Pública. A la fecha de creación (14-nov-2026) la CNSC **no** ha publicado la Guía de orientación ni los
ejes temáticos 2026-2027; cuando se publiquen, actualice `scripts/build_guide.py` (y, si cambian los ejes, `build_plan.py`
para los días aún no generados).

**Contenido de estudio por tema.** Cada tema del plan tiene su página `#guia-t-<id-del-tema>` con conceptos clave,
explicaciones con ejemplos, normas resumidas en lenguaje sencillo (versión B: leyes desde cero), trampas frecuentes de examen
y "Puntos clave", más sus fuentes oficiales de referencia. El contenido vive en `content/temas/*.md` (encabezado
`ids:` = ids base de los temas del plan que cubre, `refs:` = ids de documentos de `guia.json`) y `build_guide.py` lo convierte
con `scripts/md_mini.py` a `data/temas.json`, verificando que todo tema del plan (sin el sufijo `-vN` de las vueltas) tenga
contenido. Índice por versión: `#guia-temas`; secciones por eje: `#guia-<eje>`. El encabezado de cada simulacro, cada tema y
el plan (📘) enlazan a la página del tema; los días de repaso enlazan al índice.

## Pruebas E2E

```bash
python3 -m venv ~/.venv-pw && ~/.venv-pw/bin/pip install playwright && ~/.venv-pw/bin/python -m playwright install chromium
~/.venv-pw/bin/python tests/e2e.py <URL> [AAAA-MM-DD]
```
Responde todas las preguntas del día (2 de cada 3 correctas), comprueba selección, retroalimentación inmediata con
explicación, bloqueo de la pregunta, puntaje por tema y total, persistencia al recargar y el plan con el día de hoy
resaltado; guarda `test-A.png` y `test-B.png`.
