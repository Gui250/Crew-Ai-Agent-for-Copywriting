#!/usr/bin/env python
import sys
import warnings
from pathlib import Path

from datetime import datetime
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
# Procura o arquivo .env em múltiplos locais possíveis
current_file = Path(__file__).resolve()
possible_env_paths = [
    current_file.parent.parent.parent / '.env',                      # create_crew_project/.env
    current_file.parent.parent.parent.parent.parent.parent / '.env', # projeto_agente/.env
    current_file.parent.parent.parent.parent.parent.parent.parent / '.env',  # crew/.env
    Path.cwd() / '.env',                                             # Diretório atual de execução
    Path.home() / '.env',                                            # Home do usuário (fallback)
]

# Tenta carregar o primeiro arquivo .env encontrado que tenha OPENAI_API_KEY
env_loaded = False
for env_path in possible_env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        # Verifica se a chave foi carregada
        if os.getenv('OPENAI_API_KEY'):
            env_loaded = True
            break

# Se nenhum arquivo .env com chave foi encontrado, tenta carregar do diretório atual
if not env_loaded:
    load_dotenv(override=True)

# Verifica se OPENAI_API_KEY está definida
if not os.getenv('OPENAI_API_KEY'):
    print("AVISO: OPENAI_API_KEY não encontrada nas variáveis de ambiente.")
    print("Por favor, crie um arquivo .env com sua chave da API da OpenAI.")
    print("Exemplo: OPENAI_API_KEY=sk-...")
    print("\nLocais verificados:")
    for env_path in possible_env_paths:
        status = "✓ existe" if env_path.exists() else "✗ não existe"
        print(f"  {env_path}: {status}")

# Inicializa AgentOps (opcional - apenas se AGENTOPS_API_KEY estiver configurada)
try:
    import agentops
    agentops_api_key = os.getenv('AGENTOPS_API_KEY')
    if agentops_api_key:
        agentops.init(api_key=agentops_api_key)
        print("✓ AgentOps inicializado com sucesso!")
    else:
        print("ℹ️ AgentOps não configurado (AGENTOPS_API_KEY não encontrada no .env)")
except ImportError:
    print("ℹ️ AgentOps não instalado. Para usar, instale com: pip install agentops")
except Exception as e:
    print(f"⚠️ Erro ao inicializar AgentOps: {e}")

from crew import CreateCrewProject

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


SISTEMA = '''Um sistema de criação de uma crew de briefing para copywriting. Primeiro faz uma pesquisa de conteudos relevantes para o briefing.
    Então, cria um briefing detalhado contendo: Perfil do Cliente, 
    Lista de Dores/Desejos e 3 sugestões de "Ganchos" (Hooks) para iniciar o texto.
    O briefing deve ser formatado em Markdown.
    O briefing deve ser salvo no arquivo 'output/briefing.md'.
    O briefing deve ser salvo no arquivo 'output/briefing.md'.
    Então, cria um rascunho de copywriting baseado no briefing.
    O rascunho deve ser formatado em Markdown.
    O rascunho deve ser salvo no arquivo 'output/rascunho_copy.md'.
    Então, cria um rascunho de copywriting baseado no briefing.
    O rascunho deve ser formatado em Markdown.
    O rascunho deve ser salvo no arquivo 'output/rascunho_copy.md'.
    Então, cria um rascunho de copywriting baseado no briefing.
    O rascunho deve ser formatado em Markdown.
    O rascunho deve ser salvo no arquivo 'output/rascunho_copy.md'.
    
    
    
    
    '''

def run():
    """
    Run the crew.
    """
    inputs = {
        'definicao_do_sistema': SISTEMA,
        'topic': 'Produto ou Serviço',  # Tópico principal do copywriting
        'target_audience': 'Público-alvo do produto',  # Público-alvo
        'platform': 'Email Marketing',  # Plataforma onde será publicado
        'tone': 'profissional e persuasivo',  # Tom de voz desejado
        'url': 'Nenhuma URL fornecida. Use seu conhecimento geral.'  # URL de referência (opcional)
    }

    try:
        CreateCrewProject().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        CreateCrewProject().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CreateCrewProject().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        CreateCrewProject().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = CreateCrewProject().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")

if __name__ == "__main__":
    run()