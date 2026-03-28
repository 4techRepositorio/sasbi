#!/usr/bin/env bash
set -e

echo "Validando se o ticket possui seções mínimas..."

FILE="$1"

grep -q "## Objetivo" "$FILE"
grep -q "## Subtarefas" "$FILE"
grep -q "## Critérios de aceite" "$FILE"

echo "Plano válido"
