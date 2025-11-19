# ⚡ Solução Rápida: ModuleNotFoundError: No module named 'fastapi'

## 🎯 O Problema

O Render não está instalando as dependências antes de executar o código.

## ✅ Solução Imediata

### No Dashboard do Render:

1. **Acesse:** https://dashboard.render.com
2. **Selecione seu serviço** (ai-marketing-crew-api)
3. **Vá em "Settings" > "Build & Deploy"**
4. **Configure:**

   **Build Command:**
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```

   **Start Command:**
   ```
   python backend_api.py
   ```

5. **Clique em "Save Changes"**
6. **Vá em "Manual Deploy" > "Deploy latest commit"**

## 📋 Arquivos Criados

✅ `requirements.txt` - Cópia do requirements_backend.txt (Render procura por este nome)
✅ `Procfile` - Define o comando de start
✅ `runtime.txt` - Especifica Python 3.11
✅ `render_backend.yaml` - Atualizado

## 🔍 Verificar se Funcionou

Após o deploy, verifique os logs. Você deve ver:

```
Collecting fastapi==0.104.1
  Downloading fastapi-0.104.1-py3-none-any.whl
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

## ⚠️ Importante

- Certifique-se de que `requirements.txt` está commitado no repositório
- Faça commit e push dos novos arquivos:
  ```bash
  git add requirements.txt Procfile runtime.txt
  git commit -m "Fix Render build configuration"
  git push
  ```

## 🆘 Ainda com Problemas?

1. **Verifique os logs do build** no Render
2. **Confirme que o Build Command está correto**
3. **Tente usar Docker** (mude para Docker no Render e use Dockerfile.backend)

