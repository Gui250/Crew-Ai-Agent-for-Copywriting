# 🚀 Deploy do Backend no Render

## ✅ Configuração Correta para Render

### Opção 1: Usando render.yaml (Recomendado)

O arquivo `render_backend.yaml` já está configurado. Basta:

1. **Conectar o repositório no Render:**
   - Acesse: https://render.com
   - Clique em "New" > "Blueprint"
   - Conecte seu repositório GitHub
   - O Render detectará automaticamente o `render_backend.yaml`

2. **Ou criar manualmente:**
   - Acesse: https://render.com
   - Clique em "New" > "Web Service"
   - Conecte seu repositório
   - Configure:
     - **Name:** `ai-marketing-crew-api`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements_backend.txt`
     - **Start Command:** `python backend_api.py`
     - **Health Check Path:** `/health`

3. **Configurar Variáveis de Ambiente:**
   - Na seção "Environment Variables", adicione:
     - `OPENAI_API_KEY` = `sk-sua-chave-aqui`
     - `AGENTOPS_API_KEY` = `sua-chave-opcional` (opcional)
     - `PORT` = `8000` (opcional, Render define automaticamente)

### Opção 2: Usando Docker

Se preferir usar Docker:

1. **Configure o Render:**
   - **Environment:** `Docker`
   - **Dockerfile Path:** `Dockerfile.backend`
   - **Docker Context:** `.`

2. **O Dockerfile.backend já está configurado!**

## 📋 Arquivos Necessários

Certifique-se de que estes arquivos estão no repositório:

- ✅ `backend_api.py` - API principal
- ✅ `requirements_backend.txt` - Dependências Python
- ✅ `render_backend.yaml` - Configuração do Render
- ✅ `projeto_agente/` - Código da crew (deve estar no repositório)

## 🔧 Start Command Correto

**❌ ERRADO (caminho local do Mac):**
```
python /Users/guilhermemoreno/Desktop/crew/projeto_agente/src/projeto_agente/create_crew_project/src/create_crew_project/main.py
```

**✅ CORRETO:**
```
python backend_api.py
```

O Render executa os comandos na raiz do repositório, então use caminhos relativos.

## 🐛 Troubleshooting

### Erro: "Module not found"

**Solução:**
1. Verifique se `requirements_backend.txt` está no repositório
2. Confirme que o Build Command está correto: `pip install -r requirements_backend.txt`
3. Verifique os logs do build no Render

### Erro: "OPENAI_API_KEY is required"

**Solução:**
1. Acesse o dashboard do Render
2. Vá em "Environment" > "Environment Variables"
3. Adicione `OPENAI_API_KEY` com sua chave da OpenAI

### Erro: "File not found" ou caminho incorreto

**Solução:**
- Use apenas caminhos relativos (sem `/Users/...`)
- O Render executa na raiz do repositório
- Certifique-se de que todos os arquivos necessários estão no repositório

### Erro: "Port already in use"

**Solução:**
- O Render define automaticamente a variável `PORT`
- O código já está configurado para usar `os.getenv("PORT", 8000)`
- Não precisa configurar manualmente

## ✅ Verificação

Após o deploy, teste:

1. **Health Check:**
   ```
   https://seu-app.onrender.com/health
   ```
   Deve retornar: `{"status":"ok","message":"API está saudável"}`

2. **Root:**
   ```
   https://seu-app.onrender.com/
   ```
   Deve retornar: `{"status":"ok","message":"AI Marketing Crew API está funcionando!"}`

## 📝 Notas Importantes

1. **Primeiro Deploy:** Pode demorar 5-10 minutos
2. **Sleep Mode:** No plano gratuito, o serviço "dorme" após 15 minutos de inatividade
3. **Cold Start:** Após dormir, o primeiro request pode demorar 30-60 segundos
4. **Timeout:** Requests podem demorar até 5 minutos (processamento da crew)

## 🔄 Atualizar Deploy

Após fazer push para o GitHub:
- O Render detecta automaticamente e faz novo deploy
- Ou você pode clicar em "Manual Deploy" no dashboard

