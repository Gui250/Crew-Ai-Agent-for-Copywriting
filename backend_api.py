from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path
import sys

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
        result = crew.kickoff(inputs=request.dict())

        text = result.final_output if hasattr(result, "final_output") else str(result)

        return {"success": True, "result": text}

    except Exception as e:
        raise HTTPException(500, f"Erro ao gerar copywriting: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
