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
    
    st.title("📊 Dashboard Automático Inteligente")
    st.markdown("Envie uma planilha CSV ou Excel e receba um dashboard dinâmico e personalizado automaticamente!")

    # Inputs específicos desta ferramenta na Sidebar
    with st.sidebar:
        st.header("🔧 Dados")
        
        # Opção 1: Upload de arquivo CSV ou Excel
        uploaded_file = st.file_uploader(
            "Envie um arquivo CSV ou Excel:",
            type=['csv', 'xlsx', 'xls'],
            help="Faça upload de um arquivo CSV ou Excel para análise automática"
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
                        import io
                        import chardet
                        
                        # Detecta o tipo de arquivo pela extensão
                        file_name = uploaded_file.name.lower()
                        is_excel = file_name.endswith(('.xlsx', '.xls'))
                        is_csv = file_name.endswith('.csv')
                        
                        df = None
                        encoding_used = None
                        
                        if is_excel:
                            # Lê arquivo Excel
                            try:
                                # Tenta ler todas as abas e pega a primeira
                                uploaded_file.seek(0)
                                
                                # Tenta primeiro com openpyxl (para .xlsx)
                                try:
                                    excel_file = pd.ExcelFile(uploaded_file, engine='openpyxl')
                                    sheet_names = excel_file.sheet_names
                                    df = pd.read_excel(uploaded_file, sheet_name=sheet_names[0], engine='openpyxl')
                                    
                                    if len(sheet_names) > 1:
                                        st.info(f"📑 Arquivo Excel com {len(sheet_names)} abas. Usando a primeira aba: **{sheet_names[0]}**")
                                except Exception as e1:
                                    # Tenta com xlrd (para .xls antigos)
                                    try:
                                        uploaded_file.seek(0)
                                        excel_file = pd.ExcelFile(uploaded_file, engine='xlrd')
                                        sheet_names = excel_file.sheet_names
                                        df = pd.read_excel(uploaded_file, sheet_name=sheet_names[0], engine='xlrd')
                                        
                                        if len(sheet_names) > 1:
                                            st.info(f"📑 Arquivo Excel com {len(sheet_names)} abas. Usando a primeira aba: **{sheet_names[0]}**")
                                    except Exception as e2:
                                        # Se ambos falharem, tenta sem especificar engine
                                        try:
                                            uploaded_file.seek(0)
                                            df = pd.read_excel(uploaded_file)
                                        except Exception as e3:
                                            raise Exception(f"Erro ao ler arquivo Excel. Tente instalar openpyxl (pip install openpyxl) ou xlrd (pip install xlrd). Erros: {str(e1)}, {str(e2)}, {str(e3)}")
                                
                            except Exception as e:
                                raise Exception(f"Erro ao ler arquivo Excel: {str(e)}. Certifique-se de que openpyxl ou xlrd estão instalados.")
                        
                        elif is_csv:
                            # Lê arquivo CSV com suporte a múltiplas codificações
                            file_bytes = uploaded_file.read()
                            uploaded_file.seek(0)
                            
                            # Detecta a codificação do arquivo
                            detected = chardet.detect(file_bytes)
                            encoding = detected.get('encoding', 'utf-8')
                            confidence = detected.get('confidence', 0)
                            
                            # Lista de codificações para tentar (em ordem de prioridade)
                            encodings_to_try = [
                                encoding if confidence > 0.7 else None,
                                'utf-8',
                                'latin-1',
                                'iso-8859-1',
                                'cp1252',
                                'windows-1252',
                                'utf-8-sig'
                            ]
                            
                            encodings_to_try = [e for e in encodings_to_try if e is not None]
                            
                            last_error = None
                            
                            # Tenta cada codificação até uma funcionar
                            for enc in encodings_to_try:
                                try:
                                    uploaded_file.seek(0)
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
                                    last_error = e
                                    continue
                            
                            if df is None:
                                raise Exception(f"Não foi possível ler o arquivo CSV. Tentadas codificações: {', '.join(encodings_to_try)}. Último erro: {last_error}")
                            
                            if encoding_used and encoding_used != 'utf-8':
                                st.info(f"📝 Arquivo CSV lido com codificação: **{encoding_used}**")
                        else:
                            raise Exception(f"Formato de arquivo não suportado: {uploaded_file.name}")
                        
                        # Limpeza básica dos dados
                        # Remove colunas completamente vazias
                        df = df.dropna(axis=1, how='all')
                        # Remove linhas completamente vazias
                        df = df.dropna(axis=0, how='all')
                        
                        # Cria um resumo do arquivo (limitado para não exceder tokens)
                        max_rows_summary = min(10, df.shape[0])
                        
                        # Pega uma amostra representativa
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
                        
                        file_type = "Excel" if is_excel else "CSV"
                        csv_summary = f"""
                        ARQUIVO {file_type} CARREGADO:
                        - Nome do arquivo: {uploaded_file.name}
                        - Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas
                        - Colunas: {', '.join(df.columns.tolist())}
                        - Tipos de dados: {dict(df.dtypes)}
                        - Amostra de dados (primeiras e últimas linhas):
                        {sample_df.to_string()}
                        {stats_summary}
                        
                        NOTA: O DataFrame completo está disponível como 'df' com {df.shape[0]} linhas.
                        Use df diretamente no código, não precisa incluir todos os dados aqui.
                        """
                        
                        csv_data = True
                        data_context = csv_summary
                        
                        st.write(f"✅ Arquivo {file_type} carregado: **{uploaded_file.name}** ({df.shape[0]} linhas, {df.shape[1]} colunas)")
                        st.write(f"📊 Colunas: {', '.join(df.columns.tolist())}")
                        
                        # Mostra preview dos dados
                        with st.expander("👁️ Preview dos Dados", expanded=False):
                            st.dataframe(df.head(10), use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Erro ao ler o arquivo: {e}")
                        status.update(label="Erro ao processar arquivo", state="error")
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
                    Você é um Data Scientist Senior Especialista em Streamlit e Visualização de Dados.
                    O usuário forneceu um arquivo com os seguintes dados:
                    
                    {csv_summary}
                    
                    {columns_info}
                    
                    REGRAS CRÍTICAS: 
                    - O DataFrame já está carregado e disponível APENAS como variável 'df' (não 'data_df', não 'df_data', apenas 'df').
                    - NÃO crie novas variáveis de DataFrame. Use APENAS 'df'.
                    - NÃO tente ler o arquivo novamente usando pd.read_csv() ou pd.read_excel().
                    - Use APENAS a variável 'df' que já contém todos os dados.
                    - Use APENAS as colunas listadas acima. Verifique se a coluna existe antes de usá-la.
                    - Se uma coluna tiver espaços, use df['Nome da Coluna'] (com aspas).
                    - Sempre verifique se as colunas existem: if 'coluna' in df.columns:
                    - NÃO renomeie o DataFrame. Use 'df' diretamente.
                    
                    Crie um script Python COMPLETO usando 'streamlit' para gerar um DASHBOARD SUPER BONITO, INTUITIVO E DINÂMICO:
                    
                    DESIGN E LAYOUT:
                    - Use st.columns para criar um layout responsivo e organizado
                    - Adicione títulos e subtítulos com st.title(), st.header(), st.subheader()
                    - Use st.metric() para KPIs principais com formatação bonita (valores grandes, cores, delta)
                    - Adicione separadores visuais com st.divider() ou st.markdown("---")
                    - Use cores e formatação markdown para destacar informações importantes
                    
                    VISUALIZAÇÕES:
                    - Identifique automaticamente colunas numéricas e categóricas
                    - Crie gráficos adaptativos baseados nos tipos de dados disponíveis:
                      * Para dados temporais: gráficos de linha ou área
                      * Para comparações: gráficos de barras ou colunas
                      * Para distribuições: histogramas ou box plots
                      * Para correlações: heatmaps ou scatter plots
                    - Use plotly.express para gráficos interativos e bonitos (px.bar, px.line, px.scatter, px.histogram, etc)
                    - Se plotly não estiver disponível, use st.bar_chart, st.line_chart, st.area_chart
                    - Adicione títulos descritivos aos gráficos
                    
                    KPIs E MÉTRICAS:
                    - Calcule automaticamente métricas relevantes baseadas nas colunas disponíveis
                    - Exiba KPIs principais em cards visuais no topo usando st.metric()
                    - Formate números grandes com separadores de milhar e casas decimais apropriadas
                    - Adicione indicadores de tendência (delta) quando possível
                    
                    INTERATIVIDADE:
                    - Adicione filtros com st.selectbox, st.multiselect ou st.slider quando apropriado
                    - Permita que o usuário explore os dados de forma interativa
                    - Mostre tabelas interativas com st.dataframe() quando relevante
                    
                    ADAPTAÇÃO AUTOMÁTICA:
                    - O dashboard deve se adaptar automaticamente à estrutura da planilha
                    - Se houver colunas de data/tempo, use-as para análises temporais
                    - Se houver colunas categóricas, crie agrupamentos e comparações
                    - Se houver colunas numéricas, calcule estatísticas e tendências
                    - Se a planilha tiver muitas colunas, foque nas mais importantes
                    
                    CÓDIGO:
                    - O código deve ser autocontido e executável
                    - Sempre verifique se as colunas existem antes de usá-las
                    - Trate valores nulos e dados faltantes adequadamente
                    - Use try/except para evitar erros se colunas não existirem
                    - NÃO inclua linhas como: df = pd.read_csv() ou data_df = df.copy()
                    - Use diretamente: df.head(), df['coluna'], df.describe(), etc.
                    - Importe todas as bibliotecas necessárias (pandas, plotly, streamlit, numpy se necessário)
                    
                    EXEMPLO DE ESTRUTURA:
                    ```python
                    import streamlit as st
                    import pandas as pd
                    import plotly.express as px
                    import plotly.graph_objects as go
                    
                    # Título principal
                    st.title("📊 Dashboard de Análise")
                    
                    # KPIs no topo
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total", df.shape[0], delta=None)
                    # ... mais KPIs
                    
                    # Filtros interativos
                    # ... filtros se necessário
                    
                    # Gráficos
                    st.subheader("Visualizações")
                    # ... gráficos adaptativos
                    
                    # Tabela de dados
                    st.subheader("Dados Detalhados")
                    st.dataframe(df, use_container_width=True)
                    ```
                    """
                else:
                    inputs['definicao_do_sistema'] = f"""
                    Você é um Data Scientist Senior Especialista em Streamlit e Visualização de Dados.
                    Sua tarefa é analisar os seguintes dados: "{data_context}".
                    
                    Crie um script Python COMPLETO usando 'streamlit' para gerar um DASHBOARD SUPER BONITO, INTUITIVO E DINÂMICO:
                    
                    - Use st.columns para criar layout responsivo
                    - Use st.metric() para KPIs principais com formatação bonita
                    - Crie gráficos interativos com plotly.express (px.bar, px.line, px.scatter, etc)
                    - Adicione títulos, subtítulos e separadores visuais
                    - Use cores e formatação markdown para destacar informações
                    - Adicione filtros interativos quando apropriado
                    - O código deve ser autocontido e executável
                    - Importe todas as bibliotecas necessárias
                    """
                
                try:
                    # Prepara a requisição para o backend usando a definição já criada
                    payload = {
                        "data_context": str(data_context),
                        "topic": inputs.get('topic', 'Análise de Dados de Marketing'),
                        "definicao_do_sistema": inputs.get('definicao_do_sistema', '')
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
                            dependencies_to_check = ['plotly', 'pandas', 'openpyxl']
                            for dep in dependencies_to_check:
                                try:
                                    __import__(dep)
                                except ImportError:
                                    st.info(f"📦 Instalando {dep}...")
                                    try:
                                        subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "-q"], 
                                                             stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                                        st.success(f"✅ {dep} instalado com sucesso!")
                                    except:
                                        st.warning(f"⚠️ Não foi possível instalar {dep} automaticamente. Algumas funcionalidades podem não estar disponíveis.")
                            
                            # Se houver CSV, disponibiliza o DataFrame no contexto de execução
                            if csv_data and df is not None:
                                # Usa o DataFrame já carregado anteriormente (não precisa recarregar)
                                # Remove qualquer tentativa de ler o arquivo do código gerado
                                import re
                                
                                # Remove linhas problemáticas do código gerado
                                code_lines = code_to_run.split('\n')
                                filtered_lines = []
                                for line in code_lines:
                                    # Remove linhas que tentam ler arquivos (CSV ou Excel)
                                    if ('pd.read_csv' in line or 'pd.read_excel' in line) and ('uploaded_file' not in line.lower() and 'io.BytesIO' not in line):
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
                                # Importa bibliotecas necessárias para o contexto de execução
                                try:
                                    import plotly.express as px
                                    import plotly.graph_objects as go
                                    plotly_available = True
                                except ImportError:
                                    plotly_available = False
                                    px = None
                                    go = None
                                
                                try:
                                    import numpy as np
                                except ImportError:
                                    np = None
                                
                                exec_globals = {
                                    'pd': pd,
                                    'pandas': pd,
                                    'st': st,
                                    'streamlit': st,
                                    'df': df,  # Usa o DataFrame já carregado
                                    'np': np,
                                    'numpy': np,
                                }
                                
                                # Adiciona plotly se disponível
                                if plotly_available:
                                    exec_globals['px'] = px
                                    exec_globals['plotly'] = __import__('plotly')
                                    exec_globals['go'] = go
                                
                                # Remove None do dict
                                exec_globals = {k: v for k, v in exec_globals.items() if v is not None}
                                
                                exec(code_to_run, exec_globals) # Executa o código gerado na tela
                            else:
                                # Para dados de texto, executa normalmente
                                try:
                                    import plotly.express as px
                                    import plotly.graph_objects as go
                                    plotly_available = True
                                except ImportError:
                                    plotly_available = False
                                    px = None
                                    go = None
                                
                                try:
                                    import numpy as np
                                except ImportError:
                                    np = None
                                
                                exec_globals = {
                                    'pd': pd,
                                    'pandas': pd,
                                    'st': st,
                                    'streamlit': st,
                                    'np': np,
                                    'numpy': np,
                                }
                                
                                if plotly_available:
                                    exec_globals['px'] = px
                                    exec_globals['plotly'] = __import__('plotly')
                                    exec_globals['go'] = go
                                
                                exec_globals = {k: v for k, v in exec_globals.items() if v is not None}
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