import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Adiciona o caminho do módulo ao sys.path
project_path = Path(__file__).parent / "projeto_agente" / "src" / "projeto_agente" / "create_crew_project" / "src" / "create_crew_project"
sys.path.insert(0, str(project_path))

# Carrega variáveis de ambiente
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent / "projeto_agente" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

from crew import CreateCrewProject

st.set_page_config(page_title="AI Marketing Crew", page_icon="✍️", layout="wide")

st.title("✍️ AI Marketing Crew: Copywriter com Leitura de URL")
st.markdown("Gere copys baseados em sua estratégia e em referências da web.")

with st.sidebar:
    st.header("🔧 Configuração do Briefing")
    
    topic = st.text_input(
        "Tópico / Produto",
        placeholder="Ex: Curso de Python para Iniciantes"
    )
    
    target_audience = st.text_input(
        "Público Alvo",
        placeholder="Ex: Profissionais em transição de carreira, 25-35 anos"
    )
    
    url_reference = st.text_input(
        "URL de Referência (Opcional)",
        placeholder="https://exemplo.com/artigo-base"
    )
    
    platform = st.selectbox(
        "Plataforma de Destino",
        ["Instagram", "LinkedIn", "Blog Post", "Email Newsletter", "Twitter Thread"]
    )
    
    tone = st.select_slider(
        "Tom de Voz",
        options=["Muito Formal", "Profissional", "Casual", "Divertido/Irreverente"],
        value="Profissional"
    )
    
    st.markdown("---")
    generate_btn = st.button("🚀 Iniciar Criação", type="primary")

if generate_btn:
    if not topic or not target_audience:
        st.warning("⚠️ Por favor, preencha o Tópico e o Público Alvo antes de iniciar.")
    else:
        with st.status("🤖 A Crew está trabalhando...", expanded=True) as status:
            
            # Valida e limpa a URL
            if url_reference and url_reference.strip():
                url_input = url_reference.strip()
                # Garante que a URL começa com http:// ou https://
                if not url_input.startswith(('http://', 'https://')):
                    url_input = 'https://' + url_input
            else:
                url_input = "Nenhuma URL fornecida. Use seu conhecimento geral."
            
            # Mostra a URL que será usada
            if url_input != "Nenhuma URL fornecida. Use seu conhecimento geral.":
                st.write(f"🌐 **URL de referência:** {url_input}")

            inputs = {
                'topic': topic,
                'target_audience': target_audience,
                'platform': platform,
                'tone': tone,
                'url': url_input
            }
            
            st.write("🔍 **Agente 1:** Pesquisador de Mercado está analisando dores e desejos...")
            st.write("📝 **Agente 2:** Copywriter está escrevendo a primeira versão...")
            st.write("✅ **Agente 3:** Editor Chefe finalizou o polimento...")

            try:
                # Adiciona definicao_do_sistema aos inputs
                inputs['definicao_do_sistema'] = f"""
                Sistema de criação de briefing e copywriting para {topic}.
                O briefing deve conter: Perfil do Cliente, Lista de Dores/Desejos e 3 sugestões de "Ganchos" (Hooks).
                O copywriting deve ser baseado no briefing e seguir o framework PAS (Problema, Agitação, Solução).
                """
                
                crew_instance = CreateCrewProject()
                result = crew_instance.crew().kickoff(inputs=inputs)
                
                status.update(label="Processo Concluído!", state="complete", expanded=False)
                
                # Extrai o resultado do copy
                copy_text = ""
                
                if hasattr(result, 'tasks_output') and result.tasks_output:
                    # Pega o output da última task (geralmente é a de edição)
                    for task_output in reversed(result.tasks_output):
                        if task_output and isinstance(task_output, str):
                            copy_text = task_output
                            break
                
                # Se não encontrou, tenta extrair do resultado geral
                if not copy_text:
                    if hasattr(result, 'raw'):
                        copy_text = str(result.raw)
                    else:
                        copy_text = str(result)
                
                st.divider()
                st.subheader("📄 Copy Finalizado")
                st.markdown(copy_text)

                # Botão de Download do Copy
                st.download_button(
                    label="📥 Baixar Copy (.md)",
                    data=copy_text,
                    file_name=f"copy_{platform.lower()}_{topic.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                status.update(label="Erro na Execução", state="error")
                st.error(f"Ocorreu um erro: {str(e)}")
                st.exception(e) # Exibe o traceback completo para debug
