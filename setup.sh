#!/bin/bash

echo "=== INICIANDO SETUP DEL PROYECTO ==="

# Detectar el comando Python válido
if command -v python &>/dev/null; then
    PYTHON_CMD=python
elif command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
else
    echo "[ERROR] No se encontró Python instalado."
fi

# 1. Creando entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "[INFO] Creando entorno virtual 'venv'"
    $PYTHON_CMD -m venv venv
else
    echo "[INFO] Entorno virtual 'venv' ya existe."
fi

# 2. Activando entorno virtual
echo "[INFO] Activando entorno virtual..."
# shellcheck source=/dev/null
source venv/bin/activate

# 3. Instalar dependencias de requirements.txt
if [ -f "requirements.txt" ]; then
    echo "[INFO] Instalando dependencias de requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[ADVERTENCIA] No se encontró requirements.txt. Omitiendo."
fi

# 4. Mover hooks a .git/hooks/ y dar permisos
HOOKS_DIR="hooks"
GIT_HOOKS_DIR=".git/hooks"

echo "[INFO] Instalando hooks personalizados..."

for hook in pre-commit pre-push commit-msg; do
    if [ -f "$HOOKS_DIR/$hook" ]; then
        cp "$HOOKS_DIR/$hook" "$GIT_HOOKS_DIR/$hook"
        chmod +x "$GIT_HOOKS_DIR/$hook"
        echo "[OK] Hook $hook instalado."
    else
        echo "[ADVERTENCIA] No se encontró $HOOKS_DIR/$hook, omitiendo."
    fi
done

echo "=== SETUP FINALIZADO ==="