# 🔧 Corrigir Erro: ModuleNotFoundError: No module named 'fastapi'

## ❌ Problema

O Render não está instalando as dependências antes de executar o código.

## ✅ Soluções

### Opção 1: Configurar Manualmente no Dashboard (Recomendado)

1. **Acesse o dashboard do Render:**
   - Vá em: https://dashboard.render.com
   - Selecione seu serviço

2. **Vá em "Settings" > "Build & Deploy":**

3. **Configure:**
   - **Build Command:** 
     ```
     pip install --upgrade pip && pip install -r requirements_backend.txt
     ```
   - **Start Command:**
     ```
     python backend_api.py
     ```

4. **Salve e faça um novo deploy**

### Opção 2: Usar requirements.txt na Raiz

O Render pode estar procurando por `requirements.txt` ao invés de `requirements_backend.txt`.

**Solução rápida:**
```bash
# Copiar o arquivo
cp requirements_backend.txt requirements.txt
```

Ou criar um link simbólico (se o Render suportar).

### Opção 3: Verificar se o arquivo está no repositório

Certifique-se de que `requirements_backend.txt` está commitado:

```bash
git add requirements_backend.txt
git commit -m "Add requirements_backend.txt"
git push
```

### Opção 4: Usar Docker (Alternativa)

Se continuar com problemas, use Docker:

1. **No Render, mude para Docker:**
   - **Environment:** `Docker`
   - **Dockerfile Path:** `Dockerfile.backend`

2. **O Dockerfile.backend já está configurado!**

## 🔍 Verificar

Após configurar, verifique os logs do build no Render. Você deve ver:

```
Collecting fastapi==0.104.1
  Downloading fastapi-0.104.1-py3-none-any.whl
Successfully installed fastapi-0.104.1
```

## 📝 Checklist

- [ ] Build Command configurado no Render
- [ ] `requirements_backend.txt` está no repositório
- [ ] Arquivo foi commitado e enviado ao GitHub
- [ ] Variável `OPENAI_API_KEY` configurada
- [ ] Novo deploy foi iniciado após as mudanças

