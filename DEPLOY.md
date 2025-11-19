# 🚀 Guia de Deploy - AI Marketing Crew

Este guia explica como fazer deploy da aplicação AI Marketing Crew em diferentes plataformas.

## 📋 Pré-requisitos

1. **Variáveis de Ambiente Necessárias:**
   - `OPENAI_API_KEY` - Obrigatória (chave da API da OpenAI)
   - `AGENTOPS_API_KEY` - Opcional (para monitoramento)

2. **Arquivo .env:**
   Crie um arquivo `.env` na raiz do projeto com:
   ```
   OPENAI_API_KEY=sk-sua-chave-aqui
   AGENTOPS_API_KEY=sua-chave-opcional
   ```

## 🐳 Deploy com Docker (Local)

### 1. Build e execução com Docker Compose:

```bash
# Build e iniciar
docker-compose up --build

# Executar em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

A aplicação estará disponível em: `http://localhost:8501`

### 2. Build e execução manual com Docker:

```bash
# Build da imagem
docker build -t ai-marketing-crew .

# Executar container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-sua-chave \
  -v $(pwd)/output:/app/output \
  ai-marketing-crew
```

## ☁️ Deploy em Plataformas Cloud

### Railway

1. **Instalação:**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy:**
   ```bash
   railway init
   railway up
   ```

3. **Configurar Variáveis:**
   - Acesse o dashboard do Railway
   - Vá em "Variables" e adicione:
     - `OPENAI_API_KEY`
     - `AGENTOPS_API_KEY` (opcional)

4. **O arquivo `railway.json` já está configurado!**

### Render

1. **Via Dashboard:**
   - Acesse [render.com](https://render.com)
   - Clique em "New" > "Web Service"
   - Conecte seu repositório GitHub
   - Selecione o repositório e branch
   - Render detectará automaticamente o `render.yaml`

2. **Configurar Variáveis:**
   - Na seção "Environment Variables", adicione:
     - `OPENAI_API_KEY`
     - `AGENTOPS_API_KEY` (opcional)

3. **Deploy:**
   - Clique em "Create Web Service"
   - O deploy será automático

### Heroku

1. **Instalação:**
   ```bash
   heroku login
   heroku create ai-marketing-crew
   ```

2. **Configurar Variáveis:**
   ```bash
   heroku config:set OPENAI_API_KEY=sk-sua-chave
   heroku config:set AGENTOPS_API_KEY=sua-chave-opcional
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

4. **Criar arquivo `Procfile`:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

### Fly.io

1. **Instalação:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Inicializar:**
   ```bash
   fly launch
   ```

3. **Configurar Variáveis:**
   ```bash
   fly secrets set OPENAI_API_KEY=sk-sua-chave
   fly secrets set AGENTOPS_API_KEY=sua-chave-opcional
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

## 🔧 Configurações Adicionais

### Porta Customizada

Para usar uma porta diferente, modifique o `Dockerfile` ou use variáveis de ambiente:

```bash
# Docker
docker run -p 8080:8501 -e STREAMLIT_SERVER_PORT=8501 ai-marketing-crew

# Docker Compose (edite docker-compose.yml)
ports:
  - "8080:8501"
```

### Variáveis de Ambiente no Deploy

Todas as plataformas permitem configurar variáveis de ambiente via dashboard ou CLI. Certifique-se de adicionar:

- `OPENAI_API_KEY` (obrigatória)
- `AGENTOPS_API_KEY` (opcional)

## 📝 Notas Importantes

1. **Custos:** A aplicação usa a API da OpenAI, que tem custos por uso. Monitore seu uso no dashboard da OpenAI.

2. **Limites de Rate:** Algumas plataformas gratuitas têm limites de recursos. Considere upgrade para produção.

3. **Segurança:** Nunca commite o arquivo `.env` no Git. Ele já está no `.gitignore`.

4. **Logs:** Para debug, verifique os logs da aplicação na plataforma escolhida.

## 🐛 Troubleshooting

### ⚠️ Erro: "OPENAI_API_KEY is required" ou "Error importing native provider: OPENAI_API_KEY is required"

**Este é o erro mais comum após o deploy!**

**Solução Rápida:**
1. Acesse o dashboard da sua plataforma (Railway, Render, Heroku, etc.)
2. Vá nas configurações de **Variáveis de Ambiente** ou **Environment Variables**
3. Adicione a variável:
   - **Nome:** `OPENAI_API_KEY`
   - **Valor:** `sk-sua-chave-da-openai` (obtenha em https://platform.openai.com/api-keys)
4. Salve e aguarde o serviço reiniciar

**📖 Guia Completo:** Veja `SOLUCAO_RAPIDA.md` para instruções passo a passo por plataforma.

### Erro: "OPENAI_API_KEY not found"
- Verifique se a variável está configurada na plataforma
- Confirme que o nome está correto (case-sensitive: `OPENAI_API_KEY` em maiúsculas)
- Verifique se você salvou as alterações
- Aguarde alguns segundos para o serviço reiniciar

### Erro: "Port already in use"
- Altere a porta no `docker-compose.yml` ou use `-p` no Docker

### Erro: "Module not found"
- Verifique se todas as dependências estão no `requirements.txt`
- Execute `pip install -r requirements.txt` localmente para testar

## 📚 Recursos Adicionais

- [Documentação CrewAI](https://docs.crewai.com)
- [Documentação Streamlit](https://docs.streamlit.io)
- [Documentação Docker](https://docs.docker.com)

