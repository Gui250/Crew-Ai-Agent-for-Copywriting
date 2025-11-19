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

# Cria um filtro customizado para suprimir erros de eventos do CrewAI
class CrewAIEventsFilter(logging.Filter):
    def filter(self, record):
        # Suprime mensagens relacionadas a erros de eventos do CrewAI
        message = str(record.getMessage())
        if any(keyword in message for keyword in [
            "CrewAIEventsBus",
            "on_agent_logs_execution",
            "Expecting value: line 1 column 1",
            "JSONDecodeError"
        ]):
            return False  # Não registra esta mensagem
        return True  # Registra outras mensagens

# Aplica o filtro aos loggers do CrewAI
crewai_logger = logging.getLogger("crewai")
crewai_logger.setLevel(logging.WARNING)
crewai_logger.addFilter(CrewAIEventsFilter())

events_logger = logging.getLogger("crewai.events")
events_logger.setLevel(logging.CRITICAL)
events_logger.addFilter(CrewAIEventsFilter())

bus_logger = logging.getLogger("crewai.events.bus")
bus_logger.setLevel(logging.CRITICAL)
bus_logger.addFilter(CrewAIEventsFilter())

# Suprime warnings de eventos do CrewAI que não afetam a funcionalidade
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="crewai")
warnings.filterwarnings("ignore", message=".*Expecting value.*")
warnings.filterwarnings("ignore", message=".*JSONDecodeError.*")

# Patch para suprimir erros de JSON parsing no EventsBus do CrewAI
from io import StringIO
import re

class FilteredIO:
    """IO wrapper que filtra mensagens específicas do CrewAI EventsBus de forma mais agressiva"""
    def __init__(self, original_io):
        self.original_io = original_io
        self.buffer = []
    
    def write(self, text):
        # Filtra mensagens relacionadas a erros de eventos do CrewAI
        if text:
            # Padrões mais abrangentes a filtrar
            patterns_to_filter = [
                r'\[CrewAIEventsBus\].*Sync handler error.*on_agent_logs_execution',
                r'\[CrewAIEventsBus\].*Expecting',
                r'Expecting value: line 1 column 1 \(char 0\)',
                r'Expecting value.*line 1 column 1',
                r'JSONDecodeError.*Expecting value',
                r'JSONDecodeError',
                r'on_agent_logs_execution.*Expecting',
                r'Sync handler error.*on_agent_logs_execution',
            ]
            
            # Também verifica por palavras-chave sem regex (mais rápido)
            keywords_to_filter = [
                'CrewAIEventsBus',
                'on_agent_logs_execution',
                'Expecting value: line 1 column 1',
                'JSONDecodeError',
            ]
            
            should_filter = False
            
            # Verifica palavras-chave primeiro (mais rápido)
            text_lower = text.lower()
            for keyword in keywords_to_filter:
                if keyword.lower() in text_lower:
                    should_filter = True
                    break
            
            # Se não encontrou por palavras-chave, tenta regex
            if not should_filter:
                for pattern in patterns_to_filter:
                    if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                        should_filter = True
                        break
            
            if not should_filter:
                # Escreve no IO original apenas se não for um erro de eventos
                self.original_io.write(text)
                self.original_io.flush()
    
    def flush(self):
        self.original_io.flush()
    
    def __getattr__(self, name):
        # Delega outros atributos/métodos para o IO original
        return getattr(self.original_io, name)

class SuppressCrewAIEventsErrors:
    """Context manager para suprimir erros de eventos do CrewAI"""
    def __init__(self):
        self.original_stderr = sys.stderr
        self.original_stdout = sys.stdout
        self.filtered_stderr = FilteredIO(sys.stderr)
        self.filtered_stdout = FilteredIO(sys.stdout)
    
    def __enter__(self):
        sys.stderr = self.filtered_stderr
        sys.stdout = self.filtered_stdout
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self.original_stderr
        sys.stdout = self.original_stdout
        return False  # Não suprime exceções reais

# Garante que o projeto esteja no path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "projeto_agente" / "src"))

try:
    from projeto_agente.create_crew_project import CreateCrewProject
except Exception as e:
    print("❌ ERRO IMPORTANDO CREW:", e)
    raise

# Monkey patch para desabilitar handlers problemáticos do EventsBus
def disable_crewai_events():
    """Desabilita handlers problemáticos do CrewAI EventsBus de forma mais agressiva"""
    try:
        # Abordagem 1: Intercepta diretamente o handler on_agent_logs_execution
        try:
            from crewai.events.bus import CrewAIEventsBus
            
            # Substitui o handler problemático por um que suprime erros JSON
            if hasattr(CrewAIEventsBus, 'on_agent_logs_execution'):
                original_handler = getattr(CrewAIEventsBus, 'on_agent_logs_execution', None)
                
                def safe_wrapped_handler(*args, **kwargs):
                    """Handler que suprime erros de JSON parsing silenciosamente"""
                    try:
                        if original_handler and callable(original_handler):
                            return original_handler(*args, **kwargs)
                    except (ValueError, Exception) as e:
                        # Suprime especificamente erros de JSON parsing
                        error_str = str(e).lower()
                        if any(keyword in error_str for keyword in [
                            "expecting value", "json", "jsondecodeerror", 
                            "line 1 column 1", "char 0"
                        ]):
                            # Suprime silenciosamente - não faz nada
                            return None
                        # Re-raise outros erros que não são relacionados a JSON
                        raise
                
                CrewAIEventsBus.on_agent_logs_execution = safe_wrapped_handler
        except (ImportError, AttributeError):
            pass
        
        # Abordagem 2: Tenta desabilitar eventos completamente
        try:
            from crewai.events import EventsBus
            if hasattr(EventsBus, 'disable'):
                EventsBus.disable()
        except (ImportError, AttributeError):
            pass
        
        # Abordagem 3: Intercepta o logger do EventsBus diretamente
        try:
            import logging
            events_logger = logging.getLogger("crewai.events.bus")
            # Remove todos os handlers existentes e adiciona um filtrado
            for handler in list(events_logger.handlers):
                events_logger.removeHandler(handler)
            
            # Cria um handler customizado que filtra mensagens de erro
            class FilteredHandler(logging.Handler):
                def emit(self, record):
                    message = record.getMessage()
                    if any(keyword in message.lower() for keyword in [
                        "crewai eventsbus", "on_agent_logs_execution",
                        "expecting value", "jsondecodeerror"
                    ]):
                        return  # Não emite a mensagem
                    # Para outras mensagens, usa o handler padrão
                    print(f"[CrewAI] {message}", file=sys.stderr)
            
            events_logger.addHandler(FilteredHandler())
            events_logger.setLevel(logging.CRITICAL)  # Só mostra críticos
        except Exception:
            pass
            
    except Exception:
        # Se qualquer coisa falhar, continua normalmente
        pass

# Aplica o patch ao importar
disable_crewai_events()

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
        # Desabilita eventos problemáticos antes de criar a crew
        disable_crewai_events()
        
        crew_instance = CreateCrewProject()
        crew = crew_instance.copywriting_crew()
        
        # Executa a crew com supressão de erros de eventos
        # Nota: Erros de eventos do CrewAI (como "Expecting value: line 1 column 1")
        # são não-críticos e geralmente não impedem a execução
        with SuppressCrewAIEventsErrors():
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
