# ⚡ Solução Rápida: Erro OPENAI_API_KEY

## 🎯 O Problema

Você está vendo: `Error importing native provider: OPENAI_API_KEY is required`

## ✅ Solução (2 minutos)

### Se você fez deploy no **Railway**:

1. Acesse: https://railway.app
2. Clique no seu projeto
3. Vá em **"Variables"** (menu lateral)
4. Clique em **"+ New Variable"**
5. Digite:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-da-openai`
6. Clique em **"Add"**
7. ✅ Pronto! A aplicação reiniciará automaticamente

### Se você fez deploy no **Render**:

1. Acesse: https://render.com
2. Clique no seu serviço (Web Service)
3. Vá em **"Environment"** (menu lateral)
4. Role até **"Environment Variables"**
5. Clique em **"Add Environment Variable"**
6. Digite:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-da-openai`
7. Clique em **"Save Changes"**
8. ✅ Pronto! O serviço reiniciará automaticamente

### Se você fez deploy no **Heroku**:

1. Acesse: https://dashboard.heroku.com
2. Selecione seu app
3. Vá em **"Settings"**
4. Role até **"Config Vars"**
5. Clique em **"Reveal Config Vars"**
6. Clique em **"Add"**
7. Digite:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-da-openai`
8. Clique em **"Add"**
9. ✅ Pronto!

**Ou via terminal:**

```bash
heroku config:set OPENAI_API_KEY=sk-sua-chave-da-openai
```

## 🔑 Como Obter a Chave da OpenAI

1. Acesse: https://platform.openai.com/api-keys
2. Faça login
3. Clique em **"Create new secret key"**
4. Copie a chave (ela começa com `sk-`)
5. Cole no campo de valor da variável de ambiente

## ⚠️ Importante

- O nome da variável deve ser exatamente: `OPENAI_API_KEY` (maiúsculas)
- Após adicionar, aguarde alguns segundos para o serviço reiniciar
- Se ainda não funcionar, verifique os logs da aplicação

## 📚 Mais Detalhes

Para instruções detalhadas de outras plataformas, veja: `CONFIGURAR_VARIAVEIS.md`
