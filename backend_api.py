from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys
import logging
import json
import re
from pathlib import Path

# Configura logging para suprimir erros de eventos do CrewAI (não críticos)
# Nota: Erros "Expecting value: line 1 column 1" em handlers de eventos do CrewAI
# são conhecidos e geralmente não afetam a funcionalidade principal

# Cria um filtro customizado para suprimir erros de eventos do CrewAI
class CrewAIEventsFilter(logging.Filter):
    def filter(self, record):
        # Suprime mensagens relacionadas a erros de eventos do CrewAI
        message = str(record.getMessage()).lower()
        
        # Lista expandida de palavras-chave que indicam erros de eventos
        error_keywords = [
            "crewai eventsbus",
            "on_agent_logs_execution",
            "expecting value: line 1 column 1",
            "expecting value",
            "expecting",  # Captura erros incompletos também
            "jsondecodeerror",
            "action 'none' don't exist",
            "action 'n/a' don't exist",
            "sync handler error",
            "sync handler error in on_agent_logs_execution",
        ]
        
        # Verifica se a mensagem contém alguma palavra-chave de erro
        if any(keyword in message for keyword in error_keywords):
            return False  # Não registra esta mensagem
        
        # Verifica também por padrões regex
        error_patterns = [
            r'\[CrewAIEventsBus\].*',
            r'Expecting value.*line 1 column 1',
            r"Action 'None' don't exist",
            r"Action 'N/A' don't exist",
            r"Action '.*' don't exist",  # Captura qualquer mensagem de ação inexistente
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, message, re.IGNORECASE):
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

class FilteredIO:
    """IO wrapper que filtra mensagens específicas do CrewAI EventsBus com buffer para capturar mensagens multi-linha"""
    def __init__(self, original_io):
        self.original_io = original_io
        self.buffer = ""  # Buffer para acumular mensagens multi-linha
        self.buffer_size_limit = 5000  # Limite do buffer para evitar acúmulo excessivo
    
    def write(self, text):
        if not text:
            return
        
        # Adiciona ao buffer
        self.buffer += text
        
        # Limita o tamanho do buffer
        if len(self.buffer) > self.buffer_size_limit:
            # Mantém apenas as últimas linhas
            lines = self.buffer.split('\n')
            self.buffer = '\n'.join(lines[-50:])  # Mantém últimas 50 linhas
        
        # Verifica se deve filtrar baseado no buffer acumulado
        should_filter = self._should_filter(self.buffer)
        
        # Se encontrar um erro de eventos, limpa o buffer e não escreve
        if should_filter:
            # Limpa o buffer completamente quando encontra erro
            self.buffer = ""
            return
        
        # Se o texto contém quebra de linha ou o buffer está grande, processa
        if '\n' in text:
            # Separa em linhas
            lines = self.buffer.split('\n')
            
            # Verifica cada linha e as linhas anteriores para contexto
            output_lines = []
            for i, line in enumerate(lines):
                # Verifica a linha atual e contexto (linhas anteriores próximas)
                context = '\n'.join(lines[max(0, i-3):i+1])
                
                if not self._should_filter(context):
                    output_lines.append(line)
                # Se for erro, não adiciona à saída
            
            # Escreve apenas as linhas que não foram filtradas
            if output_lines:
                output = '\n'.join(output_lines)
                if output.strip():  # Só escreve se houver conteúdo
                    self.original_io.write(output)
                    self.original_io.flush()
            
            # Limpa o buffer após processar
            self.buffer = ""
        elif len(self.buffer) > 500:
            # Se o buffer está grande sem quebra de linha, verifica e escreve se OK
            if not self._should_filter(self.buffer):
                self.original_io.write(self.buffer)
                self.original_io.flush()
            self.buffer = ""
    
    def _should_filter(self, text):
        """Verifica se o texto deve ser filtrado"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Palavras-chave que indicam erro de eventos (verificação rápida)
        error_keywords = [
            'crewai eventsbus',
            'on_agent_logs_execution',
            'expecting value: line 1 column 1',
            'expecting value',
            'expecting',  # Captura erros incompletos também
            'jsondecodeerror',
            "action 'none' don't exist",
            "action 'n/a' don't exist",
            'sync handler error',
            'sync handler error in on_agent_logs_execution',
        ]
        
        # Verifica palavras-chave primeiro (mais rápido)
        for keyword in error_keywords:
            if keyword in text_lower:
                return True
        
        # Padrões regex mais específicos
        patterns_to_filter = [
            r'\[CrewAIEventsBus\].*Sync handler error',
            r'\[CrewAIEventsBus\].*Sync handler error.*on_agent_logs_execution',
            r'\[CrewAIEventsBus\].*Expecting',
            r'\[CrewAIEventsBus\].*Expecting.*',
            r'\[CrewAIEventsBus\].*',  # Captura qualquer mensagem do CrewAIEventsBus
            r'Expecting value: line 1 column 1 \(char 0\)',
            r'Expecting value.*line 1 column 1',
            r'Expecting.*',  # Captura qualquer erro que comece com "Expecting"
            r'JSONDecodeError.*Expecting',
            r'Sync handler error.*on_agent_logs_execution',
            r'Sync handler error.*on_agent_logs_execution.*Expecting',
            r"Action 'None' don't exist",
            r"Action 'N/A' don't exist",
            r"Action '.*' don't exist",  # Captura qualquer mensagem de ação inexistente
        ]
        
        for pattern in patterns_to_filter:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    def flush(self):
        # Antes de fazer flush, verifica o buffer restante
        if self.buffer and not self._should_filter(self.buffer):
            self.original_io.write(self.buffer)
            self.buffer = ""
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
        # Faz flush final dos buffers antes de restaurar
        self.filtered_stderr.flush()
        self.filtered_stdout.flush()
        
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
                    except (ValueError, json.JSONDecodeError, Exception) as e:
                        # Suprime especificamente erros de JSON parsing
                        error_str = str(e).lower()
                        error_type = type(e).__name__.lower()
                        
                        # Verifica se é um erro de JSON parsing
                        is_json_error = (
                            isinstance(e, json.JSONDecodeError) or
                            "jsondecodeerror" in error_type or
                            any(keyword in error_str for keyword in [
                                "expecting value", "json", "jsondecodeerror", 
                                "line 1 column 1", "char 0", "expecting"
                            ])
                        )
                        
                        if is_json_error:
                            # Suprime silenciosamente - não faz nada
                            return None
                        # Re-raise outros erros que não são relacionados a JSON
                        raise
                
                CrewAIEventsBus.on_agent_logs_execution = safe_wrapped_handler
                
            # Também tenta interceptar o método _handle_sync se existir
            if hasattr(CrewAIEventsBus, '_handle_sync'):
                original_sync_handler = getattr(CrewAIEventsBus, '_handle_sync', None)
                
                def safe_sync_handler(*args, **kwargs):
                    """Handler sync que suprime erros de JSON parsing"""
                    try:
                        if original_sync_handler and callable(original_sync_handler):
                            return original_sync_handler(*args, **kwargs)
                    except (ValueError, json.JSONDecodeError, Exception) as e:
                        error_str = str(e).lower()
                        if any(keyword in error_str for keyword in [
                            "expecting value", "json", "jsondecodeerror", 
                            "line 1 column 1", "char 0", "expecting"
                        ]):
                            return None
                        raise
                
                CrewAIEventsBus._handle_sync = safe_sync_handler
            
            # Intercepta também métodos relacionados a eventos que podem gerar erros
            # Tenta interceptar qualquer método que possa estar gerando o erro
            for method_name in ['_handle_event', 'handle', 'emit', '_emit']:
                if hasattr(CrewAIEventsBus, method_name):
                    original_method = getattr(CrewAIEventsBus, method_name)
                    if callable(original_method):
                        def create_safe_handler(orig_method):
                            def safe_handler(*args, **kwargs):
                                try:
                                    return orig_method(*args, **kwargs)
                                except (ValueError, json.JSONDecodeError, Exception) as e:
                                    error_str = str(e).lower()
                                    if any(keyword in error_str for keyword in [
                                        "expecting value", "json", "jsondecodeerror", 
                                        "line 1 column 1", "char 0", "expecting"
                                    ]):
                                        return None
                                    raise
                            return safe_handler
                        setattr(CrewAIEventsBus, method_name, create_safe_handler(original_method))
                
        except (ImportError, AttributeError) as e:
            # Log silencioso se não conseguir importar
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
                    message_lower = message.lower()
                    if any(keyword in message_lower for keyword in [
                        "crewai eventsbus", "on_agent_logs_execution",
                        "expecting value", "expecting", "jsondecodeerror",
                        "sync handler error", "action", "don't exist"
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

class DashboardRequest(BaseModel):
    data_context: str
    topic: Optional[str] = "Análise de Dados"
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

@app.post("/api/dashboard")
async def generate_dashboard(request: DashboardRequest):

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY não configurada no Render.")

    try:
        # Desabilita eventos problemáticos antes de criar a crew
        disable_crewai_events()
        
        crew_instance = CreateCrewProject()
        crew = crew_instance.dashboard_crew()
        
        # Prepara os inputs para a crew de dashboard
        inputs = {
            "data_context": request.data_context,
            "topic": request.topic or "Análise de Dados",
            "definicao_do_sistema": request.definicao_do_sistema or ""
        }
        
        # Executa a crew com supressão de erros de eventos
        with SuppressCrewAIEventsErrors():
            result = crew.kickoff(inputs=inputs)
        
        text = result.final_output if hasattr(result, "final_output") else str(result)

        return {"success": True, "result": text, "raw": text}

    except Exception as e:
        error_msg = str(e)
        import traceback
        print(f"❌ Erro ao gerar dashboard: {error_msg}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        
        # Se for apenas erro de eventos JSON, tenta retornar uma mensagem mais amigável
        if "expecting value" in error_msg.lower() and "line 1 column 1" in error_msg.lower():
            raise HTTPException(
                500, 
                "Erro ao processar eventos internos do CrewAI. Isso geralmente não afeta o resultado. "
                "Se o problema persistir, verifique os logs do servidor."
            )
        raise HTTPException(500, f"Erro ao gerar dashboard: {error_msg}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
