# 🔧 Como Configurar Variáveis de Ambiente no Deploy

## ⚠️ Erro: "OPENAI_API_KEY is required"

Se você está vendo este erro, significa que a variável de ambiente `OPENAI_API_KEY` não está configurada na plataforma de deploy.

## 🚀 Solução Rápida por Plataforma

### Railway

1. Acesse o dashboard do Railway: https://railway.app
2. Selecione seu projeto
3. Vá em **"Variables"** (ou **"Settings"** > **"Variables"**)
4. Clique em **"+ New Variable"**
5. Adicione:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
6. Clique em **"Add"**
7. A aplicação será reiniciada automaticamente

**Via CLI:**
```bash
railway variables set OPENAI_API_KEY=sk-sua-chave-aqui
```

### Render

1. Acesse o dashboard do Render: https://render.com
2. Selecione seu serviço (Web Service)
3. Vá em **"Environment"** no menu lateral
4. Na seção **"Environment Variables"**, clique em **"Add Environment Variable"**
5. Adicione:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
6. Clique em **"Save Changes"**
7. O serviço será reiniciado automaticamente

### Heroku

1. Acesse o dashboard do Heroku: https://dashboard.heroku.com
2. Selecione seu app
3. Vá em **"Settings"**
4. Role até **"Config Vars"**
5. Clique em **"Reveal Config Vars"**
6. Adicione:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
7. Clique em **"Add"**

**Via CLI:**
```bash
heroku config:set OPENAI_API_KEY=sk-sua-chave-aqui
```

### Fly.io

1. Acesse o dashboard do Fly.io: https://fly.io
2. Selecione seu app
3. Vá em **"Secrets"**
4. Adicione:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
5. Clique em **"Set Secret"**

**Via CLI:**
```bash
fly secrets set OPENAI_API_KEY=sk-sua-chave-aqui
```

### Vercel

1. Acesse o dashboard do Vercel: https://vercel.com
2. Selecione seu projeto
3. Vá em **"Settings"** > **"Environment Variables"**
4. Adicione:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
5. Selecione os ambientes (Production, Preview, Development)
6. Clique em **"Save"**
7. Faça um novo deploy

### DigitalOcean App Platform

1. Acesse o dashboard do DigitalOcean
2. Selecione seu app
3. Vá em **"Settings"** > **"App-Level Environment Variables"**
4. Clique em **"Edit"**
5. Adicione:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
6. Clique em **"Save"**
7. O app será reiniciado

### AWS (Elastic Beanstalk, ECS, etc.)

**Elastic Beanstalk:**
1. Acesse o console AWS
2. Vá em Elastic Beanstalk > Seu ambiente
3. Clique em **"Configuration"**
4. Role até **"Software"** > **"Environment properties"**
5. Adicione: `OPENAI_API_KEY` = `sk-sua-chave-aqui`
6. Clique em **"Apply"**

**ECS (via Task Definition):**
- Adicione a variável na definição da task:
```json
{
  "environment": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-sua-chave-aqui"
    }
  ]
}
```

### Google Cloud Platform (Cloud Run)

1. Acesse o console GCP
2. Vá em Cloud Run > Seu serviço
3. Clique em **"Edit & Deploy New Revision"**
4. Vá em **"Variables & Secrets"**
5. Clique em **"Add Variable"**
6. Adicione:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
7. Clique em **"Deploy"**

**Via CLI:**
```bash
gcloud run services update seu-servico \
  --set-env-vars OPENAI_API_KEY=sk-sua-chave-aqui
```

### Azure (App Service)

1. Acesse o portal Azure
2. Vá em App Services > Seu app
3. No menu lateral, vá em **"Configuration"**
4. Na aba **"Application settings"**, clique em **"+ New application setting"**
5. Adicione:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-sua-chave-aqui`
6. Clique em **"OK"** e depois em **"Save"**

## 🔐 Variável Opcional: AGENTOPS_API_KEY

Se você quiser usar monitoramento com AgentOps (opcional), adicione também:

- **Name:** `AGENTOPS_API_KEY`
- **Value:** `sua-chave-agentops`

## ✅ Verificação

Após configurar, verifique se está funcionando:

1. Acesse sua aplicação no navegador
2. Se o erro desapareceu, está funcionando!
3. Se ainda aparecer o erro:
   - Verifique se o nome da variável está correto (case-sensitive)
   - Verifique se você salvou as alterações
   - Aguarde alguns segundos para o serviço reiniciar
   - Verifique os logs da aplicação

## 🐛 Troubleshooting

### Erro persiste após configurar

1. **Verifique o nome:** Deve ser exatamente `OPENAI_API_KEY` (maiúsculas)
2. **Reinicie o serviço:** Algumas plataformas precisam de restart manual
3. **Verifique os logs:** Veja se há outros erros nos logs da aplicação
4. **Teste localmente:** Certifique-se de que funciona com `.env` local

### Como obter a chave da OpenAI

1. Acesse: https://platform.openai.com/api-keys
2. Faça login na sua conta
3. Clique em **"Create new secret key"**
4. Copie a chave (ela só aparece uma vez!)
5. Cole no campo de valor da variável de ambiente

## 📝 Nota de Segurança

⚠️ **NUNCA** commite sua chave da API no código ou no Git!
- Use sempre variáveis de ambiente
- O arquivo `.env` já está no `.gitignore`
- Nunca compartilhe sua chave publicamente

