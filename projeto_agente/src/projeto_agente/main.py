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
    current_file.parent.parent.parent.parent / '.env',  # /Users/guilhermemoreno/Desktop/crew/.env
    current_file.parent.parent.parent / '.env',        # /Users/guilhermemoreno/Desktop/crew/projeto_agente/.env
    Path.cwd() / '.env',                                # Diretório atual de execução
    Path.home() / '.env',                               # Home do usuário (fallback)
]

# Tenta carregar o primeiro arquivo .env encontrado
env_loaded = False
for env_path in possible_env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        env_loaded = True
        break

# Se nenhum arquivo .env foi encontrado, tenta carregar do diretório atual
if not env_loaded:
    load_dotenv(override=True)

# Verifica se OPENAI_API_KEY está definida
if not os.getenv('OPENAI_API_KEY'):
    print("AVISO: OPENAI_API_KEY não encontrada nas variáveis de ambiente.")
    print("Por favor, crie um arquivo .env com sua chave da API da OpenAI.")
    print("Exemplo: OPENAI_API_KEY=sk-...")

from crew import ProjetoAgente

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        ProjetoAgente().crew().kickoff(inputs=inputs)
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
        ProjetoAgente().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ProjetoAgente().crew().replay(task_id=sys.argv[1])

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
        ProjetoAgente().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

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
        result = ProjetoAgente().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")


if __name__ == "__main__":
    run()