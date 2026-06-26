#!/usr/bin/env bash
# Lleva contador de interacciones en .vault-meta/interaction-count.txt.
# Emite SAVE_REMINDER cada 10 para que Claude guarde contexto al vault.
COUNT_FILE=".vault-meta/interaction-count.txt"
count=0
[ -f "$COUNT_FILE" ] && count=$(cat "$COUNT_FILE" 2>/dev/null || echo 0)
count=$((count + 1))
echo "$count" > "$COUNT_FILE"
if [ $((count % 30)) -eq 0 ]; then
  echo "⚠️ SAVE_REMINDER — ACCIÓN OBLIGATORIA ANTES DE RESPONDER: Ejecutá /save AHORA. Guardá esta sesión en wiki/references/ como nota estructurada (frontmatter type: reference). Hacelo como PRIMERA acción del próximo turno, antes de responder al usuario. No es opcional ni postergable."
fi
