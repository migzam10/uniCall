#!/usr/bin/env bash
# Prueba manual rápida del backend: crea el entorno, instala dependencias,
# corre migraciones y ejecuta toda la batería de pruebas automatizadas.
#
# Uso:
#   cd backend
#   chmod +x test_manual.sh
#   ./test_manual.sh
set -e

echo "== 1. Creando entorno virtual =="
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

echo "== 2. Instalando dependencias =="
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "== 3. Verificando espeak-ng (necesario para TTS) =="
if ! command -v espeak-ng &> /dev/null; then
  echo "AVISO: espeak-ng no está instalado."
  echo "  Linux/WSL: sudo apt-get install espeak-ng"
  echo "  macOS:     brew install espeak-ng"
  echo "Continuando de todos modos (las pruebas de TTS fallarán sin esto)..."
fi

echo "== 4. Preparando base de datos de prueba (SQLite) =="
cp -n .env.example .env || true
if grep -q "^DATABASE_URL=" .env; then
  sed -i.bak 's#^DATABASE_URL=.*#DATABASE_URL=sqlite+aiosqlite:///./dev.db#' .env && rm -f .env.bak
fi
rm -f dev.db test.db
alembic upgrade head

echo "== 5. Corriendo toda la batería de pruebas automatizadas =="
pytest tests/ -v

echo ""
echo "== Listo =="
echo "Para levantar el servidor y explorar la API interactivamente:"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo "  Abre http://localhost:8000/docs"
