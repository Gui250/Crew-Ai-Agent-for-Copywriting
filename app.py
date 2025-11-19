import streamlit as st
import requests
import os
import pandas as pd # Importado para o dashboard
import re # Importado para extrair código do dashboard
from dotenv import load_dotenv
from pathlib import Path

# --- CONFIGURAÇÃO INICIAL ---
# Carrega variáveis de ambiente (apenas para configuração local)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)

# URL do Backend API (configurável via variável de ambiente ou usar padrão)
BACKEND_URL = os.getenv('BACKEND_API_URL', 'https://crew-ai-agent-for-copywriting-1.onrender.com')

# Remove barra final se houver
BACKEND_URL = BACKEND_URL.rstrip('/')

st.set_page_config(page_title="AI Marketing Crew", page_icon="🚀", layout="wide")

# Mostra informações do backend na sidebar (apenas em desenvolvimento)
if os.getenv('STREAMLIT_ENV') != 'production':
    with st.sidebar:
        st.caption(f"🔗 Backend: {BACKEND_URL}")

# --- MENU DE NAVEGAÇÃO ---
with st.sidebar:
    st.title("🤖 AI Agent Suite")
    ferramenta = st.selectbox(
        "Escolha a Ferramenta:",
        ["✍️ Gerador de Copy", "📊 Dashboard Automático"]
    )
    st.markdown("---")

# ==============================================================================
# ABA 1: GERADOR DE COPY (Seu código original)
# ==============================================================================
if ferramenta == "✍️ Gerador de Copy":
    
    st.title("✍️ AI Marketing Crew: Copywriter")
    st.markdown("Gere copys baseados em sua estratégia e em referências da web.")

    # Inputs específicos desta ferramenta
    with st.sidebar:
        st.header("🔧 Configuração do Copy")
        
        topic = st.text_input(
            "Tópico / Produto",
            placeholder="Ex: Curso de Python para Iniciantes"
        )
        
        target_audience = st.text_input(
            "Público Alvo",
            placeholder="Ex: Profissionais em transição, 25-35 anos"
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
        generate_btn = st.button("🚀 Iniciar Copy", type="primary")

    # Lógica de Execução
    if generate_btn:
        if not topic or not target_audience:
            st.warning("⚠️ Por favor, preencha o Tópico e o Público Alvo antes de iniciar.")
        else:
            with st.status("🤖 A Crew está trabalhando...", expanded=True) as status:
                
                # Validação de URL
                if url_reference and url_reference.strip():
                    url_input = url_reference.strip()
                    if not url_input.startswith(('http://', 'https://')):
                        url_input = 'https://' + url_input
                else:
                    url_input = "Nenhuma URL fornecida. Use seu conhecimento geral."
                
                if url_input != "Nenhuma URL fornecida. Use seu conhecimento geral.":
                    st.write(f"🌐 **URL de referência:** {url_input}")

                inputs = {
                    'topic': topic,
                    'target_audience': target_audience,
                    'platform': platform,
                    'tone': tone,
                    'url': url_input
                }
                
                st.write("🔍 **Agente 1:** Pesquisador de Mercado está analisando...")
                st.write("📝 **Agente 2:** Copywriter está escrevendo...")
                st.write("✅ **Agente 3:** Editor Chefe finalizou o polimento...")

                try:
                    # Prepara a requisição para o backend
                    definicao_do_sistema = f"""
                    Sistema de criação de briefing e copywriting para {topic}.
                    O briefing deve conter: Perfil do Cliente, Dores/Desejos e Ganchos.
                    O copywriting deve seguir o framework PAS.
                    """
                    
                    payload = {
                        "topic": topic,
                        "target_audience": target_audience,
                        "platform": platform,
                        "tone": tone,
                        "url": url_input,
                        "definicao_do_sistema": definicao_do_sistema
                    }
                    
                    # Faz requisição ao backend
                    api_url = f"{BACKEND_URL}/api/copywriting"
                    st.write(f"🌐 Conectando ao backend: {BACKEND_URL}")
                    
                    response = requests.post(
                        api_url,
                        json=payload,
                        timeout=300  # 5 minutos de timeout (processamento pode demorar)
                    )
                    
                    # Verifica o content-type antes de tentar fazer parse JSON
                    content_type = response.headers.get('content-type', '')
                    
                    if response.status_code == 200:
                        try:
                            if 'application/json' in content_type:
                                result_data = response.json()
                                copy_text = result_data.get("result", "")
                                
                                if not copy_text:
                                    copy_text = result_data.get("raw", "Nenhum resultado retornado.")
                            else:
                                # Se não for JSON, usa o texto direto
                                copy_text = response.text
                                if not copy_text:
                                    copy_text = "Nenhum resultado retornado."
                            
                            status.update(label="Copy Gerado com Sucesso!", state="complete", expanded=False)
                        except ValueError as json_error:
                            # Erro ao fazer parse JSON
                            st.error(f"❌ Erro ao processar resposta JSON: {json_error}")
                            st.write(f"📄 Resposta recebida (texto): {response.text[:500]}")
                            raise Exception(f"Resposta do backend não é JSON válido: {response.text[:200]}")
                    else:
                        # Trata erros HTTP
                        try:
                            if 'application/json' in content_type:
                                error_data = response.json()
                                error_msg = error_data.get("detail", error_data.get("message", f"Erro {response.status_code}"))
                            else:
                                error_msg = f"Erro {response.status_code}: {response.text[:200]}"
                        except ValueError:
                            error_msg = f"Erro {response.status_code}: {response.text[:200]}"
                        raise Exception(f"Erro do backend: {error_msg}")
                    
                    st.divider()
                    st.subheader("📄 Copy Finalizado")
                    st.markdown(copy_text)

                    st.download_button(
                        label="📥 Baixar Copy (.md)",
                        data=copy_text,
                        file_name=f"copy_{platform.lower()}_{topic.replace(' ', '_')}.md",
                        mime="text/markdown"
                    )
                    
                except requests.exceptions.Timeout:
                    status.update(label="Timeout", state="error")
                    st.error("⏱️ O processamento está demorando muito. Tente novamente ou use dados menores.")
                except requests.exceptions.ConnectionError:
                    status.update(label="Erro de Conexão", state="error")
                    st.error(f"❌ Não foi possível conectar ao backend em {BACKEND_URL}. Verifique se o serviço está online.")
                except ValueError as json_error:
                    # Erro de parsing JSON
                    status.update(label="Erro de Formato", state="error")
                    st.error(f"❌ Erro ao processar resposta do backend (não é JSON válido): {str(json_error)}")
                    st.info("💡 Dica: Verifique se o backend está retornando JSON válido. Pode ser que o serviço esteja offline ou retornando HTML.")
                except requests.exceptions.RequestException as e:
                    status.update(label="Erro na Requisição", state="error")
                    st.error(f"❌ Erro ao comunicar com o backend: {str(e)}")
                    # Tenta mostrar mais detalhes se disponível
                    if hasattr(e, 'response') and e.response is not None:
                        with st.expander("🔍 Detalhes da Resposta"):
                            st.write(f"Status Code: {e.response.status_code}")
                            st.write(f"Headers: {dict(e.response.headers)}")
                            st.write(f"Conteúdo: {e.response.text[:500]}")
                except Exception as e:
                    status.update(label="Erro na Execução", state="error")
                    st.error(f"❌ Ocorreu um erro: {str(e)}")
                    import traceback
                    with st.expander("🔍 Detalhes do Erro"):
                        st.code(traceback.format_exc())

# ==============================================================================
# ABA 2: DASHBOARD AUTOMÁTICO (Nova Ferramenta)
# ==============================================================================
elif ferramenta == "📊 Dashboard Automático":
    
    st.title("📊 Gerador de Dashboard")
    st.markdown("Cole seus dados brutos ou envie um arquivo CSV e deixe a IA criar gráficos interativos.")

    # Inputs específicos desta ferramenta na Sidebar
    with st.sidebar:
        st.header("🔧 Dados")
        
        # Opção 1: Upload de arquivo CSV
        uploaded_file = st.file_uploader(
            "Ou envie um arquivo CSV:",
            type=['csv'],
            help="Faça upload de um arquivo CSV para análise automática"
        )
        
        st.markdown("---")
        st.markdown("**OU**")
        st.markdown("---")
        
        # Opção 2: Entrada de texto
        data_input = st.text_area(
            "Cole seus dados aqui (Texto ou JSON):",
            height=200,
            placeholder="Ex: Gastamos R$ 5000 no Google Ads, tivemos 200 leads e 15 vendas. O CPC foi R$ 25."
        )
        generate_dash_btn = st.button("📈 Gerar Gráficos", type="primary")

    if generate_dash_btn:
        # Validação melhorada: verifica se há dados válidos (não vazios)
        has_text_data = data_input and data_input.strip()
        has_csv_file = uploaded_file is not None
        
        if not has_text_data and not has_csv_file:
            st.warning("⚠️ Por favor, insira os dados ou envie um arquivo CSV para análise.")
        else:
            with st.status("🤖 Analisando números e desenhando gráficos...", expanded=True) as status:
                
                # Processa o arquivo CSV se fornecido
                csv_data = None
                csv_summary = None
                data_context = None
                df = None  # Inicializa df no escopo correto
                
                if uploaded_file is not None:
                    try:
                        # Lê o CSV e salva o conteúdo em bytes para reutilização
                        file_bytes = uploaded_file.read()
                        uploaded_file.seek(0)  # Reset para o início do arquivo
                        
                        # Tenta ler o CSV com diferentes codificações
                        import io
                        import chardet
                        
                        # Detecta a codificação do arquivo
                        detected = chardet.detect(file_bytes)
                        encoding = detected.get('encoding', 'utf-8')
                        confidence = detected.get('confidence', 0)
                        
                        # Lista de codificações para tentar (em ordem de prioridade)
                        encodings_to_try = [
                            encoding if confidence > 0.7 else None,  # Usa a detectada se confiança > 70%
                            'utf-8',
                            'latin-1',  # ISO-8859-1
                            'iso-8859-1',
                            'cp1252',   # Windows-1252
                            'windows-1252',
                            'utf-8-sig'  # UTF-8 com BOM
                        ]
                        
                        # Remove None da lista
                        encodings_to_try = [e for e in encodings_to_try if e is not None]
                        
                        df = None
                        encoding_used = None
                        last_error = None
                        
                        # Tenta cada codificação até uma funcionar
                        for enc in encodings_to_try:
                            try:
                                uploaded_file.seek(0)  # Reset para o início
                                # Tenta primeiro com separador padrão (vírgula)
                                df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep=',')
                                
                                # Se o DataFrame tem apenas 1 coluna, tenta com ponto e vírgula
                                if df.shape[1] == 1:
                                    uploaded_file.seek(0)
                                    df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep=';')
                                
                                # Se ainda tem apenas 1 coluna, tenta com tab
                                if df.shape[1] == 1:
                                    uploaded_file.seek(0)
                                    df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep='\t')
                                
                                encoding_used = enc
                                break
                            except (UnicodeDecodeError, UnicodeError) as e:
                                last_error = e
                                continue
                            except Exception as e:
                                # Outros erros (não relacionados à codificação)
                                last_error = e
                                continue
                        
                        if df is None:
                            raise Exception(f"Não foi possível ler o arquivo CSV. Tentadas codificações: {', '.join(encodings_to_try)}. Último erro: {last_error}")
                        
                        if encoding_used and encoding_used != 'utf-8':
                            st.info(f"📝 Arquivo lido com codificação: **{encoding_used}**")
                        
                        # Cria um resumo do CSV (limitado para não exceder tokens)
                        # Limita a quantidade de dados enviados
                        max_rows_summary = min(10, df.shape[0])  # Máximo 10 linhas no resumo
                        max_rows_full = min(50, df.shape[0])  # Máximo 50 linhas para análise
                        
                        # Pega uma amostra representativa (primeiras e últimas linhas)
                        if df.shape[0] > max_rows_summary:
                            sample_df = pd.concat([
                                df.head(max_rows_summary // 2),
                                df.tail(max_rows_summary // 2)
                            ])
                        else:
                            sample_df = df
                        
                        # Estatísticas resumidas
                        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                        stats_summary = ""
                        if len(numeric_cols) > 0:
                            stats_summary = f"\n- Estatísticas das colunas numéricas:\n{df[numeric_cols].describe().to_string()}"
                        
                        csv_summary = f"""
                        ARQUIVO CSV CARREGADO:
                        - Nome do arquivo: {uploaded_file.name}
                        - Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas
                        - Colunas: {', '.join(df.columns.tolist())}
                        - Amostra de dados (primeiras e últimas linhas):
                        {sample_df.to_string()}
                        {stats_summary}
                        
                        NOTA: O DataFrame completo está disponível como 'df' com {df.shape[0]} linhas.
                        Use df diretamente no código, não precisa incluir todos os dados aqui.
                        """
                        
                        # Marca que há CSV carregado (sem converter tudo para string - economiza tokens)
                        csv_data = True  # Usa boolean para indicar que há CSV
                        data_context = csv_summary
                        
                        st.write(f"✅ Arquivo CSV carregado: **{uploaded_file.name}** ({df.shape[0]} linhas, {df.shape[1]} colunas)")
                        st.write(f"📊 Colunas: {', '.join(df.columns.tolist())}")
                        
                    except Exception as e:
                        st.error(f"Erro ao ler o arquivo CSV: {e}")
                        status.update(label="Erro ao processar CSV", state="error")
                        st.stop()
                
                # Se não há CSV, usa os dados de texto
                if not data_context:
                    if has_text_data:
                        data_context = data_input.strip()
                    else:
                        # Fallback: se por algum motivo não há dados, usa uma mensagem padrão
                        data_context = "Nenhum dado fornecido. Por favor, forneça dados para análise."
                
                # Garantir que data_context sempre tenha um valor válido
                if not data_context or not data_context.strip():
                    data_context = "Nenhum dado fornecido. Por favor, forneça dados para análise."
                
                # Inputs para a Crew - SEMPRE inclui data_context
                inputs = {
                    'topic': 'Análise de Dados de Marketing',
                    'data_context': str(data_context)  # Garantir que seja string
                }
                
                # Instrução específica para o Agente focar em Código Python/Streamlit
                if csv_data:
                    # Prepara informações sobre as colunas disponíveis
                    df_columns = df.columns.tolist() if df is not None else []
                    columns_list = ', '.join([f"'{col}'" for col in df_columns])
                    columns_info = f"Colunas disponíveis no DataFrame: {columns_list}"
                    
                    inputs['definicao_do_sistema'] = f"""
                    Você é um Data Scientist Senior Especialista em Streamlit.
                    O usuário forneceu um arquivo CSV com os seguintes dados:
                    
                    {csv_summary}
                    
                    {columns_info}
                    
                    REGRAS CRÍTICAS: 
                    - O DataFrame já está carregado e disponível APENAS como variável 'df' (não 'data_df', não 'df_data', apenas 'df').
                    - NÃO crie novas variáveis de DataFrame. Use APENAS 'df'.
                    - NÃO tente ler o arquivo CSV novamente usando pd.read_csv() com o nome do arquivo.
                    - Use APENAS a variável 'df' que já contém todos os dados.
                    - Use APENAS as colunas listadas acima. Verifique se a coluna existe antes de usá-la.
                    - Se uma coluna tiver espaços, use df['Nome da Coluna'] (com aspas).
                    - Sempre verifique se as colunas existem: if 'coluna' in df.columns:
                    - NÃO renomeie o DataFrame. Use 'df' diretamente.
                    
                    Crie um script Python COMPLETO usando 'streamlit' para gerar um dashboard.
                    - Use APENAS a variável 'df' que já está disponível (NÃO use pd.read_csv, NÃO crie data_df ou outras variáveis).
                    - Use st.columns para exibir os KPIs principais (Cards com números grandes) no topo.
                    - Crie pelo menos 2 gráficos visuais usando st.bar_chart, st.line_chart, st.area_chart ou plotly.
                    - Use os dados EXATOS do DataFrame 'df', não invente dados.
                    - O código deve ser autocontido e executável.
                    - Sempre verifique se as colunas existem antes de usá-las.
                    - Exemplo seguro: if 'coluna' in df.columns: st.write(df['coluna'])
                    - NÃO inclua linhas como: df = pd.read_csv('nome_arquivo.csv') ou data_df = df.copy()
                    - Use diretamente: df.head(), df['coluna'], df.describe(), etc.
                    """
                else:
                    inputs['definicao_do_sistema'] = f"""
                    Você é um Data Scientist Senior Especialista em Streamlit.
                    Sua tarefa é ler os seguintes dados: "{data_context}".
                    
                    Crie um script Python COMPLETO usando 'streamlit' para gerar um dashboard.
                    - Use st.columns para métricas (KPIs).
                    - Use st.bar_chart ou st.line_chart para visualizações.
                    - O código deve ser executável.
                    """
                
                try:
                    # Prepara a requisição para o backend
                    definicao_do_sistema = f"""
                    Você é um Data Scientist Senior Especialista em Streamlit.
                    Sua tarefa é ler os seguintes dados: "{data_context}".
                    
                    Crie um script Python COMPLETO usando 'streamlit' para gerar um dashboard.
                    - Use st.columns para métricas (KPIs).
                    - Use st.bar_chart ou st.line_chart para visualizações.
                    - O código deve ser executável.
                    """
                    
                    payload = {
                        "data_context": str(data_context),
                        "topic": "Análise de Dados de Marketing",
                        "definicao_do_sistema": definicao_do_sistema
                    }
                    
                    # Faz requisição ao backend
                    api_url = f"{BACKEND_URL}/api/dashboard"
                    st.write(f"🌐 Conectando ao backend: {BACKEND_URL}")
                    
                    response = requests.post(
                        api_url,
                        json=payload,
                        timeout=300  # 5 minutos de timeout
                    )
                    
                    # Verifica o content-type antes de tentar fazer parse JSON
                    content_type = response.headers.get('content-type', '')
                    
                    if response.status_code == 200:
                        try:
                            if 'application/json' in content_type:
                                result_data = response.json()
                                raw_result = result_data.get("result", result_data.get("raw", ""))
                            else:
                                # Se não for JSON, usa o texto direto
                                raw_result = response.text
                                if not raw_result:
                                    raw_result = "Nenhum resultado retornado."
                            
                            status.update(label="Dashboard Criado!", state="complete", expanded=False)
                        except ValueError as json_error:
                            # Erro ao fazer parse JSON
                            st.error(f"❌ Erro ao processar resposta JSON: {json_error}")
                            st.write(f"📄 Resposta recebida (texto): {response.text[:500]}")
                            raise Exception(f"Resposta do backend não é JSON válido: {response.text[:200]}")
                    else:
                        # Trata erros HTTP
                        try:
                            if 'application/json' in content_type:
                                error_data = response.json()
                                error_msg = error_data.get("detail", error_data.get("message", f"Erro {response.status_code}"))
                            else:
                                error_msg = f"Erro {response.status_code}: {response.text[:200]}"
                        except ValueError:
                            error_msg = f"Erro {response.status_code}: {response.text[:200]}"
                        raise Exception(f"Erro do backend: {error_msg}")
                    
                    st.subheader("Visualização")
                    
                    # Tenta extrair e rodar o código Python gerado pela IA
                    code_match = re.search(r'```python\n(.*?)```', raw_result, re.DOTALL)
                    if code_match:
                        code_to_run = code_match.group(1)
                        try:
                            # Verifica e instala dependências necessárias se não estiverem disponíveis
                            import subprocess
                            import sys
                            dependencies_to_check = ['plotly', 'pandas']
                            for dep in dependencies_to_check:
                                try:
                                    __import__(dep)
                                except ImportError:
                                    st.info(f"📦 Instalando {dep}...")
                                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "-q"])
                                    st.success(f"✅ {dep} instalado com sucesso!")
                            
                            # Se houver CSV, disponibiliza o DataFrame no contexto de execução
                            if csv_data and df is not None:
                                # Usa o DataFrame já carregado anteriormente (não precisa recarregar)
                                # Remove qualquer tentativa de ler o arquivo do código gerado
                                import re
                                
                                # Remove linhas problemáticas do código gerado
                                code_lines = code_to_run.split('\n')
                                filtered_lines = []
                                for line in code_lines:
                                    # Remove linhas que tentam ler CSV com pd.read_csv
                                    if 'pd.read_csv' in line and ('uploaded_file' not in line.lower() and 'io.BytesIO' not in line):
                                        # Pula esta linha - o DataFrame já está disponível
                                        continue
                                    # Remove tentativas de criar variáveis de DataFrame (data_df, df_data, etc)
                                    if re.search(r'\b(data_df|df_data|df_copy|data)\s*=', line) and 'df' in line.lower():
                                        # Substitui por comentário ou remove
                                        continue
                                    # Substitui referências a data_df por df
                                    if 'data_df' in line:
                                        line = line.replace('data_df', 'df')
                                    filtered_lines.append(line)
                                
                                code_to_run = '\n'.join(filtered_lines)
                                
                                # Usa o DataFrame já carregado
                                exec_globals = {
                                    'pd': pd,
                                    'st': st,
                                    'df': df,  # Usa o DataFrame já carregado
                                    'pandas': pd,  # Alias adicional
                                    'np': __import__('numpy') if 'numpy' in code_to_run else None
                                }
                                
                                # Remove None do dict
                                exec_globals = {k: v for k, v in exec_globals.items() if v is not None}
                                
                                exec(code_to_run, exec_globals) # Executa o código gerado na tela
                            else:
                                # Para dados de texto, executa normalmente
                                exec_globals = {
                                    'pd': pd,
                                    'st': st
                                }
                                exec(code_to_run, exec_globals) # Executa o código gerado na tela
                        except Exception as exec_error:
                            error_msg = str(exec_error)
                            st.error(f"Erro ao renderizar gráficos: {error_msg}")
                            
                            # Mostra informações úteis sobre o DataFrame se houver erro
                            if csv_data and df is not None:
                                cols_list = ', '.join([f"'{col}'" for col in df.columns.tolist()])
                                st.info(f"📊 **Colunas disponíveis no DataFrame:** {cols_list}")
                                st.info(f"📏 **Dimensões:** {df.shape[0]} linhas x {df.shape[1]} colunas")
                                
                                # Se o erro menciona uma coluna específica, mostra ajuda
                                if "'" in error_msg or '"' in error_msg:
                                    import re
                                    # Tenta extrair o nome da coluna do erro
                                    col_match = re.search(r"['\"]([^'\"]+)['\"]", error_msg)
                                    if col_match:
                                        col_name = col_match.group(1)
                                        if col_name not in df.columns.tolist():
                                            st.warning(f"⚠️ A coluna '{col_name}' não existe no DataFrame. Verifique o nome exato das colunas acima.")
                            
                            st.code(code_to_run, language='python')
                    else:
                        st.info("A IA não retornou um bloco de código executável. Veja a análise abaixo:")
                        st.write(raw_result)
                        
                except requests.exceptions.Timeout:
                    status.update(label="Timeout", state="error")
                    st.error("⏱️ O processamento está demorando muito. Tente novamente ou use dados menores.")
                except requests.exceptions.ConnectionError:
                    status.update(label="Erro de Conexão", state="error")
                    st.error(f"❌ Não foi possível conectar ao backend em {BACKEND_URL}. Verifique se o serviço está online.")
                except ValueError as json_error:
                    # Erro de parsing JSON
                    status.update(label="Erro de Formato", state="error")
                    st.error(f"❌ Erro ao processar resposta do backend (não é JSON válido): {str(json_error)}")
                    st.info("💡 Dica: Verifique se o backend está retornando JSON válido. Pode ser que o serviço esteja offline ou retornando HTML.")
                except requests.exceptions.RequestException as e:
                    status.update(label="Erro na Requisição", state="error")
                    st.error(f"❌ Erro ao comunicar com o backend: {str(e)}")
                    # Tenta mostrar mais detalhes se disponível
                    if hasattr(e, 'response') and e.response is not None:
                        with st.expander("🔍 Detalhes da Resposta"):
                            st.write(f"Status Code: {e.response.status_code}")
                            st.write(f"Headers: {dict(e.response.headers)}")
                            st.write(f"Conteúdo: {e.response.text[:500]}")
                except Exception as e:
                    status.update(label="Erro na Execução", state="error")
                    st.error(f"❌ Erro na execução: {str(e)}")
                    import traceback
                    with st.expander("🔍 Detalhes do Erro"):
                        st.code(traceback.format_exc())