from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys
import logging
from pathlib import Path

# Configura logging para suprimir erros de eventos do CrewAI (não críticos)
# Nota: Erros "Expecting value: line 1 column 1" em handlers de eventos do CrewAI
# são conhecidos e geralmente não afetam a funcionalidade principal
logging.getLogger("crewai").setLevel(logging.WARNING)
logging.getLogger("crewai.events").setLevel(logging.ERROR)
logging.getLogger("crewai.events.bus").setLevel(logging.CRITICAL)  # Suprime erros do EventsBus

# Suprime warnings de eventos do CrewAI que não afetam a funcionalidade
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="crewai")

# Garante que o projeto esteja no path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "projeto_agente" / "src"))

try:
    from projeto_agente.create_crew_project import CreateCrewProject
except Exception as e:
    print("❌ ERRO IMPORTANDO CREW:", e)
    raise

app = FastAPI(title="AI Marketing Crew API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CopyRequest(BaseModel):
    topic: str
    target_audience: str
    platform: str
    tone: str
    url: Optional[str] = None
    definicao_do_sistema: Optional[str] = None


@app.get("/")
def root():
    return {"status": "ok", "message": "API online"}

@app.post("/api/copywriting")
async def generate_copy(request: CopyRequest):

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY não configurada no Render.")

    try:
        crew_instance = CreateCrewProject()
        crew = crew_instance.copywriting_crew()
        
        # Executa a crew
        # Nota: Erros de eventos do CrewAI (como "Expecting value: line 1 column 1")
        # são não-críticos e geralmente não impedem a execução
        result = crew.kickoff(inputs=request.dict())
        
        text = result.final_output if hasattr(result, "final_output") else str(result)

        return {"success": True, "result": text}

    except Exception as e:
        error_msg = str(e)
        # Erros de eventos do CrewAI são não-críticos, mas se ocorrerem durante kickoff,
        # podem indicar um problema real. Logamos o erro completo para debug.
        import traceback
        print(f"❌ Erro ao gerar copywriting: {error_msg}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        
        # Se for apenas erro de eventos JSON, tenta retornar uma mensagem mais amigável
        if "expecting value" in error_msg.lower() and "line 1 column 1" in error_msg.lower():
            raise HTTPException(
                500, 
                "Erro ao processar eventos internos do CrewAI. Isso geralmente não afeta o resultado. "
                "Se o problema persistir, verifique os logs do servidor."
            )
        raise HTTPException(500, f"Erro ao gerar copywriting: {error_msg}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
