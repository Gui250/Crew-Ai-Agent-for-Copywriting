# 🔗 Frontend (Streamlit) Consumindo Backend (Render)

## ✅ Configuração Atual

O frontend Streamlit agora está configurado para consumir a API do backend hospedado no Render:

**Backend URL:** `https://crew-ai-agent-for-copywriting.onrender.com`

## 📋 Como Funciona

### Arquitetura

```
┌─────────────────────┐         HTTP POST         ┌─────────────────────┐
│                     │   ────────────────────>   │                     │
│  Streamlit Frontend │                           │  Backend API (FastAPI) │
│  (Streamlit Cloud)  │   <────────────────────   │  (Render)            │
│                     │         JSON Response      │                     │
└─────────────────────┘                            └─────────────────────┘
```

### Endpoints Utilizados

1. **`POST /api/copywriting`** - Gera copywriting
   - Payload: `{topic, target_audience, platform, tone, url, definicao_do_sistema}`
   - Response: `{success, result, raw}`

2. **`POST /api/dashboard`** - Gera código de dashboard
   - Payload: `{data_context, topic, definicao_do_sistema}`
   - Response: `{success, result, raw}`

3. **`GET /health`** - Health check (opcional)

## 🔧 Configuração

### Variável de Ambiente (Opcional)

Você pode configurar a URL do backend via variável de ambiente:

```bash
BACKEND_API_URL=https://crew-ai-agent-for-copywriting.onrender.com
```

**No Streamlit Community Cloud:**
1. Acesse seu app no Streamlit Cloud
2. Vá em "Settings" > "Secrets"
3. Adicione:
   ```toml
   BACKEND_API_URL = "https://crew-ai-agent-for-copywriting.onrender.com"
   ```

Se não configurar, o app usará a URL padrão: `https://crew-ai-agent-for-copywriting.onrender.com`

## 🚀 Deploy do Frontend no Streamlit Cloud

1. **Conecte seu repositório:**
   - Acesse: https://share.streamlit.io
   - Conecte seu repositório GitHub

2. **Configure o app:**
   - **Main file path:** `app.py`
   - **Python version:** 3.11

3. **Variáveis de Ambiente (Opcional):**
   - `BACKEND_API_URL` - URL do backend (padrão já configurado)

4. **Deploy:**
   - Clique em "Deploy"
   - Aguarde o build

## ✅ Vantagens desta Arquitetura

1. **Separação de Responsabilidades:**
   - Frontend: Interface do usuário (Streamlit)
   - Backend: Processamento pesado (CrewAI)

2. **Escalabilidade:**
   - Backend pode ser escalado independentemente
   - Múltiplos frontends podem usar o mesmo backend

3. **Custos:**
   - Streamlit Cloud: Gratuito
   - Render: Plano gratuito disponível

4. **Manutenção:**
   - Atualizações no backend não afetam o frontend
   - Fácil de debugar e monitorar

## 🐛 Troubleshooting

### Erro: "Não foi possível conectar ao backend"

1. **Verifique se o backend está online:**
   - Acesse: https://crew-ai-agent-for-copywriting.onrender.com/health
   - Deve retornar: `{"status":"ok","message":"API está saudável"}`

2. **Verifique a URL:**
   - Confirme que a URL está correta no código
   - Verifique se não há barra final duplicada

3. **CORS:**
   - O backend já está configurado para aceitar requisições do Streamlit Cloud
   - Domínios permitidos: `*.streamlit.app`, `*.streamlit.io`

### Erro: "Timeout"

- O processamento pode demorar (até 5 minutos)
- Tente novamente ou use dados menores
- Verifique os logs do backend no Render

### Erro: "Erro do backend: ..."

- Verifique os logs do backend no Render
- Confirme que `OPENAI_API_KEY` está configurada no backend
- Verifique se há erros na requisição

## 📝 Notas

- O timeout está configurado para 5 minutos (300 segundos)
- O frontend não precisa mais da `OPENAI_API_KEY` (apenas o backend precisa)
- Todas as requisições são feitas via HTTP POST com JSON

## 🔄 Atualizar URL do Backend

Se você mudar a URL do backend:

1. **Via código:** Edite `app.py` linha ~18:
   ```python
   BACKEND_URL = os.getenv('BACKEND_API_URL', 'https://sua-nova-url.onrender.com')
   ```

2. **Via variável de ambiente:** Configure `BACKEND_API_URL` no Streamlit Cloud

