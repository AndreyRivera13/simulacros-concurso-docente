#!/usr/bin/env bash
# Trabajo diario: agrega el siguiente día pendiente de cada versión, valida, prueba y publica.
# Requisitos: python3; git con permiso de push al repo; para --llm, variables LLM_API_KEY/LLM_BASE_URL/LLM_MODEL.
# Si el borrador drafts/<V>/<FECHA>.txt ya existe (p. ej. lo escribió un agente), no se llama al LLM.
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only
for V in A B; do
  D=$(python3 scripts/next_day.py | awk -v v="$V" '$1==v{print $2}')
  [ "$D" = "plan" ] && { echo "$V: plan completo"; continue; }
  if [ ! -f "drafts/$V/$D.txt" ]; then python3 scripts/next_day.py "$V" "$D" --llm; fi
  python3 scripts/build_day.py "$V" "$D"        # valida formato, 20 preguntas/tema, baraja y actualiza index.json
  ADDED="${ADDED:-} $V:$D"
done
git add data drafts
git commit -m "Simulacro diario:${ADDED:- (sin cambios)}" || { echo "Nada que publicar"; exit 0; }
git push                                         # GitHub Pages redepliega automáticamente
echo "Publicado:${ADDED:-}"
