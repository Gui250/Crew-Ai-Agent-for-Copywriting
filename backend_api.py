"""
API Backend para AI Marketing Crew
Deploy no Render: https://crew-ai-agent-for-copywriting.onrender.com
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Adiciona o caminho do módulo ao sys.path
project_path = Path(__file__).parent / "projeto_agente" / "src" / "projeto_agente" / "create_crew_project" / "src" / "create_crew_project"
sys.path.insert(0, str(project_path))

# Carrega variáveis de ambiente
load_dotenv(override=False)

# Verifica OPENAI_API_KEY (mas não para a execução, apenas avisa)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    import sys
    print("⚠️ AVISO: OPENAI_API_KEY não encontrada nas variáveis de ambiente!", file=sys.stderr)
    print("⚠️ A API não funcionará sem esta chave. Configure no Render.", file=sys.stderr)
    # Não para a execução aqui, deixa o FastAPI iniciar para mostrar erro mais claro

try:
    from crew import CreateCrewProject
    from crewai import Crew, Process
except ImportError as e:
    import sys
    print(f"❌ ERRO ao importar módulos da crew: {e}", file=sys.stderr)
    print(f"❌ Caminho verificado: {project_path}", file=sys.stderr)
    raise

app = FastAPI(title="AI Marketing Crew API", version="1.0.0")

# Configura CORS para permitir requisições do Streamlit Community Cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.streamlit.app",
        "https://*.streamlit.io",
        "http://localhost:8501",  # Para desenvolvimento local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de requisição
class CopyRequest(BaseModel):
    topic: str
    target_audience: str
    platform: str
    tone: str
    url: Optional[str] = "Nenhuma URL fornecida. Use seu conhecimento geral."
    definicao_do_sistema: Optional[str] = None

class DashboardRequest(BaseModel):
    data_context: str
    topic: Optional[str] = "Análise de Dados de Marketing"
    definicao_do_sistema: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Endpoint de health check"""
    return HealthResponse(
        status="ok",
        message="AI Marketing Crew API está funcionando!"
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """Endpoint de health check"""
    return HealthResponse(
        status="ok",
        message="API está saudável"
    )

@app.post("/api/copywriting")
async def generate_copy(request: CopyRequest):
    """
    Gera copywriting usando a crew de copywriting
    """
    # Verifica OPENAI_API_KEY antes de processar
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY não configurada. Configure esta variável no Render."
        )
    
    try:
        # Prepara os inputs
        inputs = {
            'topic': request.topic,
            'target_audience': request.target_audience,
            'platform': request.platform,
            'tone': request.tone,
            'url': request.url or "Nenhuma URL fornecida. Use seu conhecimento geral."
        }
        
        # Define o sistema se não fornecido
        if not request.definicao_do_sistema:
            inputs['definicao_do_sistema'] = f"""
            Sistema de criação de briefing e copywriting para {request.topic}.
            O briefing deve conter: Perfil do Cliente, Dores/Desejos e Ganchos.
            O copywriting deve seguir o framework PAS.
            """
        else:
            inputs['definicao_do_sistema'] = request.definicao_do_sistema
        
        # Executa a crew
        crew_instance = CreateCrewProject()
        crew_obj = crew_instance.copywriting_crew()
        result = crew_obj.kickoff(inputs=inputs)
        
        # Extrai o resultado
        copy_text = ""
        if hasattr(result, 'tasks_output') and result.tasks_output:
            for task_output in reversed(result.tasks_output):
                if task_output and isinstance(task_output, str):
                    copy_text = task_output
                    break
        
        if not copy_text:
            copy_text = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        return {
            "success": True,
            "result": copy_text,
            "raw": str(result.raw) if hasattr(result, 'raw') else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar copy: {str(e)}"
        )

@app.post("/api/dashboard")
async def generate_dashboard(request: DashboardRequest):
    """
    Gera código de dashboard Streamlit usando a crew de BI
    """
    # Verifica OPENAI_API_KEY antes de processar
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY não configurada. Configure esta variável no Render."
        )
    
    try:
        # Prepara os inputs
        inputs = {
            'topic': request.topic or 'Análise de Dados de Marketing',
            'data_context': request.data_context
        }
        
        # Define o sistema se não fornecido
        if not request.definicao_do_sistema:
            inputs['definicao_do_sistema'] = """
            Você é um Data Scientist Senior Especialista em Streamlit.
            Crie um script Python COMPLETO usando 'streamlit' para gerar um dashboard.
            - Use st.columns para métricas (KPIs).
            - Use st.bar_chart ou st.line_chart para visualizações.
            - O código deve ser executável.
            """
        else:
            inputs['definicao_do_sistema'] = request.definicao_do_sistema
        
        # Executa a crew
        crew_instance = CreateCrewProject()
        crew_obj = crew_instance.dashboard_crew()
        result = crew_obj.kickoff(inputs=inputs)
        
        # Extrai o resultado
        raw_result = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        return {
            "success": True,
            "result": raw_result,
            "raw": raw_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar dashboard: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Verifica OPENAI_API_KEY antes de iniciar
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERRO: OPENAI_API_KEY não encontrada!", file=sys.stderr)
        print("❌ Configure esta variável no Render: Settings > Environment Variables", file=sys.stderr)
        sys.exit(1)
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Iniciando servidor na porta {port}...", file=sys.stderr)
    print(f"✅ OPENAI_API_KEY configurada: {'Sim' if os.getenv('OPENAI_API_KEY') else 'Não'}", file=sys.stderr)
    
    uvicorn.run(app, host="0.0.0.0", port=port)

