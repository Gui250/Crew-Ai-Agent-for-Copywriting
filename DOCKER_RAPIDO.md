# ⚡ Mudar para Docker no Render - Guia Rápido

## 🎯 5 Passos Simples

### 1️⃣ Acesse o Render
https://dashboard.render.com → Selecione seu serviço

### 2️⃣ Vá em Settings
Menu lateral → **"Settings"**

### 3️⃣ Mude Environment
Na seção **"Build & Deploy"**, encontre:
```
Environment: Python 3
```
**Mude para:**
```
Environment: Docker
```

### 4️⃣ Configure Docker
Preencha:
- **Dockerfile Path:** `Dockerfile.backend`
- **Docker Context:** `.` (ponto)

### 5️⃣ Salve e Deploy
- Clique em **"Save Changes"**
- Vá em **"Manual Deploy"** → **"Deploy latest commit"**

## ✅ Pronto!

Aguarde 5-10 minutos para o build. Depois teste:
```
https://crew-ai-agent-for-copywriting.onrender.com/health
```

## 📸 Onde Está Cada Coisa?

```
Render Dashboard
├── Seu Serviço (ai-marketing-crew-api)
    ├── Settings ← Clique aqui
    │   ├── Build & Deploy
    │   │   ├── Environment: [Python 3] → Mude para Docker
    │   │   ├── Dockerfile Path: [Dockerfile.backend]
    │   │   └── Docker Context: [.]
    │   └── Environment Variables
    │       └── OPENAI_API_KEY ← Verifique se está configurado
    └── Manual Deploy ← Clique aqui após salvar
```

## 🆘 Precisa de Ajuda?

Veja o guia completo: `MUDAR_PARA_DOCKER.md`

