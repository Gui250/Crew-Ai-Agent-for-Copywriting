#!/bin/bash
# Script de build para o Render
set -e

echo "🔧 Atualizando pip..."
pip install --upgrade pip

echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "✅ Build concluído!"

