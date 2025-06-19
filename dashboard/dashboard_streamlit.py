import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import time
import sys
import os

# Importa as configurações do banco
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.database_config import _config as DatabaseConfig, conectar_postgres

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização precoce do session_state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"

if 'crud_opcao' not in st.session_state:
    st.session_state.crud_opcao = "Selecione uma operação..."

if 'analytics_opcao' not in st.session_state:
    st.session_state.analytics_opcao = "Selecione uma análise..."

# URL do servidor Flask local
FLASK_SERVER_URL = "http://127.0.0.1:8000/get_data"

# === FUNÇÕES CRUD PARA STREAMLIT ===

def crud_inserir_dados():
    """Interface Streamlit para inserir novos dados"""
    st.subheader("📥 Inserir Nova Leitura")
    
    with st.form("inserir_dados_form"):
        # Data/hora
        col1, col2 = st.columns(2)
        with col1:
            usar_atual = st.checkbox("Usar data/hora atual", value=True)
        with col2:
            if not usar_atual:
                data_hora = st.datetime_input("Data/Hora da Leitura", datetime.now())
            else:
                data_hora = datetime.now()
        
        # Sensores
        col1, col2, col3 = st.columns(3)
        with col1:
            umidade = st.number_input("Umidade (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
        with col2:
            temperatura = st.number_input("Temperatura (°C)", min_value=-50.0, max_value=70.0, value=25.0, step=0.1)
        with col3:
            ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
        
        # Estados
        col1, col2, col3 = st.columns(3)
        with col1:
            fosforo = st.selectbox("Fósforo", ["Ausente", "Presente"]) == "Presente"
        with col2:
            potassio = st.selectbox("Potássio", ["Ausente", "Presente"]) == "Presente"
        with col3:
            bomba = st.selectbox("Bomba", ["Desligada", "Ligada"]) == "Ligada"
        
        submitted = st.form_submit_button("✅ Inserir Dados")
        
        if submitted:
            try:
                conn, cursor = conectar_postgres()
                if conn:
                    cursor.execute(f"""
                        INSERT INTO {DatabaseConfig.SCHEMA}.leituras_sensores 
                        (data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (data_hora, umidade, temperatura, ph, fosforo, potassio, bomba))
                    conn.commit()
                    st.success("✅ Dados inseridos com sucesso!")
                    st.balloons()
                    cursor.close()
                    conn.close()
                    st.cache_data.clear()  # Limpa cache para mostrar novos dados
                else:
                    st.error("❌ Erro ao conectar com o banco de dados")
            except Exception as e:
                st.error(f"❌ Erro ao inserir dados: {e}")

def crud_listar_dados():
    """Interface Streamlit para listar dados"""
    st.subheader("📄 Gerenciar Leituras")
    
    try:
        conn, cursor = conectar_postgres()
        if conn:
            cursor.execute(f"""
                SELECT id, data_hora_leitura, criacaots, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                ORDER BY data_hora_leitura DESC
                LIMIT 50
            """)
            rows = cursor.fetchall()
            
            if rows:
                # Converte para DataFrame
                df = pd.DataFrame(rows, columns=[
                    'ID', 'Data/Hora Leitura', 'Criação', 'Umidade', 'Temperatura', 
                    'pH', 'Fósforo', 'Potássio', 'Bomba'
                ])
                
                # Formata as colunas boolean
                df['Fósforo'] = df['Fósforo'].apply(lambda x: "✅ Presente" if x else "❌ Ausente")
                df['Potássio'] = df['Potássio'].apply(lambda x: "✅ Presente" if x else "❌ Ausente")
                df['Bomba'] = df['Bomba'].apply(lambda x: "✅ Ligada" if x else "❌ Desligada")
                
                st.dataframe(df, use_container_width=True, height=400)
                st.info(f"📊 Mostrando últimos 50 registros de {len(rows)} encontrados")
            else:
                st.warning("⚠️ Nenhum dado encontrado")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"❌ Erro ao listar dados: {e}")

def crud_atualizar_dados():
    """Interface Streamlit para atualizar dados"""
    st.subheader("✏️ Atualizar Leitura")
    
    # Busca registros para seleção
    try:
        conn, cursor = conectar_postgres()
        if conn:
            cursor.execute(f"""
                SELECT id, data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                ORDER BY data_hora_leitura DESC
                LIMIT 20
            """)
            registros = cursor.fetchall()
            
            if registros:
                # Cria opções para o selectbox
                opcoes = []
                for reg in registros:
                    data_formatada = reg[1].strftime("%Y-%m-%d %H:%M:%S") if reg[1] else "N/A"
                    opcoes.append(f"ID {reg[0]} - {data_formatada} (T:{reg[3]}°C, H:{reg[2]}%)")
                
                registro_selecionado = st.selectbox("Selecione o registro para atualizar:", opcoes)
                
                if registro_selecionado:
                    # Extrai o ID do registro selecionado
                    id_registro = int(registro_selecionado.split(" ")[1])
                    
                    # Busca dados atuais do registro
                    cursor.execute(f"""
                        SELECT umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                        FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                        WHERE id = %s
                    """, (id_registro,))
                    dados_atuais = cursor.fetchone()
                    
                    if dados_atuais:
                        with st.form("atualizar_dados_form"):
                            st.info(f"📋 Atualizando registro ID: {id_registro}")
                            
                            # Campos com valores atuais
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                nova_umidade = st.number_input("Nova Umidade (%)", 
                                                             min_value=0.0, max_value=100.0, 
                                                             value=float(dados_atuais[0]), step=0.1)
                            with col2:
                                nova_temperatura = st.number_input("Nova Temperatura (°C)", 
                                                                 min_value=-50.0, max_value=70.0, 
                                                                 value=float(dados_atuais[1]), step=0.1)
                            with col3:
                                novo_ph = st.number_input("Novo pH", 
                                                        min_value=0.0, max_value=14.0, 
                                                        value=float(dados_atuais[2]), step=0.1)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                novo_fosforo = st.selectbox("Novo Fósforo", 
                                                          ["Ausente", "Presente"], 
                                                          index=1 if dados_atuais[3] else 0) == "Presente"
                            with col2:
                                novo_potassio = st.selectbox("Novo Potássio", 
                                                           ["Ausente", "Presente"], 
                                                           index=1 if dados_atuais[4] else 0) == "Presente"
                            with col3:
                                nova_bomba = st.selectbox("Nova Bomba", 
                                                        ["Desligada", "Ligada"], 
                                                        index=1 if dados_atuais[5] else 0) == "Ligada"
                            
                            submitted = st.form_submit_button("✅ Atualizar Registro")
                            
                            if submitted:
                                try:
                                    cursor.execute(f"""
                                        UPDATE {DatabaseConfig.SCHEMA}.leituras_sensores
                                        SET umidade = %s, temperatura = %s, ph = %s, fosforo = %s, potassio = %s, bomba_dagua = %s
                                        WHERE id = %s
                                    """, (nova_umidade, nova_temperatura, novo_ph, novo_fosforo, novo_potassio, nova_bomba, id_registro))
                                    
                                    if cursor.rowcount > 0:
                                        conn.commit()
                                        st.success("✅ Registro atualizado com sucesso!")
                                        st.cache_data.clear()
                                    else:
                                        st.warning("⚠️ Nenhum registro foi atualizado")
                                except Exception as e:
                                    st.error(f"❌ Erro ao atualizar: {e}")
            else:
                st.warning("⚠️ Nenhum registro encontrado")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"❌ Erro ao buscar registros: {e}")

def crud_remover_dados():
    """Interface Streamlit para remover dados"""
    st.subheader("🗑️ Remover Leitura")
    
    try:
        conn, cursor = conectar_postgres()
        if conn:
            cursor.execute(f"""
                SELECT id, data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                ORDER BY data_hora_leitura DESC
                LIMIT 20
            """)
            registros = cursor.fetchall()
            
            if registros:
                # Cria opções para o selectbox
                opcoes = ["Selecione um registro..."]
                for reg in registros:
                    data_formatada = reg[1].strftime("%Y-%m-%d %H:%M:%S") if reg[1] else "N/A"
                    opcoes.append(f"ID {reg[0]} - {data_formatada} (T:{reg[3]}°C, H:{reg[2]}%)")
                
                registro_selecionado = st.selectbox("Selecione o registro para remover:", opcoes)
                
                if registro_selecionado != opcoes[0]:
                    # Extrai o ID do registro selecionado
                    id_registro = int(registro_selecionado.split(" ")[1])
                    
                    # Busca dados completos do registro
                    cursor.execute(f"""
                        SELECT id, data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua
                        FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                        WHERE id = %s
                    """, (id_registro,))
                    registro = cursor.fetchone()
                    
                    if registro:
                        st.warning("⚠️ Registro a ser removido:")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info(f"**ID:** {registro[0]}")
                            st.info(f"**Data/Hora:** {registro[1]}")
                            st.info(f"**Umidade:** {registro[2]}%")
                            st.info(f"**Temperatura:** {registro[3]}°C")
                        
                        with col2:
                            st.info(f"**pH:** {registro[4]}")
                            st.info(f"**Fósforo:** {'✅ Presente' if registro[5] else '❌ Ausente'}")
                            st.info(f"**Potássio:** {'✅ Presente' if registro[6] else '❌ Ausente'}")
                            st.info(f"**Bomba:** {'✅ Ligada' if registro[7] else '❌ Desligada'}")
                        
                        # Confirmação
                        confirmar = st.checkbox("⚠️ Confirmo que desejo remover este registro")
                        
                        if confirmar and st.button("🗑️ REMOVER REGISTRO", type="primary"):
                            try:
                                cursor.execute(f"DELETE FROM {DatabaseConfig.SCHEMA}.leituras_sensores WHERE id = %s", (id_registro,))
                                if cursor.rowcount > 0:
                                    conn.commit()
                                    st.success("✅ Registro removido com sucesso!")
                                    st.cache_data.clear()
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Nenhum registro foi removido")
                            except Exception as e:
                                st.error(f"❌ Erro ao remover: {e}")
            else:
                st.warning("⚠️ Nenhum registro encontrado")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"❌ Erro ao buscar registros: {e}")

def crud_estatisticas():
    """Interface Streamlit para mostrar estatísticas"""
    st.subheader("📊 Estatísticas dos Dados")
    
    try:
        conn, cursor = conectar_postgres()
        if conn:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_registros,
                    AVG(umidade) as umidade_media,
                    MIN(umidade) as umidade_min,
                    MAX(umidade) as umidade_max,
                    AVG(temperatura) as temp_media,
                    MIN(temperatura) as temp_min,
                    MAX(temperatura) as temp_max,
                    AVG(ph) as ph_medio,
                    MIN(ph) as ph_min,
                    MAX(ph) as ph_max
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores
            """)
            stats = cursor.fetchone()
            
            if stats and stats[0] > 0:
                # Métricas principais
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total de Registros", f"{stats[0]:,}")
                
                with col2:
                    st.metric("💧 Umidade Média", f"{stats[1]:.1f}%")
                
                with col3:
                    st.metric("🌡️ Temperatura Média", f"{stats[4]:.1f}°C")
                
                with col4:
                    st.metric("⚗️ pH Médio", f"{stats[7]:.1f}")
                
                # Estatísticas detalhadas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info("💧 **UMIDADE**")
                    st.write(f"Média: {stats[1]:.1f}%")
                    st.write(f"Mínima: {stats[2]:.1f}%")
                    st.write(f"Máxima: {stats[3]:.1f}%")
                
                with col2:
                    st.info("🌡️ **TEMPERATURA**")
                    st.write(f"Média: {stats[4]:.1f}°C")
                    st.write(f"Mínima: {stats[5]:.1f}°C")
                    st.write(f"Máxima: {stats[6]:.1f}°C")
                
                with col3:
                    st.info("⚗️ **pH**")
                    st.write(f"Médio: {stats[7]:.1f}")
                    st.write(f"Mínimo: {stats[8]:.1f}")
                    st.write(f"Máximo: {stats[9]:.1f}")
                
            else:
                st.warning("⚠️ Nenhum dado disponível para estatísticas")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"❌ Erro ao calcular estatísticas: {e}")

def crud_consulta_umidade():
    """Interface Streamlit para consulta por umidade"""
    st.subheader("🔎 Consulta por Umidade")
    
    col1, col2 = st.columns(2)
    with col1:
        limite = st.number_input("Valor de referência (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
    with col2:
        condicao = st.selectbox("Condição", ["acima", "abaixo"])
    
    if st.button("🔍 Buscar"):
        try:
            conn, cursor = conectar_postgres()
            if conn:
                if condicao == 'acima':
                    cursor.execute(f"""
                        SELECT id, data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                        FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                        WHERE umidade > %s 
                        ORDER BY data_hora_leitura DESC
                    """, (limite,))
                else:
                    cursor.execute(f"""
                        SELECT id, data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                        FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                        WHERE umidade < %s 
                        ORDER BY data_hora_leitura DESC
                    """, (limite,))
                
                rows = cursor.fetchall()
                
                if rows:
                    st.success(f"🔍 Encontrados {len(rows)} registros com umidade {condicao} de {limite}%")
                    
                    # Converte para DataFrame
                    df = pd.DataFrame(rows, columns=[
                        'ID', 'Data/Hora', 'Umidade', 'Temperatura', 'pH', 'Fósforo', 'Potássio', 'Bomba'
                    ])
                    
                    # Formata as colunas boolean
                    df['Fósforo'] = df['Fósforo'].apply(lambda x: "✅" if x else "❌")
                    df['Potássio'] = df['Potássio'].apply(lambda x: "✅" if x else "❌")
                    df['Bomba'] = df['Bomba'].apply(lambda x: "✅" if x else "❌")
                    
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("⚠️ Nenhum registro encontrado com esse critério")
                
                cursor.close()
                conn.close()
        except Exception as e:
            st.error(f"❌ Erro na consulta: {e}")

# === FUNÇÕES PARA ANÁLISE ESTATÍSTICA COM R ===

def exportar_dados_para_r():
    """Exporta dados do PostgreSQL para CSV que será usado pelo R"""
    try:
        conn, cursor = conectar_postgres()
        if conn:
            # Query para buscar todos os dados necessários para análise
            cursor.execute(f"""
                SELECT data_hora_leitura as timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                ORDER BY data_hora_leitura
            """)
            rows = cursor.fetchall()
            
            if rows:
                # Converte para DataFrame
                df = pd.DataFrame(rows, columns=[
                    'timestamp', 'umidade', 'temperatura', 'ph', 'fosforo', 'potassio', 'bomba_dagua'
                ])
                
                # Salva no diretório de análise estatística
                output_path = os.path.join(parent_dir, 'analise_estatistica', 'leituras_sensores.csv')
                df.to_csv(output_path, index=False)
                
                st.success(f"✅ Dados exportados com sucesso! {len(rows)} registros salvos em:")
                st.code(output_path)
                return True
            else:
                st.warning("⚠️ Nenhum dado encontrado para exportar")
                return False
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"❌ Erro ao exportar dados: {e}")
        return False

def executar_script_r():
    """Executa o script R de análise estatística"""
    try:
        # Caminho para o script R
        script_path = os.path.join(parent_dir, 'analise_estatistica', 'AnaliseEstatisticaBD.R')
        analise_dir = os.path.join(parent_dir, 'analise_estatistica')
        
        if not os.path.exists(script_path):
            st.error(f"❌ Script R não encontrado: {script_path}")
            return False
            
        # Executa o script R
        import subprocess
        
        with st.spinner("🔄 Executando análise estatística com R..."):
            result = subprocess.run(['Rscript', script_path], 
                                  cwd=analise_dir,
                                  capture_output=True, 
                                  text=True,
                                  timeout=60)
        
        if result.returncode == 0:
            st.success("✅ Análise R executada com sucesso!")
            if result.stdout:
                st.text("📋 Output do R:")
                st.code(result.stdout)
            return True
        else:
            st.error("❌ Erro na execução do script R:")
            st.code(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        st.error("❌ Timeout: Script R demorou mais de 60 segundos")
        return False
    except FileNotFoundError:
        st.error("❌ R não encontrado no sistema. Certifique-se de que o R está instalado e no PATH")
        return False
    except Exception as e:
        st.error(f"❌ Erro ao executar script R: {e}")
        return False

def mostrar_resumo_estatistico():
    """Mostra o resumo estatístico gerado pelo R"""
    try:
        resumo_path = os.path.join(parent_dir, 'analise_estatistica', 'resumo_estatistico.csv')
        
        if os.path.exists(resumo_path):
            df_resumo = pd.read_csv(resumo_path)
            st.subheader("📊 Resumo Estatístico (Gerado pelo R)")
            st.dataframe(df_resumo, use_container_width=True)
            
            # Botão para download
            csv_data = df_resumo.to_csv(index=False)
            st.download_button(
                label="📥 Download Resumo Estatístico",
                data=csv_data,
                file_name="resumo_estatistico.csv",
                mime="text/csv"
            )
            return True
        else:
            st.warning("⚠️ Arquivo de resumo estatístico não encontrado. Execute a análise primeiro.")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro ao ler resumo estatístico: {e}")
        return False

def verificar_ambiente_r():
    """Verifica se o ambiente R está configurado corretamente"""
    try:
        import subprocess
        result = subprocess.run(['R', '--version'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            st.success("✅ R está instalado e funcionando")
            st.text("📋 Versão do R:")
            st.code(result.stdout.split('\n')[0])
            return True
        else:
            st.error("❌ Problema com a instalação do R")
            return False
            
    except FileNotFoundError:
        st.error("❌ R não encontrado. Instale o R para usar as análises estatísticas.")
        st.markdown("""
        **Como instalar o R:**
        - **macOS**: `brew install r` ou baixe de https://cran.r-project.org/
        - **Ubuntu**: `sudo apt-get install r-base`
        - **Windows**: Baixe de https://cran.r-project.org/
        """)
        return False
    except Exception as e:
        st.error(f"❌ Erro ao verificar R: {e}")
        return False

def pagina_analytics_r():
    """Página dedicada à análise estatística com R"""
    st.title("🤖 Análise Estatística com R")
    st.markdown("**Análise preditiva e estatística usando linguagem R**")
    
    # Botão para voltar ao dashboard
    if st.button("🏠 Voltar ao Dashboard", type="primary"):
        st.session_state.current_page = "dashboard"
        st.session_state.analytics_opcao = "Selecione uma análise..."
        st.rerun()
    
    st.markdown("---")
    
    # Informações do sistema
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"🏗️ **Schema:** {DatabaseConfig.SCHEMA}")
    with col2:
        st.info(f"📊 **Linguagem:** R + Python")
    with col3:
        st.info(f"📁 **Pasta:** analise_estatistica/")
    
    st.markdown("---")
    
    # Verificação do ambiente R
    st.subheader("🔍 Verificação do Ambiente")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Verificar Instalação do R", use_container_width=True):
            verificar_ambiente_r()
    
    with col2:
        if st.button("📤 Exportar Dados para R", use_container_width=True):
            exportar_dados_para_r()
    
    st.markdown("---")
    
    # Seleção de análises
    analytics_opcao = st.selectbox(
        "**Selecione a análise desejada:**",
        [
            "Selecione uma análise...",
            "📊 Executar Análise Estatística Completa",
            "📈 Ver Resumo Estatístico",
            "📋 Status dos Arquivos R",
            "🔧 Configurar Ambiente R"
        ],
        key="analytics_page_selectbox"
    )
    
    st.markdown("---")
    
    # Executa a operação selecionada
    if analytics_opcao == "📊 Executar Análise Estatística Completa":
        st.subheader("📊 Análise Estatística Completa")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("1️⃣ Exportar Dados", use_container_width=True):
                exportar_dados_para_r()
        
        with col2:
            if st.button("2️⃣ Executar Script R", use_container_width=True):
                if executar_script_r():
                    st.balloons()
        
        st.markdown("---")
        st.info("💡 **Processo completo:** 1) Exporte os dados → 2) Execute o script R → 3) Veja os resultados")
        
    elif analytics_opcao == "📈 Ver Resumo Estatístico":
        mostrar_resumo_estatistico()
        
    elif analytics_opcao == "📋 Status dos Arquivos R":
        st.subheader("📋 Status dos Arquivos R")
        
        # Verifica arquivos na pasta analise_estatistica
        analise_dir = os.path.join(parent_dir, 'analise_estatistica')
        
        arquivos_r = {
            "AnaliseEstatisticaBD.R": "Script principal de análise",
            "leituras_sensores.csv": "Dados exportados para análise",
            "resumo_estatistico.csv": "Resumo gerado pelo R",
            "requirements.txt": "Dependências R"
        }
        
        for arquivo, descricao in arquivos_r.items():
            arquivo_path = os.path.join(analise_dir, arquivo)
            if os.path.exists(arquivo_path):
                st.success(f"✅ **{arquivo}** - {descricao}")
            else:
                st.error(f"❌ **{arquivo}** - {descricao} (não encontrado)")
        
    elif analytics_opcao == "🔧 Configurar Ambiente R":
        st.subheader("🔧 Configuração do Ambiente R")
        
        st.markdown("""
        **Pacotes R necessários:**
        ```r
        install.packages(c("readr", "dplyr", "ggplot2", "lubridate", "forecast"))
        ```
        
        **Para instalar os pacotes automaticamente:**
        """)
        
        if st.button("📦 Instalar Pacotes R", use_container_width=True):
            try:
                import subprocess
                
                # Script R melhorado para instalação
                install_script = '''
                # Função para instalar pacotes
                install_and_load <- function(package) {
                  if (!require(package, character.only = TRUE, quietly = TRUE)) {
                    cat("Instalando pacote:", package, "\\n")
                    install.packages(package, repos = "https://cran.rstudio.com/")
                    if (require(package, character.only = TRUE, quietly = TRUE)) {
                      cat("✅", package, "instalado com sucesso\\n")
                    } else {
                      cat("❌ Erro ao instalar", package, "\\n")
                    }
                  } else {
                    cat("✅", package, "já está instalado\\n")
                  }
                }

                # Instalar pacotes necessários
                packages <- c("readr", "dplyr", "ggplot2", "lubridate", "forecast")
                cat("=== INSTALANDO PACOTES R ===\\n")
                
                for (pkg in packages) {
                  install_and_load(pkg)
                }
                
                cat("=== INSTALAÇÃO CONCLUÍDA ===\\n")
                '''
                
                install_cmd = ['Rscript', '-e', install_script]
                
                with st.spinner("📦 Instalando pacotes R... (pode demorar alguns minutos)"):
                    result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    st.success("✅ Pacotes R instalados com sucesso!")
                    st.text("📋 Log da instalação:")
                    st.code(result.stdout)
                else:
                    st.error("❌ Erro na instalação dos pacotes:")
                    st.code(result.stderr)
                    st.info("💡 Tente executar manualmente no R: install.packages(c('readr', 'dplyr', 'ggplot2', 'lubridate', 'forecast'))")
            except subprocess.TimeoutExpired:
                st.error("❌ Timeout: Instalação demorou mais de 5 minutos")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
        
    else:
        st.info("👆 Selecione uma análise no menu acima para começar")
        
        # Preview da estrutura do projeto R
        st.subheader("📁 Estrutura do Projeto R")
        st.markdown("""
        ```
        analise_estatistica/
        ├── 📄 AnaliseEstatisticaBD.R       # Script principal
        ├── 📊 leituras_sensores.csv        # Dados para análise  
        ├── 📈 resumo_estatistico.csv       # Resultados gerados
        ├── 📦 requirements.txt             # Dependências R
        └── 📋 README.md                    # Documentação
        ```
        
        **Funcionalidades disponíveis:**
        - ✅ Estatísticas descritivas
        - ✅ Correlações entre variáveis
        - ✅ Visualizações com ggplot2
        - ✅ Previsões ARIMA para umidade
        - ✅ Análise de séries temporais
        """)

def pagina_crud():
    """Página dedicada ao CRUD"""
    st.title("🗃️ Gerenciamento de Registros")
    st.markdown("**Operações do Banco de Dados PostgreSQL**")
    
    # Botão para voltar ao dashboard
    if st.button("🏠 Voltar ao Dashboard", type="primary"):
        st.session_state.current_page = "dashboard"
        st.session_state.crud_opcao = "Selecione uma operação..."
        st.rerun()
    
    st.markdown("---")
    
    # Informações do banco
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"🏗️ **Schema:** {DatabaseConfig.SCHEMA}")
    with col2:
        st.info(f"🖥️ **Host:** {DatabaseConfig.HOST}")
    with col3:
        st.info(f"💾 **Database:** {DatabaseConfig.DATABASE}")
    
    st.markdown("---")
    
    # Seleção de operação CRUD
    crud_opcao = st.selectbox(
        "**Selecione a operação desejada:**",
        [
            "Selecione uma operação...",
            "📥 Inserir Nova Leitura",
            "📄 Gerenciar Leituras",
            "✏️ Atualizar Leitura",
            "🗑️ Remover Leitura",
            "📊 Estatísticas dos Dados",
            "🔎 Consulta por Umidade"
        ],
        key="crud_page_selectbox"
    )
    
    st.markdown("---")
    
    # Executa a operação selecionada
    if crud_opcao == "📥 Inserir Nova Leitura":
        crud_inserir_dados()
    elif crud_opcao == "📄 Gerenciar Leituras":
        crud_listar_dados()
    elif crud_opcao == "✏️ Atualizar Leitura":
        crud_atualizar_dados()
    elif crud_opcao == "🗑️ Remover Leitura":
        crud_remover_dados()
    elif crud_opcao == "📊 Estatísticas dos Dados":
        crud_estatisticas()
    elif crud_opcao == "🔎 Consulta por Umidade":
        crud_consulta_umidade()
    else:
        st.info("👆 Selecione uma operação no menu acima para começar")
        
        # Mostra preview das últimas leituras
        st.subheader("📊 Últimas Leituras (Preview)")
        try:
            conn, cursor = conectar_postgres()
            if conn:
                cursor.execute(f"""
                    SELECT id, data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                    FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                    ORDER BY data_hora_leitura DESC
                    LIMIT 5
                """)
                rows = cursor.fetchall()
                
                if rows:
                    df = pd.DataFrame(rows, columns=[
                        'ID', 'Data/Hora', 'Umidade (%)', 'Temp (°C)', 'pH', 'Fósforo', 'Potássio', 'Bomba'
                    ])
                    
                    # Formata as colunas boolean
                    df['Fósforo'] = df['Fósforo'].apply(lambda x: "✅" if x else "❌")
                    df['Potássio'] = df['Potássio'].apply(lambda x: "✅" if x else "❌")
                    df['Bomba'] = df['Bomba'].apply(lambda x: "✅" if x else "❌")
                    
                    st.dataframe(df, use_container_width=True)
                    st.caption("Mostrando apenas os 5 registros mais recentes")
                else:
                    st.warning("⚠️ Nenhum registro encontrado")
                
                cursor.close()
                conn.close()
        except Exception as e:
            st.error(f"❌ Erro ao buscar dados: {e}")

# --- Função para consultar a API do tempo ---
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_clima_atual():
    """Obtém dados climáticos simulados (API desabilitada temporariamente)"""
    # API_KEY = "SUA_API_KEY_AQUI"  # <-- Para usar a API real, substitua pela sua chave da OpenWeatherMap
    # CIDADE = "Camopi"
    # URL = f"https://api.openweathermap.org/data/2.5/weather?q={CIDADE}&appid={API_KEY}&units=metric&lang=pt_br"
    
    # VERSÃO SIMULADA - Para usar API real, descomente o código acima e comente este bloco
    try:
        # Retorna dados simulados para demonstração
        import random
        from datetime import datetime
        
        # Simula condições climáticas variáveis
        temp_base = 28
        temp_variacao = random.uniform(-3, 3)
        temperatura_atual = round(temp_base + temp_variacao, 1)
        
        umidade_atual = random.randint(60, 85)
        
        condicoes = ["Ensolarado", "Parcialmente nublado", "Nublado", "Céu limpo"]
        condicao_atual = random.choice(condicoes)
        
        vento_atual = round(random.uniform(2, 8), 1)
        
        # 20% de chance de chuva para demonstrar o alerta
        vai_chover_hoje = random.random() < 0.2
        chuva_atual = round(random.uniform(0.5, 5.0), 1) if vai_chover_hoje else 0.0

        clima = {
            'cidade': 'Camopi (Simulado)',
            'temperatura': temperatura_atual,
            'umidade': umidade_atual,
            'condicao': condicao_atual,
            'vento': vento_atual,
            'chuva': chuva_atual,
            'vai_chover': vai_chover_hoje
        }

        return clima

    except Exception as e:
        st.warning(f"⚠️ API climática temporariamente indisponível. Usando dados simulados.")
        return {
            'cidade': 'Camopi (Simulado)',
            'temperatura': 26.5,
            'umidade': 72,
            'condicao': 'Parcialmente nublado',
            'vento': 4.2,
            'chuva': 0.0,
            'vai_chover': False
        }
    
    # CÓDIGO PARA USO REAL DA API (descomente para usar):
    # try:
    #     response = requests.get(URL, timeout=5)
    #     response.raise_for_status()
    #     dados = response.json()
    #
    #     clima = {
    #         'cidade': dados.get("name", "Desconhecida"),
    #         'temperatura': dados.get("main", {}).get("temp", "N/A"),
    #         'umidade': dados.get("main", {}).get("humidity", "N/A"),
    #         'condicao': dados.get("weather", [{}])[0].get("description", "N/A").capitalize(),
    #         'vento': dados.get("wind", {}).get("speed", "N/A"),
    #         'chuva': dados.get("rain", {}).get("1h", 0.0)
    #     }
    #
    #     clima['vai_chover'] = clima['chuva'] > 0
    #     return clima
    #
    # except Exception as e:
    #     st.error(f"Erro ao consultar clima: {e}")
    #     return {
    #         'cidade': 'Erro',
    #         'temperatura': 'N/A',
    #         'umidade': 'N/A',
    #         'condicao': 'Erro ao consultar clima',
    #         'vento': 'N/A',
    #         'chuva': 'N/A',
    #         'vai_chover': False
    #     }

# --- Função para obter os dados do Flask ---
@st.cache_data(ttl=2)  # Cache por 2 segundos para refresh mais rápido
def get_sensor_data():
    """Obtém dados dos sensores do servidor Flask"""
    try:
        response = requests.get(FLASK_SERVER_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'dados' in data and data['dados']:
            return data
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com o servidor Flask: {e}")
        return None

def init_session_state():
    """Inicializa as variáveis do session_state"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    if 'crud_opcao' not in st.session_state:
        st.session_state.crud_opcao = "Selecione uma operação..."
    
    if 'analytics_opcao' not in st.session_state:
        st.session_state.analytics_opcao = "Selecione uma análise..."

# --- Interface principal ---
def main():
    # Inicializa sistema de navegação por páginas PRIMEIRO
    init_session_state()
    
    # Título principal
    st.title("🌱 FarmTech Solutions Dashboard")
    
    # Botões de navegação principal
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🗃️ Gerenciamento de Registros", use_container_width=True, type="primary"):
            st.session_state.current_page = "crud"
            st.rerun()
    
    with col2:
        # Método mais confiável usando markdown com link direto
        st.markdown("""
        <a href="http://localhost:8000/plotter" target="_self">
            <button style="
                width: 100%;
                height: 38px;
                background-color: #ff4b4b;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 400;
                padding: 0 12px;
            ">
                📈 Ver Gráficos Avançados (Live Plotter)
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🤖 Análise Estatística (R)", use_container_width=True, type="secondary"):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    st.markdown("---")
    
    # Navega para a página correta
    current_page = getattr(st.session_state, 'current_page', 'dashboard')
    if current_page == "crud":
        pagina_crud()
        return  # Sai da função para não mostrar o dashboard
    elif current_page == "analytics":
        pagina_analytics_r()
        return  # Sai da função para não mostrar o dashboard
    
    # === DASHBOARD PRINCIPAL ===
    
    # Sidebar para controles
    with st.sidebar:
        st.header("⚙️ Controles")
        auto_refresh = st.checkbox("🔄 Atualização Automática", value=True)
        refresh_interval = st.slider("Intervalo (segundos)", 3, 60, 45)
        
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.header("📊 Servidor")
        st.info(f"URL: {FLASK_SERVER_URL}")
        st.info(f"DB: {DatabaseConfig.HOST}")
        st.info(f"Schema: {DatabaseConfig.SCHEMA}")
    
    # Placeholder para status de conexão
    status_placeholder = st.empty()
    
    # Obtém dados dos sensores
    sensor_data = get_sensor_data()
    
    if sensor_data and sensor_data.get('dados'):
        # Status de conexão
        status_placeholder.success(f"✅ Conectado - {sensor_data.get('total_registros', 0)} registros")
        
        # Converte para DataFrame
        df = pd.DataFrame(sensor_data['dados'])
        
        # Processa timestamps com diferentes formatos
        if 'data_hora_leitura' in df.columns:
            try:
                # Abordagem mais robusta - força coerção de erros
                df['data_hora_leitura'] = pd.to_datetime(df['data_hora_leitura'], errors='coerce')
                df = df.sort_values('data_hora_leitura', ascending=False)
            except Exception as e:
                st.error(f"Erro ao processar timestamps: {e}")
                # Se falhar, usa dados sem ordenação por data
                pass
        
        # Dados mais recentes
        if not df.empty:
            ultimo_registro = df.iloc[0]
            
            # === SEÇÃO 1: MÉTRICAS PRINCIPAIS ===
            st.header("📊 Dados Atuais")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                temp_value = ultimo_registro.get('temperatura', 0)
                try:
                    temp_float = float(temp_value)
                    temp_display = f"{temp_float:.1f}°C"
                except:
                    temp_display = f"{temp_value}°C"
                
                st.metric(
                    label="🌡️ Temperatura",
                    value=temp_display,
                    delta=None
                )
                
            with col2:
                umid_value = ultimo_registro.get('umidade', 0)
                try:
                    umid_float = float(umid_value)
                    umid_display = f"{umid_float:.1f}%"
                except:
                    umid_display = f"{umid_value}%"
                
                st.metric(
                    label="💧 Umidade",
                    value=umid_display,
                    delta=None
                )
                
            with col3:
                ph_value = ultimo_registro.get('ph', 7)
                try:
                    ph_float = float(ph_value)
                    ph_display = f"{ph_float:.1f}"
                except:
                    ph_display = str(ph_value)
                
                st.metric(
                    label="⚗️ pH",
                    value=ph_display,
                    delta=None
                )
                
            with col4:
                bomba_status = ultimo_registro.get('bomba_dagua', False)
                if isinstance(bomba_status, str):
                    bomba_ligada = bomba_status.lower() in ['true', 'on', '1']
                else:
                    bomba_ligada = bool(bomba_status)
                    
                st.metric(
                    label="🚰 Bomba",
                    value="Ligada" if bomba_ligada else "Desligada",
                    delta=None
                )
            
            # === SEÇÃO 2: STATUS DOS NUTRIENTES ===
            st.header("🧪 Nutrientes")
            col1, col2 = st.columns(2)
            
            with col1:
                fosforo_value = ultimo_registro.get('fosforo', False)
                if isinstance(fosforo_value, str):
                    fosforo_presente = fosforo_value.lower() in ['true', 'presente', '1']
                else:
                    fosforo_presente = bool(fosforo_value)
                
                if fosforo_presente:
                    st.success("🧪 Fósforo: Presente ✅")
                else:
                    st.error("🧪 Fósforo: Ausente ❌")
            
            with col2:
                potassio_value = ultimo_registro.get('potassio', False)
                if isinstance(potassio_value, str):
                    potassio_presente = potassio_value.lower() in ['true', 'presente', '1']
                else:
                    potassio_presente = bool(potassio_value)
                
                if potassio_presente:
                    st.success("🧪 Potássio: Presente ✅")
                else:
                    st.error("🧪 Potássio: Ausente ❌")
            
            # === SEÇÃO 3: GRÁFICOS ===
            st.header("📈 Tendências")
            
            if len(df) > 1:
                # Prepara dados para gráficos (últimos 20 registros)
                df_plot = df.head(20).copy()
                
                # Converte colunas numéricas para garantir que sejam números
                for col in ['umidade', 'temperatura', 'ph']:
                    if col in df_plot.columns:
                        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')
                
                # Remove linhas com valores NaN
                df_plot = df_plot.dropna(subset=['data_hora_leitura'])
                df_plot = df_plot.sort_values('data_hora_leitura')
                
                if not df_plot.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de Umidade
                        if 'umidade' in df_plot.columns:
                            fig_umidade = px.line(
                                df_plot, 
                                x='data_hora_leitura', 
                                y='umidade',
                                title='💧 Umidade do Solo',
                                labels={'umidade': 'Umidade (%)', 'data_hora_leitura': 'Horário'}
                            )
                            fig_umidade.update_traces(line_color='#1f77b4')
                            st.plotly_chart(fig_umidade, use_container_width=True)
                    
                    with col2:
                        # Gráfico de Temperatura
                        if 'temperatura' in df_plot.columns:
                            fig_temperatura = px.line(
                                df_plot, 
                                x='data_hora_leitura', 
                                y='temperatura',
                                title='🌡️ Temperatura do Solo',
                                labels={'temperatura': 'Temperatura (°C)', 'data_hora_leitura': 'Horário'}
                            )
                            fig_temperatura.update_traces(line_color='#ff7f0e')
                            st.plotly_chart(fig_temperatura, use_container_width=True)
                    
                    # Gráfico de pH
                    if 'ph' in df_plot.columns:
                        fig_ph = px.line(
                            df_plot, 
                            x='data_hora_leitura', 
                            y='ph',
                            title='⚗️ Nível de pH',
                            labels={'ph': 'pH', 'data_hora_leitura': 'Horário'}
                        )
                        fig_ph.update_traces(line_color='#2ca02c')
                        fig_ph.add_hline(y=7, line_dash="dash", line_color="red", 
                                       annotation_text="pH Neutro (7)")
                        st.plotly_chart(fig_ph, use_container_width=True)
                else:
                    st.warning("⚠️ Dados insuficientes para gráficos")
            
            # === SEÇÃO 4: DADOS CLIMÁTICOS ===
            st.header("🌤️ Condições Climáticas")
            
            clima = get_clima_atual()
            
            if clima and clima.get('cidade') != 'Erro':
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info(f"📍 **Cidade:** {clima['cidade']}")
                    st.info(f"🌡️ **Temperatura:** {clima['temperatura']}°C")
                
                with col2:
                    st.info(f"💧 **Umidade:** {clima['umidade']}%")
                    st.info(f"☁️ **Condição:** {clima['condicao']}")
                
                with col3:
                    st.info(f"🌬️ **Vento:** {clima['vento']} m/s")
                    st.info(f"🌧️ **Chuva:** {clima['chuva']} mm")
                
                # Alerta de chuva
                if clima['vai_chover']:
                    st.warning(f"🌧️ **ALERTA:** Previsão de {clima['chuva']} mm de chuva! Manter bomba d'água desligada!")
                else:
                    st.success("☀️ Sem previsão de chuva nas próximas horas.")
            else:
                st.error("❌ Erro ao obter dados climáticos")
    
            # === SEÇÃO 5: TABELA DE DADOS ===
            st.header("📋 Histórico de Leituras")
            
            # Prepara dados para exibição
            df_display = df.copy()
            if 'data_hora_leitura' in df_display.columns:
                try:
                    df_display['data_hora_leitura'] = df_display['data_hora_leitura'].dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    # Se falhar, mantém formato original
                    pass
            
            # Renomeia colunas para melhor exibição
            column_mapping = {
                'id': 'ID',
                'data_hora_leitura': 'Data/Hora',
                'temperatura': 'Temp (°C)',
                'umidade': 'Umidade (%)',
                'ph': 'pH',
                'fosforo': 'Fósforo',
                'potassio': 'Potássio',
                'bomba_dagua': 'Bomba'
            }
            
            df_display = df_display.rename(columns=column_mapping)
            
            # Seleciona colunas para exibir
            cols_to_show = [col for col in column_mapping.values() if col in df_display.columns]
            df_display = df_display[cols_to_show]
            
            st.dataframe(
                df_display.head(10),
                use_container_width=True,
                height=400
            )
        else:
            if sensor_data and sensor_data.get('dados'):
                st.warning("⚠️ Nenhum dado encontrado")
    
    # Mensagem de erro de conexão
    if not sensor_data or not sensor_data.get('dados'):
        status_placeholder.error("❌ Erro ao conectar com o servidor ou sem dados")
        st.error("Verifique se o servidor Flask está rodando em http://127.0.0.1:8000")
    
    # Auto-refresh otimizado
    if auto_refresh:
        # Mostra próxima atualização
        with st.empty():
            for i in range(refresh_interval, 0, -1):
                st.caption(f"🔄 Próxima atualização em {i} segundos...")
                time.sleep(1)
        
        # Limpa cache e recarrega
        st.cache_data.clear()
        st.rerun()

# --- Execução principal ---
if __name__ == "__main__":
    main() 