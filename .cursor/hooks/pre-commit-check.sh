#!/usr/bin/env bash
set -e

echo "Rodando validações básicas..."

if [ -f "apps/api/requirements.txt" ]; then
  echo "Backend detectado"
fi

if [ -f "apps/web/package.json" ]; then
  echo "Frontend detectado"
fi

echo "Validação concluída"
