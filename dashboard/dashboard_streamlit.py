import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import time
import sys
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib

# Importa as configurações do banco
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.database_config import _config as DatabaseConfig, conectar_postgres

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions Dashboard",
    page_icon="",
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

if 'rscript_path' not in st.session_state:
    st.session_state.rscript_path = 'Rscript'  # Comando padrão para R

# URL do servidor Flask local
FLASK_SERVER_URL = "http://127.0.0.1:8000/get_data"

# === FUNÇÕES CRUD PARA STREAMLIT ===

def crud_inserir_dados():
    """Interface Streamlit para inserir novos dados"""
    st.subheader("Inserir Nova Leitura")
    
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
        
        submitted = st.form_submit_button("Inserir Dados")
        
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
                    st.success("Dados inseridos com sucesso!")
                    st.balloons()
                    cursor.close()
                    conn.close()
                    st.cache_data.clear()  # Limpa cache para mostrar novos dados
                else:
                    st.error("Erro ao conectar com o banco de dados")
            except Exception as e:
                st.error(f"Erro ao inserir dados: {e}")

def crud_listar_dados():
    """Interface Streamlit para listar dados"""
    st.subheader("Gerenciar Leituras")
    
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
                df['Fósforo'] = df['Fósforo'].apply(lambda x: "Presente" if x else "Ausente")
                df['Potássio'] = df['Potássio'].apply(lambda x: "Presente" if x else "Ausente")
                df['Bomba'] = df['Bomba'].apply(lambda x: "Ligada" if x else "Desligada")
                
                st.dataframe(df, use_container_width=True, height=400)
                st.info(f"Mostrando últimos 50 registros de {len(rows)} encontrados")
            else:
                st.warning("Nenhum dado encontrado")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"Erro ao listar dados: {e}")

def crud_atualizar_dados():
    """Interface Streamlit para atualizar dados"""
    st.subheader("Atualizar Leitura")
    
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
                            st.info(f"Atualizando registro ID: {id_registro}")
                            
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
                            
                            submitted = st.form_submit_button("Atualizar Registro")
                            
                            if submitted:
                                try:
                                    cursor.execute(f"""
                                        UPDATE {DatabaseConfig.SCHEMA}.leituras_sensores
                                        SET umidade = %s, temperatura = %s, ph = %s, fosforo = %s, potassio = %s, bomba_dagua = %s
                                        WHERE id = %s
                                    """, (nova_umidade, nova_temperatura, novo_ph, novo_fosforo, novo_potassio, nova_bomba, id_registro))
                                    
                                    if cursor.rowcount > 0:
                                        conn.commit()
                                        st.success("Registro atualizado com sucesso!")
                                        st.cache_data.clear()
                                    else:
                                        st.warning("Nenhum registro foi atualizado")
                                except Exception as e:
                                    st.error(f"Erro ao atualizar: {e}")
            else:
                st.warning("Nenhum registro encontrado")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"Erro ao buscar registros: {e}")

def crud_remover_dados():
    """Interface Streamlit para remover dados"""
    st.subheader("Remover Leitura")
    
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
                        st.warning("Registro a ser removido:")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info(f"**ID:** {registro[0]}")
                            st.info(f"**Data/Hora:** {registro[1]}")
                            st.info(f"**Umidade:** {registro[2]}%")
                            st.info(f"**Temperatura:** {registro[3]}°C")
                        
                        with col2:
                            st.info(f"**pH:** {registro[4]}")
                            st.info(f"**Fósforo:** {'Presente' if registro[5] else 'Ausente'}")
                            st.info(f"**Potássio:** {'Presente' if registro[6] else 'Ausente'}")
                            st.info(f"**Bomba:** {'Ligada' if registro[7] else 'Desligada'}")
                        
                        # Confirmação
                        confirmar = st.checkbox("Confirmo que desejo remover este registro")
                        
                        if confirmar and st.button("REMOVER REGISTRO", type="primary"):
                            try:
                                cursor.execute(f"DELETE FROM {DatabaseConfig.SCHEMA}.leituras_sensores WHERE id = %s", (id_registro,))
                                if cursor.rowcount > 0:
                                    conn.commit()
                                    st.success("Registro removido com sucesso!")
                                    st.cache_data.clear()
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.warning("Nenhum registro foi removido")
                            except Exception as e:
                                st.error(f"Erro ao remover: {e}")
            else:
                st.warning("Nenhum registro encontrado")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"Erro ao buscar registros: {e}")

def crud_estatisticas():
    """Interface Streamlit para mostrar estatísticas"""
    st.subheader("Estatísticas dos Dados")
    
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
                    st.metric("Total de Registros", f"{stats[0]:,}")
                
                with col2:
                    st.metric("Umidade Média", f"{stats[1]:.1f}%")
                
                with col3:
                    st.metric("Temperatura Média", f"{stats[4]:.1f}°C")
                
                with col4:
                    st.metric("pH Médio", f"{stats[7]:.1f}")
                
                # Estatísticas detalhadas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info("**UMIDADE**")
                    st.write(f"Média: {stats[1]:.1f}%")
                    st.write(f"Mínima: {stats[2]:.1f}%")
                    st.write(f"Máxima: {stats[3]:.1f}%")
                
                with col2:
                    st.info("**TEMPERATURA**")
                    st.write(f"Média: {stats[4]:.1f}°C")
                    st.write(f"Mínima: {stats[5]:.1f}°C")
                    st.write(f"Máxima: {stats[6]:.1f}°C")
                
                with col3:
                    st.info("**pH**")
                    st.write(f"Médio: {stats[7]:.1f}")
                    st.write(f"Mínimo: {stats[8]:.1f}")
                    st.write(f"Máximo: {stats[9]:.1f}")
                
            else:
                st.warning("Nenhum dado disponível para estatísticas")
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"Erro ao calcular estatísticas: {e}")

def crud_consulta_umidade():
    """Interface Streamlit para consulta por umidade"""
    st.subheader("Consulta por Umidade")
    
    col1, col2 = st.columns(2)
    with col1:
        limite = st.number_input("Valor de referência (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
    with col2:
        condicao = st.selectbox("Condição", ["acima", "abaixo"])
    
    if st.button("Buscar"):
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
                    st.success(f"Encontrados {len(rows)} registros com umidade {condicao} de {limite}%")
                    
                    # Converte para DataFrame
                    df = pd.DataFrame(rows, columns=[
                        'ID', 'Data/Hora', 'Umidade', 'Temperatura', 'pH', 'Fósforo', 'Potássio', 'Bomba'
                    ])
                    
                    # Formata as colunas boolean
                    df['Fósforo'] = df['Fósforo'].apply(lambda x: "Presente" if x else "Ausente")
                    df['Potássio'] = df['Potássio'].apply(lambda x: "Presente" if x else "Ausente")
                    df['Bomba'] = df['Bomba'].apply(lambda x: "Ligada" if x else "Desligada")
                    
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Nenhum registro encontrado com esse critério")
                
                cursor.close()
                conn.close()
        except Exception as e:
            st.error(f"Erro na consulta: {e}")

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
                
                st.success(f"Dados exportados com sucesso! {len(rows)} registros salvos em:")
                st.code(output_path)
                return True
            else:
                st.warning("Nenhum dado encontrado para exportar")
                return False
            
            cursor.close()
            conn.close()
    except Exception as e:
        st.error(f"Erro ao exportar dados: {e}")
        return False

def executar_script_r():
    """Executa o script R de análise estatística, pedindo o caminho se não for encontrado."""
    try:
        # Caminho para o script R
        script_path = os.path.join(parent_dir, 'analise_estatistica', 'AnaliseEstatisticaBD.R')
        analise_dir = os.path.join(parent_dir, 'analise_estatistica')
        
        if not os.path.exists(script_path):
            st.error(f"Script R não encontrado: {script_path}")
            return False
            
        # Usa o caminho do R salvo na sessão
        r_executable = st.session_state.get('rscript_path', 'Rscript')
        
        import subprocess
        with st.spinner(f"Executando análise com '{r_executable}'..."):
            result = subprocess.run([r_executable, script_path], 
                                  cwd=analise_dir,
                                  capture_output=True, 
                                  text=True,
                                  timeout=60)
        
        if result.returncode == 0:
            st.success("Análise R executada com sucesso!")
            if result.stdout:
                st.text("Output do R:")
                st.code(result.stdout)
            
            # Adiciona botão para download do PDF
            pdf_path = os.path.join(analise_dir, 'Rplots.pdf')
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                st.download_button(
                    label="Baixar Relatório PDF",
                    data=pdf_bytes,
                    file_name="relatorio_analise_R.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("PDF não disponível (execute o script R primeiro)")
        
            # Adiciona botão para download do CSV
            resumo_path = os.path.join(analise_dir, 'resumo_estatistico.csv')
            if os.path.exists(resumo_path):
                df_resumo = pd.read_csv(resumo_path)
                csv_data = df_resumo.to_csv(index=False)
                st.download_button(
                    label="Baixar Resumo CSV",
                    data=csv_data,
                    file_name="resumo_estatistico.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("O arquivo resumo_estatistico.csv não foi encontrado.")

            return True
        else:
            st.error("Erro na execução do script R:")
            st.code(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        st.error("Timeout: Script R demorou mais de 60 segundos")
        return False
    except FileNotFoundError:
        st.error("R não encontrado no sistema.")
        
        st.warning("Forneça o caminho para a pasta 'bin' da sua instalação do R.")
        
        r_bin_path = st.text_input(
            "Caminho para a pasta 'bin' do R", 
            value=st.session_state.get('r_bin_path_input', r"C:\Program Files\R\R-4.4.3\bin"),
            key="r_bin_path_input",
            help="Exemplo: C:\\Program Files\\R\\R-4.4.3\\bin"
        )

        if st.button("Salvar caminho e tentar novamente"):
            # Constrói o caminho completo para Rscript.exe
            potential_rscript_path = os.path.join(r_bin_path, 'Rscript.exe')
            
            # Validação do caminho
            if os.path.isdir(r_bin_path) and os.path.exists(potential_rscript_path):
                st.session_state.rscript_path = potential_rscript_path
                st.success(f"Caminho do Rscript salvo: {potential_rscript_path}")
                
                # Executa o script R imediatamente após configurar o caminho
                st.info("Executando análise R com o novo caminho...")
                time.sleep(1)
                
                # Chama a função novamente para executar o script
                return executar_script_r()
            else:
                st.error("Caminho inválido. Verifique se a pasta 'bin' existe e contém 'Rscript.exe'.")
        return False
    except Exception as e:
        st.error(f"Erro ao executar script R: {e}")
        return False

def mostrar_resumo_estatistico():
    """Mostra o resumo estatístico gerado pelo R"""
    try:
        resumo_path = os.path.join(parent_dir, 'analise_estatistica', 'resumo_estatistico.csv')
        
        if os.path.exists(resumo_path):
            df_resumo = pd.read_csv(resumo_path)
            st.subheader("Resumo Estatístico (Gerado pelo R)")
            st.dataframe(df_resumo, use_container_width=True)
            
            # Botão para download
            csv_data = df_resumo.to_csv(index=False)
            st.download_button(
                label="Download Resumo Estatístico",
                data=csv_data,
                file_name="resumo_estatistico.csv",
                mime="text/csv"
            )
            return True
        else:
            st.warning("Arquivo de resumo estatístico não encontrado. Execute a análise primeiro.")
            return False
            
    except Exception as e:
        st.error(f"Erro ao ler resumo estatístico: {e}")
        return False

def verificar_ambiente_r():
    """Verifica se o ambiente R está configurado corretamente"""
    try:
        import subprocess
        result = subprocess.run(['R', '--version'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            st.success("R está instalado e funcionando")
            st.text("Versão do R:")
            st.code(result.stdout.split('\n')[0])
            return True
        else:
            st.error("Problema com a instalação do R")
            return False
            
    except FileNotFoundError:
        st.error("R não encontrado. Instale o R para usar as análises estatísticas.")
        st.markdown("""
        **Como instalar o R:**
        - **macOS**: `brew install r` ou baixe de https://cran.r-project.org/
        - **Ubuntu**: `sudo apt-get install r-base`
        - **Windows**: Baixe de https://cran.r-project.org/
        """)
        return False
    except Exception as e:
        st.error(f"Erro ao verificar R: {e}")
        return False

def pagina_analytics_r():
    """Página dedicada à análise estatística com R"""
    st.title("Análise Estatística com R")
    st.markdown("**Análise preditiva e estatística usando linguagem R**")
    
    # Botão para voltar ao dashboard
    if st.button("Voltar ao Dashboard", type="primary"):
        st.session_state.current_page = "dashboard"
        st.session_state.analytics_opcao = "Selecione uma análise..."
        st.rerun()
    
    st.markdown("---")
    
    # Informações do sistema
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Schema:** {DatabaseConfig.SCHEMA}")
    with col2:
        st.info(f"**Linguagem:** R + Python")
    with col3:
        st.info(f"**Pasta:** analise_estatistica/")
    
    st.markdown("---")
    
    # Verificação do ambiente R
    st.subheader("Verificação do Ambiente")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Verificar Instalação do R", use_container_width=True):
            verificar_ambiente_r()
    
    with col2:
        if st.button("Exportar Dados para R", use_container_width=True):
            exportar_dados_para_r()
    
    st.markdown("---")
    
    # Seleção de análises
    analytics_opcao = st.selectbox(
        "**Selecione a análise desejada:**",
        [
            "Selecione uma análise...",
            "Executar Análise Estatística Completa",
            "Ver Resumo Estatístico",
            "Status dos Arquivos R",
            "Configurar Ambiente R"
        ],
        key="analytics_page_selectbox"
    )
    
    st.markdown("---")
    
    # Executa a operação selecionada
    if analytics_opcao == "Executar Análise Estatística Completa":
        st.subheader("Análise Estatística Completa")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("1. Exportar Dados", use_container_width=True):
                exportar_dados_para_r()
        
        with col2:
            if st.button("2. Executar Script R", use_container_width=True):
                if executar_script_r():
                    st.balloons()
        
        st.markdown("---")
        st.info("**Processo completo:** 1) Exporte os dados → 2) Execute o script R → 3) Veja os resultados")
        
        # Seção de downloads após execução
        st.markdown("---")
        st.subheader("Downloads Disponíveis")
        
        analise_dir = os.path.join(parent_dir, 'analise_estatistica')
        
        # Verifica e mostra botões de download
        col1, col2 = st.columns(2)
        
        with col1:
            # Download do PDF
            pdf_path = os.path.join(analise_dir, 'Rplots.pdf')
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                st.download_button(
                    label="Baixar Relatório PDF",
                    data=pdf_bytes,
                    file_name="relatorio_analise_R.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("PDF não disponível (execute o script R primeiro)")
        
        with col2:
            # Download do CSV
            resumo_path = os.path.join(analise_dir, 'resumo_estatistico.csv')
            if os.path.exists(resumo_path):
                df_resumo = pd.read_csv(resumo_path)
                csv_data = df_resumo.to_csv(index=False)
                st.download_button(
                    label="Baixar Resumo CSV",
                    data=csv_data,
                    file_name="resumo_estatistico.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("CSV não disponível (execute o script R primeiro)")
        
        # Mostra preview do resumo se disponível
        if os.path.exists(resumo_path):
            st.markdown("---")
            st.subheader("Preview do Resumo Estatístico")
            st.dataframe(df_resumo, use_container_width=True)
    elif analytics_opcao == "Ver Resumo Estatístico":
        mostrar_resumo_estatistico()
        
    elif analytics_opcao == "Status dos Arquivos R":
        st.subheader("Status dos Arquivos R")
        
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
                st.success(f"**{arquivo}** - {descricao}")
            else:
                st.error(f"**{arquivo}** - {descricao} (não encontrado)")
        
    elif analytics_opcao == "Configurar Ambiente R":
        st.subheader("Configuração do Ambiente R")
        
        st.markdown("""
        **Pacotes R necessários:**
        ```r
        install.packages(c("readr", "dplyr", "ggplot2", "lubridate", "forecast"))
        ```
        
        **Para instalar os pacotes automaticamente:**
        """)
        
        if st.button("Instalar Pacotes R", use_container_width=True):
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
                      cat("", package, "instalado com sucesso\\n")
                    } else {
                      cat("Erro ao instalar", package, "\\n")
                    }
                  } else {
                    cat("", package, "já está instalado\\n")
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
                
                # Usa o caminho do R salvo na sessão para instalar pacotes
                r_executable = st.session_state.get('rscript_path', 'Rscript')
                install_cmd = [r_executable, '-e', install_script]
                
                with st.spinner(f"Instalando pacotes com '{r_executable}'... (pode demorar)"):
                    result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    st.success("Pacotes R instalados com sucesso!")
                    st.text("Log da instalação:")
                    st.code(result.stdout)
                else:
                    st.error("Erro na instalação dos pacotes:")
                    st.code(result.stderr)
                    st.info("Tente executar manualmente no R: install.packages(c('readr', 'dplyr', 'ggplot2', 'lubridate', 'forecast'))")
            except FileNotFoundError:
                 st.error(f"R ('{st.session_state.get('rscript_path', 'Rscript')}') não encontrado. Vá para 'Executar Análise Estatística Completa' e clique em 'Executar Script R' para configurar o caminho.")
            except subprocess.TimeoutExpired:
                st.error("Timeout: Instalação demorou mais de 5 minutos")
            except Exception as e:
                st.error(f"Erro: {e}")
        
    else:
        st.info("Selecione uma análise no menu acima para começar")
        
        # Preview da estrutura do projeto R
        st.subheader("Estrutura do Projeto R")
        st.markdown("""
        ```
        analise_estatistica/
        ├── AnaliseEstatisticaBD.R       # Script principal
        ├── leituras_sensores.csv        # Dados para análise  
        ├── resumo_estatistico.csv       # Resultados gerados
        ├── requirements.txt             # Dependências R
        └── README.md                    # Documentação
        ```
        
        **Funcionalidades disponíveis:**
        - Estatísticas descritivas
        - Correlações entre variáveis
        - Visualizações com ggplot2
        - Previsões ARIMA para umidade
        - Análise de séries temporais
        """)

def pagina_crud():
    """Página dedicada ao CRUD"""
    st.title("Gerenciamento de Registros")
    st.markdown("**Operações do Banco de Dados PostgreSQL**")
    
    # Botão para voltar ao dashboard
    if st.button("Voltar ao Dashboard", type="primary"):
        st.session_state.current_page = "dashboard"
        st.session_state.crud_opcao = "Selecione uma operação..."
        st.rerun()
    
    st.markdown("---")
    
    # Informações do banco
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Schema:** {DatabaseConfig.SCHEMA}")
    with col2:
        st.info(f"**Host:** {DatabaseConfig.HOST}")
    with col3:
        st.info(f"**Database:** {DatabaseConfig.DATABASE}")
    
    st.markdown("---")
    
    # Seleção de operação CRUD
    crud_opcao = st.selectbox(
        "**Selecione a operação desejada:**",
        [
            "Selecione uma operação...",
            "Inserir Nova Leitura",
            "Gerenciar Leituras",
            "Atualizar Leitura",
            "Remover Leitura",
            "Estatísticas dos Dados",
            "Consulta por Umidade"
        ],
        key="crud_page_selectbox"
    )
    
    st.markdown("---")
    
    # Executa a operação selecionada
    if crud_opcao == "Inserir Nova Leitura":
        crud_inserir_dados()
    elif crud_opcao == "Gerenciar Leituras":
        crud_listar_dados()
    elif crud_opcao == "Atualizar Leitura":
        crud_atualizar_dados()
    elif crud_opcao == "Remover Leitura":
        crud_remover_dados()
    elif crud_opcao == "Estatísticas dos Dados":
        crud_estatisticas()
    elif crud_opcao == "Consulta por Umidade":
        crud_consulta_umidade()
    else:
        st.info("Selecione uma operação no menu acima para começar")
        
        # Mostra preview das últimas leituras
        st.subheader("Últimas Leituras (Preview)")
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
                    df['Fósforo'] = df['Fósforo'].apply(lambda x: "Presente" if x else "Ausente")
                    df['Potássio'] = df['Potássio'].apply(lambda x: "Presente" if x else "Ausente")
                    df['Bomba'] = df['Bomba'].apply(lambda x: "Ligada" if x else "Desligada")
                    
                    st.dataframe(df, use_container_width=True)
                    st.caption("Mostrando apenas os 5 registros mais recentes")
                else:
                    st.warning("Nenhum registro encontrado")
                
                cursor.close()
                conn.close()
        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")

# === FUNÇÕES PARA MACHINE LEARNING COM SCIKIT-LEARN ===

def preparar_dados_ml():
    """Prepara dados do banco para Machine Learning com dados meteorológicos"""
    try:
        conn, cursor = conectar_postgres()
        if conn:
            # Primeiro tenta usar dados integrados (com meteorologia)
            cursor.execute(f"""
                SELECT COUNT(*) FROM {DatabaseConfig.SCHEMA}.leituras_integradas
            """)
            count_integradas = cursor.fetchone()[0]
            
            if count_integradas > 10:
                # Usa dados integrados completos
                cursor.execute(f"""
                    SELECT umidade_solo, temperatura_solo, ph_solo, fosforo, potassio, bomba_dagua,
                           temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento,
                           probabilidade_chuva, quantidade_chuva, diferenca_temperatura,
                           deficit_umidade, fator_evapotranspiracao, hora_do_dia, dia_semana,
                           mes, vai_chover_hoje, vento_forte, dia_quente
                    FROM {DatabaseConfig.SCHEMA}.view_ml_completa
                    WHERE umidade_solo IS NOT NULL AND temperatura_solo IS NOT NULL
                    ORDER BY data_hora_leitura DESC
                    LIMIT 1000
                """)
                rows = cursor.fetchall()
                
                if rows:
                    df = pd.DataFrame(rows, columns=[
                        'umidade_solo', 'temperatura_solo', 'ph_solo', 'fosforo', 'potassio', 
                        'bomba_dagua', 'temperatura_externa', 'umidade_ar', 'pressao_atmosferica',
                        'velocidade_vento', 'probabilidade_chuva', 'quantidade_chuva',
                        'diferenca_temperatura', 'deficit_umidade', 'fator_evapotranspiracao',
                        'hora_do_dia', 'dia_semana', 'mes', 'vai_chover_hoje', 'vento_forte', 'dia_quente'
                    ])
                    
                    # Renomeia colunas para compatibilidade
                    df = df.rename(columns={
                        'umidade_solo': 'umidade',
                        'temperatura_solo': 'temperatura', 
                        'ph_solo': 'ph'
                    })
                    
                    cursor.close()
                    conn.close()
                    st.success(f"Usando dados INTEGRADOS com meteorologia: {len(df)} registros")
                    return df
            
            # Fallback: usa dados básicos dos sensores
            cursor.execute(f"""
                SELECT umidade, temperatura, ph, fosforo, potassio, bomba_dagua,
                       EXTRACT(HOUR FROM data_hora_leitura) as hora_do_dia,
                       EXTRACT(DOW FROM data_hora_leitura) as dia_semana,
                       EXTRACT(MONTH FROM data_hora_leitura) as mes
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                WHERE umidade IS NOT NULL AND temperatura IS NOT NULL AND ph IS NOT NULL
                ORDER BY data_hora_leitura DESC
                LIMIT 1000
            """)
            rows = cursor.fetchall()
            
            if len(rows) > 10:  # Mínimo de dados para ML
                df = pd.DataFrame(rows, columns=[
                    'umidade', 'temperatura', 'ph', 'fosforo', 'potassio', 
                    'bomba_dagua', 'hora_do_dia', 'dia_semana', 'mes'
                ])
                
                # Converte booleanos para numérico
                df['fosforo'] = df['fosforo'].astype(int)
                df['potassio'] = df['potassio'].astype(int)
                df['bomba_dagua'] = df['bomba_dagua'].astype(int)
                
                cursor.close()
                conn.close()
                st.info(f"Usando dados BÁSICOS (sem meteorologia): {len(df)} registros")
                return df
            else:
                st.warning("Dados insuficientes para Machine Learning (mínimo 10 registros)")
                cursor.close()
                conn.close()
                return None
    except Exception as e:
        st.error(f"Erro ao preparar dados para ML: {e}")
        return None

def treinar_modelo_irrigacao(df):
    """Treina modelo para prever necessidade de irrigação com dados meteorológicos"""
    try:
        # Features básicas
        features_basicas = ['temperatura', 'ph', 'fosforo', 'potassio', 'hora_do_dia', 'dia_semana', 'mes']
        
        # Features meteorológicas (se disponíveis)
        features_meteorologicas = [
            'temperatura_externa', 'umidade_ar', 'pressao_atmosferica', 'velocidade_vento',
            'probabilidade_chuva', 'quantidade_chuva', 'diferenca_temperatura', 
            'deficit_umidade', 'fator_evapotranspiracao', 'vai_chover_hoje', 'vento_forte', 'dia_quente'
        ]
        
        # Verifica quais features estão disponíveis
        features_disponiveis = []
        for feat in features_basicas:
            if feat in df.columns:
                features_disponiveis.append(feat)
        
        for feat in features_meteorologicas:
            if feat in df.columns:
                features_disponiveis.append(feat)
        
        X = df[features_disponiveis]
        
        # Log das features utilizadas
        if any(feat in df.columns for feat in features_meteorologicas):
            st.info(f"Usando {len(features_disponiveis)} features (incluindo meteorologia)")
        else:
            st.info(f"Usando {len(features_disponiveis)} features básicas")
        
        # Target (variável dependente) - bomba de irrigação
        y = df['bomba_dagua']
        
        # Divide dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Treina modelo Random Forest
        modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        modelo.fit(X_train, y_train)
        
        # Avalia modelo
        y_pred = modelo.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Importância das features
        feature_importance = pd.DataFrame({
            'feature': features_disponiveis,
            'importance': modelo.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return modelo, accuracy, feature_importance, X_test, y_test, y_pred
        
    except Exception as e:
        st.error(f"Erro ao treinar modelo: {e}")
        return None, None, None, None, None, None

def treinar_modelo_umidade(df):
    """Treina modelo para prever umidade futura com dados meteorológicos"""
    try:
        # Features básicas para prever umidade
        features_basicas = ['temperatura', 'ph', 'fosforo', 'potassio', 'bomba_dagua', 'hora_do_dia', 'mes']
        
        # Features meteorológicas que afetam umidade do solo
        features_meteorologicas = [
            'temperatura_externa', 'umidade_ar', 'pressao_atmosferica', 'velocidade_vento',
            'probabilidade_chuva', 'quantidade_chuva', 'diferenca_temperatura', 
            'fator_evapotranspiracao', 'vai_chover_hoje', 'vento_forte', 'dia_quente'
        ]
        
        # Verifica quais features estão disponíveis
        features_disponiveis = []
        for feat in features_basicas:
            if feat in df.columns:
                features_disponiveis.append(feat)
        
        for feat in features_meteorologicas:
            if feat in df.columns:
                features_disponiveis.append(feat)
        
        X = df[features_disponiveis]
        y = df['umidade']
        
        # Divide dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Normaliza dados
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Treina modelo
        modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo.fit(X_train_scaled, y_train)
        
        # Avalia modelo
        y_pred = modelo.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Importância das features
        feature_importance = pd.DataFrame({
            'feature': features_disponiveis,
            'importance': modelo.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return modelo, scaler, rmse, feature_importance, X_test, y_test, y_pred
        
    except Exception as e:
        st.error(f"Erro ao treinar modelo de umidade: {e}")
        return None, None, None, None, None, None, None

def prever_irrigacao_inteligente(modelo_irrigacao, modelo_umidade, scaler, hora_atual=None):
    """Faz previsões inteligentes de irrigação"""
    try:
        if hora_atual is None:
            hora_atual = datetime.now().hour
        
        # Cenários de teste
        cenarios = [
            {"temperatura": 25, "ph": 6.5, "fosforo": 1, "potassio": 1, "hora_do_dia": hora_atual, "dia_semana": 1},
            {"temperatura": 30, "ph": 6.0, "fosforo": 0, "potassio": 1, "hora_do_dia": hora_atual, "dia_semana": 1},
            {"temperatura": 35, "ph": 7.0, "fosforo": 1, "potassio": 0, "hora_do_dia": hora_atual, "dia_semana": 1},
        ]
        
        resultados = []
        
        for i, cenario in enumerate(cenarios):
            # Previsão de irrigação
            X_irrig = np.array([[cenario["temperatura"], cenario["ph"], cenario["fosforo"], 
                               cenario["potassio"], cenario["hora_do_dia"], cenario["dia_semana"]]])
            prob_irrigacao = modelo_irrigacao.predict_proba(X_irrig)[0][1]  # Probabilidade de irrigar
            
            # Previsão de umidade (com e sem irrigação)
            X_umid_sem = np.array([[cenario["temperatura"], cenario["ph"], cenario["fosforo"], 
                                  cenario["potassio"], 0, cenario["hora_do_dia"]]])
            X_umid_com = np.array([[cenario["temperatura"], cenario["ph"], cenario["fosforo"], 
                                  cenario["potassio"], 1, cenario["hora_do_dia"]]])
            
            X_umid_sem_scaled = scaler.transform(X_umid_sem)
            X_umid_com_scaled = scaler.transform(X_umid_com)
            
            umidade_sem_irrigacao = modelo_umidade.predict(X_umid_sem_scaled)[0]
            umidade_com_irrigacao = modelo_umidade.predict(X_umid_com_scaled)[0]
            
            # Recomendação inteligente
            if prob_irrigacao > 0.5 or umidade_sem_irrigacao < 30:
                recomendacao = "IRRIGAR"
                motivo = f"Prob: {prob_irrigacao:.2f} | Umidade esperada sem irrigação: {umidade_sem_irrigacao:.1f}%"
            else:
                recomendacao = "NÃO IRRIGAR"
                motivo = f"Prob: {prob_irrigacao:.2f} | Umidade atual suficiente: {umidade_sem_irrigacao:.1f}%"
            
            resultados.append({
                "cenario": f"Cenário {i+1}",
                "temperatura": cenario["temperatura"],
                "ph": cenario["ph"],
                "nutrientes": f"P:{cenario['fosforo']} K:{cenario['potassio']}",
                "prob_irrigacao": prob_irrigacao,
                "umidade_sem_irrig": umidade_sem_irrigacao,
                "umidade_com_irrig": umidade_com_irrigacao,
                "recomendacao": recomendacao,
                "motivo": motivo
            })
        
        return resultados
        
    except Exception as e:
        st.error(f"Erro nas previsões: {e}")
        return []

def pagina_ml_scikit():
    """Página dedicada ao Machine Learning com Scikit-learn"""
    st.title("Machine Learning com Scikit-learn")
    st.markdown("**Modelo preditivo inteligente para irrigação automatizada**")
    
    # Botão para voltar ao dashboard
    if st.button("Voltar ao Dashboard", type="primary"):
        st.session_state.current_page = "dashboard"
        st.rerun()
    
    st.markdown("---")
    
    # Informações do sistema
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Algoritmo:** Random Forest")
    with col2:
        st.info(f"**Biblioteca:** Scikit-learn")
    with col3:
        st.info(f"**Objetivo:** Irrigação Inteligente")
    
    st.markdown("---")
    
    # Preparar dados
    with st.spinner("Carregando dados para Machine Learning..."):
        df = preparar_dados_ml()
    
    if df is not None and len(df) > 10:
        st.success(f"Dados carregados: {len(df)} registros para análise ML")
        
        # Estatísticas dos dados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Registros", len(df))
        with col2:
            irrigacoes = df['bomba_dagua'].sum()
            st.metric("Irrigações", f"{irrigacoes}")
        with col3:
            umidade_media = df['umidade'].mean()
            st.metric("Umidade Média", f"{umidade_media:.1f}%")
        with col4:
            temp_media = df['temperatura'].mean()
            st.metric("Temp Média", f"{temp_media:.1f}°C")
        
        st.markdown("---")
        
        # Seleção de modelos
        ml_opcao = st.selectbox(
            "**Selecione o modelo de Machine Learning:**",
            [
                "Selecione um modelo...",
                "Modelo de Previsão de Irrigação",
                "Modelo de Previsão de Umidade",
                "Sistema Inteligente Completo",
                "Análise de Importância das Variáveis"
            ]
        )
        
        st.markdown("---")
        
        if ml_opcao == "Modelo de Previsão de Irrigação":
            st.subheader("Previsão de Necessidade de Irrigação")
            
            if st.button("Treinar Modelo de Irrigação", use_container_width=True):
                with st.spinner("Treinando modelo Random Forest..."):
                    modelo, accuracy, feature_importance, X_test, y_test, y_pred = treinar_modelo_irrigacao(df)
                
                if modelo is not None:
                    st.success(f"Modelo treinado com sucesso!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Acurácia do Modelo", f"{accuracy:.3f}")
                        
                        # Matriz de confusão simples
                        # Garante que a matriz seja 2x2, mesmo com dados de teste desbalanceados
                        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
                        st.text("Matriz de Confusão:")
                        st.dataframe(pd.DataFrame(cm, 
                                               columns=['Pred: Não Irrigar', 'Pred: Irrigar'],
                                               index=['Real: Não Irrigar', 'Real: Irrigar']))
                    
                    with col2:
                        st.text("Importância das Variáveis:")
                        fig_importance = px.bar(feature_importance, 
                                              x='importance', 
                                              y='feature',
                                              orientation='h',
                                              title="Importância das Features")
                        st.plotly_chart(fig_importance, use_container_width=True)
        
        elif ml_opcao == "Modelo de Previsão de Umidade":
            st.subheader("Previsão de Umidade do Solo")
            
            if st.button("Treinar Modelo de Umidade", use_container_width=True):
                with st.spinner("Treinando modelo Random Forest..."):
                    modelo, scaler, rmse, feature_importance, X_test, y_test, y_pred = treinar_modelo_umidade(df)
                
                if modelo is not None:
                    st.success(f"Modelo de umidade treinado!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("RMSE", f"{rmse:.2f}%")
                        
                        # Gráfico de predição vs real
                        fig_pred = px.scatter(x=y_test, y=y_pred,
                                            labels={'x': 'Umidade Real (%)', 'y': 'Umidade Prevista (%)'},
                                            title="Predição vs Realidade")
                        fig_pred.add_shape(type="line", x0=y_test.min(), y0=y_test.min(), 
                                         x1=y_test.max(), y1=y_test.max(), line=dict(color="red", dash="dash"))
                        st.plotly_chart(fig_pred, use_container_width=True)
                    
                    with col2:
                        st.text("Importância das Variáveis:")
                        fig_importance = px.bar(feature_importance, 
                                              x='importance', 
                                              y='feature',
                                              orientation='h',
                                              title="Importância das Features")
                        st.plotly_chart(fig_importance, use_container_width=True)
        
        elif ml_opcao == "Sistema Inteligente Completo":
            st.subheader("Sistema de Irrigação Inteligente")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Treinar Modelo de Irrigação", use_container_width=True):
                    with st.spinner("Treinando modelo de irrigação..."):
                        modelo_irrig, accuracy, _, _, _, _ = treinar_modelo_irrigacao(df)
                        if modelo_irrig:
                            st.session_state.modelo_irrigacao = modelo_irrig
                            st.success(f"Modelo irrigação: {accuracy:.3f}")
            
            with col2:
                if st.button("Treinar Modelo de Umidade", use_container_width=True):
                    with st.spinner("Treinando modelo de umidade..."):
                        modelo_umid, scaler, rmse, _, _, _, _ = treinar_modelo_umidade(df)
                        if modelo_umid:
                            st.session_state.modelo_umidade = modelo_umid
                            st.session_state.scaler_umidade = scaler
                            st.success(f"Modelo umidade: RMSE {rmse:.2f}")
            
            st.markdown("---")
            
            # Sistema de recomendações
            if st.button("Gerar Recomendações Inteligentes", use_container_width=True):
                if (hasattr(st.session_state, 'modelo_irrigacao') and 
                    hasattr(st.session_state, 'modelo_umidade') and
                    hasattr(st.session_state, 'scaler_umidade')):
                    
                    with st.spinner("Calculando recomendações..."):
                        recomendacoes = prever_irrigacao_inteligente(
                            st.session_state.modelo_irrigacao,
                            st.session_state.modelo_umidade,
                            st.session_state.scaler_umidade
                        )
                    
                    if recomendacoes:
                        st.subheader("Recomendações de Irrigação")
                        
                        for rec in recomendacoes:
                            with st.expander(f"{rec['cenario']} - {rec['recomendacao']}"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write(f"**Temperatura:** {rec['temperatura']}°C")
                                    st.write(f"**pH:** {rec['ph']}")
                                    st.write(f"**Nutrientes:** {rec['nutrientes']}")
                                
                                with col2:
                                    st.write(f"**Prob. Irrigação:** {rec['prob_irrigacao']:.3f}")
                                    st.write(f"**Umidade sem irrigação:** {rec['umidade_sem_irrig']:.1f}%")
                                    st.write(f"**Umidade com irrigação:** {rec['umidade_com_irrig']:.1f}%")
                                
                                with col3:
                                    st.write(f"**{rec['recomendacao']}**")
                                    st.write(rec['motivo'])
                
                else:
                    st.warning("Treine ambos os modelos primeiro!")
        
        elif ml_opcao == "Análise de Importância das Variáveis":
            st.subheader("Análise de Features")
            
            if st.button("Analisar Importância", use_container_width=True):
                modelo_irrig, _, feat_irrig, _, _, _ = treinar_modelo_irrigacao(df)
                modelo_umid, _, _, feat_umid, _, _, _ = treinar_modelo_umidade(df)
                
                if modelo_irrig and modelo_umid:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text("Importância para Irrigação:")
                        fig1 = px.bar(feat_irrig, x='importance', y='feature', orientation='h',
                                     title="Features mais importantes para Irrigação")
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        st.text("Importância para Umidade:")
                        fig2 = px.bar(feat_umid, x='importance', y='feature', orientation='h',
                                     title="Features mais importantes para Umidade")
                        st.plotly_chart(fig2, use_container_width=True)
        
        else:
            st.info("Selecione um modelo no menu acima para começar")
            
            # Informações sobre Machine Learning
            st.subheader("Sobre os Modelos de Machine Learning")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Modelo de Irrigação:**
                - Algoritmo: Random Forest Classifier
                - Objetivo: Prever se deve irrigar (Sim/Não)
                - Features: Temperatura, pH, Nutrientes, Hora
                - Métrica: Acurácia
                """)
            
            with col2:
                st.markdown("""
                **Modelo de Umidade:**
                - Algoritmo: Random Forest Regressor
                - Objetivo: Prever nível de umidade
                - Features: Temperatura, pH, Bomba, Hora
                - Métrica: RMSE (Erro Quadrático Médio)
                """)
            
            st.markdown("""
            **Sistema Inteligente:**
            
            O sistema combina ambos os modelos para tomar decisões inteligentes:
            1. **Coleta dados** dos sensores (temperatura, pH, nutrientes)
            2. **Coleta dados meteorológicos** (chuva, vento, pressão)
            3. **Calcula probabilidade** de necessidade de irrigação
            4. **Prevê umidade** com e sem irrigação
            5. **Gera recomendação** baseada em múltiplos fatores
            6. **Aprende continuamente** com novos dados
            
            **Benefícios com Meteorologia:**
            - Não irriga se vai chover
            - Considera evaporação por vento
            - Otimiza baseado na pressão atmosférica
            - Ajusta para umidade do ar
            - Economia de água inteligente
            """)
        
        # Seção sobre dados meteorológicos
        st.subheader("Integração Meteorológica")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Dados Coletados:**
            - Temperatura externa
            - Umidade do ar
            - Velocidade do vento
            - Pressão atmosférica
            - Probabilidade de chuva
            - Índice UV
            """)
        
        with col2:
            st.markdown("""
            **🧠 Como a IA Usa:**
            - Se prob. chuva > 70% → NÃO irrigar
            - Se vento forte → Aumentar irrigação
            - Se pressão baixa → Aguardar chuva
            - Se temp. alta → Irrigar mais cedo
            - Se umidade ar baixa → Irrigar mais
            """)
    
    else:
        st.error("Dados insuficientes para Machine Learning")
        st.info("Aguarde mais dados serem coletados pelos sensores ou insira dados manualmente via CRUD")
        
        # Botão para popular dados de teste
        if st.button("Gerar Dados de Teste para ML", use_container_width=True):
            with st.spinner("Gerando dados de teste..."):
                dados_gerados = gerar_dados_teste_ml()
                if dados_gerados > 0:
                    st.success(f"{dados_gerados} registros de teste gerados!")
                    st.info("Recarregue a página para treinar os modelos")

def gerar_dados_teste_ml():
    """Gera dados de teste para demonstrar o ML"""
    try:
        import random
        from datetime import datetime, timedelta
        
        dados_gerados = 0
        
        # Gera 50 registros de teste dos últimos 7 dias
        for i in range(50):
            # Data aleatória nos últimos 7 dias
            data_base = datetime.now() - timedelta(days=random.randint(0, 7))
            data_base = data_base - timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Dados dos sensores
            umidade = random.uniform(20, 80)
            temperatura = random.uniform(18, 35)
            ph = random.uniform(5.5, 8.0)
            fosforo = random.choice([True, False])
            potassio = random.choice([True, False])
            
            # Lógica para bomba (baseada em umidade)
            bomba = umidade < 35 or (umidade < 50 and temperatura > 30)
            
            # Dados meteorológicos simulados
            temp_externa = temperatura + random.uniform(-3, 5)
            umidade_ar = random.uniform(45, 95)
            pressao = random.uniform(1000, 1025)
            vento = random.uniform(2, 20)
            prob_chuva = random.uniform(0, 100)
            chuva = random.uniform(0, 8) if prob_chuva > 70 else 0
            
            dados_meteorologicos = {
                'temperatura_externa': temp_externa,
                'umidade_ar': umidade_ar,
                'pressao_atmosferica': pressao,
                'velocidade_vento': vento,
                'direcao_vento': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
                'condicao_clima': random.choice(['Ensolarado', 'Nublado', 'Chuva leve', 'Chuva']),
                'probabilidade_chuva': prob_chuva,
                'quantidade_chuva': chuva,
                'indice_uv': random.uniform(0, 11),
                'visibilidade': random.uniform(5, 30),
                'cidade': 'Camopi (Teste)',
                'fonte_dados': 'Dados de Teste'
            }
            
            dados_sensores = {
                'umidade': umidade,
                'temperatura': temperatura,
                'ph': ph,
                'fosforo': fosforo,
                'potassio': potassio,
                'bomba_dagua': bomba
            }
            
            # Salva dados meteorológicos
            if salvar_dados_meteorologicos(dados_meteorologicos):
                # Cria leitura integrada
                if criar_leitura_integrada(dados_sensores, dados_meteorologicos):
                    dados_gerados += 1
        
        return dados_gerados
        
    except Exception as e:
        st.error(f"Erro ao gerar dados de teste: {e}")
        return 0

# === FUNÇÕES PARA DADOS METEOROLÓGICOS ===

@st.cache_data(ttl=300)  # Cache por 5 minutos
def coletar_dados_meteorologicos():
    """Coleta dados meteorológicos da API OpenWeatherMap"""
    try:
        # Para demonstração, vamos usar dados simulados mais realistas
        # Em produção, descomente e configure a API real
        
        import random
        from datetime import datetime
        
        # Simula condições climáticas mais realistas baseadas na hora
        hora_atual = datetime.now().hour
        
        # Temperatura varia conforme o horário
        if 6 <= hora_atual <= 12:  # Manhã
            temp_base = 24 + random.uniform(-2, 3)
        elif 12 <= hora_atual <= 18:  # Tarde
            temp_base = 29 + random.uniform(-3, 4)
        elif 18 <= hora_atual <= 22:  # Noite
            temp_base = 26 + random.uniform(-2, 2)
        else:  # Madrugada
            temp_base = 22 + random.uniform(-1, 2)
        
        # Umidade do ar inversamente relacionada à temperatura
        umidade_ar = max(45, min(95, 85 - (temp_base - 22) * 2 + random.uniform(-5, 5)))
        
        # Pressão atmosférica com variação realista
        pressao = 1013.25 + random.uniform(-15, 15)
        
        # Vento com padrões diurnos
        if 10 <= hora_atual <= 16:  # Ventos mais fortes durante o dia
            vento = random.uniform(8, 18)
        else:  # Ventos mais calmos à noite
            vento = random.uniform(3, 12)
        
        # Probabilidade de chuva baseada em umidade e pressão
        if umidade_ar > 80 and pressao < 1010:
            prob_chuva = random.uniform(60, 95)
        elif umidade_ar > 70:
            prob_chuva = random.uniform(20, 60)
        else:
            prob_chuva = random.uniform(0, 20)
        
        # Quantidade de chuva se probabilidade for alta
        if prob_chuva > 70:
            chuva = random.uniform(0.5, 8.0)
        elif prob_chuva > 40:
            chuva = random.uniform(0.0, 2.0)
        else:
            chuva = 0.0
        
        # Condições climáticas baseadas em chuva e temperatura
        if chuva > 2:
            condicao = random.choice(["Chuva forte", "Tempestade", "Chuva"])
        elif chuva > 0:
            condicao = random.choice(["Chuva leve", "Garoa", "Chuvisco"])
        elif temp_base > 30:
            condicao = random.choice(["Ensolarado", "Muito quente", "Céu limpo"])
        elif umidade_ar > 80:
            condicao = random.choice(["Nublado", "Muito úmido", "Neblina"])
        else:
            condicao = random.choice(["Parcialmente nublado", "Ensolarado", "Céu limpo"])
        
        # Direção do vento
        direcoes = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        direcao_vento = random.choice(direcoes)
        
        # Índice UV baseado na hora e condições
        if 10 <= hora_atual <= 16 and "Ensolarado" in condicao:
            indice_uv = random.uniform(6, 11)
        elif 8 <= hora_atual <= 18:
            indice_uv = random.uniform(2, 8)
        else:
            indice_uv = random.uniform(0, 2)
        
        # Visibilidade baseada em chuva e umidade
        if chuva > 5:
            visibilidade = random.uniform(2, 8)
        elif umidade_ar > 85:
            visibilidade = random.uniform(8, 15)
        else:
            visibilidade = random.uniform(15, 30)
        
        dados_meteorologicos = {
            'temperatura_externa': round(temp_base, 1),
            'umidade_ar': round(umidade_ar, 1),
            'pressao_atmosferica': round(pressao, 2),
            'velocidade_vento': round(vento, 1),
            'direcao_vento': direcao_vento,
            'condicao_clima': condicao,
            'probabilidade_chuva': round(prob_chuva, 1),
            'quantidade_chuva': round(chuva, 1),
            'indice_uv': round(indice_uv, 1),
            'visibilidade': round(visibilidade, 1),
            'cidade': 'Camopi (Simulado)',
            'fonte_dados': 'Simulação Inteligente'
        }
        
        return dados_meteorologicos
        
    except Exception as e:
        st.error(f"Erro ao coletar dados meteorológicos: {e}")
        return None

def salvar_dados_meteorologicos(dados_met):
    """Salva dados meteorológicos no banco PostgreSQL"""
    try:
        conn, cursor = conectar_postgres()
        if conn and dados_met:
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.dados_meteorologicos 
                (temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento, 
                 direcao_vento, condicao_clima, probabilidade_chuva, quantidade_chuva,
                 indice_uv, visibilidade, cidade, fonte_dados)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados_met['temperatura_externa'],
                dados_met['umidade_ar'], 
                dados_met['pressao_atmosferica'],
                dados_met['velocidade_vento'],
                dados_met['direcao_vento'],
                dados_met['condicao_clima'],
                dados_met['probabilidade_chuva'],
                dados_met['quantidade_chuva'],
                dados_met['indice_uv'],
                dados_met['visibilidade'],
                dados_met['cidade'],
                dados_met['fonte_dados']
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Erro ao salvar dados meteorológicos: {e}")
        return False

def calcular_fatores_evapotranspiracao(temp_solo, temp_externa, umidade_ar, vento):
    """Calcula fatores que afetam a evapotranspiração"""
    try:
        # Diferença de temperatura (externa - solo)
        diferenca_temp = temp_externa - temp_solo
        
        # Déficit de umidade (ar - solo) - aproximação
        # Assumindo que umidade do solo ideal é ~40-60%
        deficit_umidade = umidade_ar - 50  # Referência
        
        # Fator de evapotranspiração baseado em Penman-Monteith simplificado
        # ET = f(temperatura, vento, déficit de umidade)
        fator_et = (temp_externa * 0.3) + (vento * 0.2) - (umidade_ar * 0.1)
        fator_et = max(0, fator_et)  # Não pode ser negativo
        
        return diferenca_temp, deficit_umidade, fator_et
        
    except Exception:
        return 0, 0, 0

def criar_leitura_integrada(dados_sensores, dados_meteorologicos):
    """Combina dados dos sensores com dados meteorológicos"""
    try:
        # Calcula fatores derivados
        diferenca_temp, deficit_umidade, fator_et = calcular_fatores_evapotranspiracao(
            dados_sensores.get('temperatura', 25),
            dados_meteorologicos.get('temperatura_externa', 25),
            dados_meteorologicos.get('umidade_ar', 70),
            dados_meteorologicos.get('velocidade_vento', 5)
        )
        
        conn, cursor = conectar_postgres()
        if conn:
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.leituras_integradas 
                (umidade_solo, temperatura_solo, ph_solo, fosforo, potassio, bomba_dagua,
                 temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento,
                 condicao_clima, probabilidade_chuva, quantidade_chuva,
                 diferenca_temperatura, deficit_umidade, fator_evapotranspiracao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados_sensores.get('umidade', 0),
                dados_sensores.get('temperatura', 0),
                dados_sensores.get('ph', 7.0),
                dados_sensores.get('fosforo', False),
                dados_sensores.get('potassio', False),
                dados_sensores.get('bomba_dagua', False),
                dados_meteorologicos.get('temperatura_externa', 25),
                dados_meteorologicos.get('umidade_ar', 70),
                dados_meteorologicos.get('pressao_atmosferica', 1013),
                dados_meteorologicos.get('velocidade_vento', 5),
                dados_meteorologicos.get('condicao_clima', 'Desconhecido'),
                dados_meteorologicos.get('probabilidade_chuva', 0),
                dados_meteorologicos.get('quantidade_chuva', 0),
                diferenca_temp,
                deficit_umidade,
                fator_et
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Erro ao criar leitura integrada: {e}")
        return False

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
    st.title("FarmTech Solutions Dashboard")
    
    # Botões de navegação principal - Agora com 4 colunas
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("Gerenciamento CRUD", use_container_width=True, type="primary"):
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
                Live Plotter
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Análise R", use_container_width=True, type="secondary"):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col4:
        if st.button("Machine Learning", use_container_width=True, type="secondary"):
            st.session_state.current_page = "ml"
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
    elif current_page == "ml":
        pagina_ml_scikit()
        return  # Sai da função para não mostrar o dashboard
    
    # === DASHBOARD PRINCIPAL ===
    
    # Sidebar para controles
    with st.sidebar:
        st.header("Controles")
        auto_refresh = st.checkbox("Atualização Automática", value=True)
        refresh_interval = st.slider("Intervalo (segundos)", 3, 60, 45)
        
        # Checkbox para coleta automática de dados meteorológicos
        coletar_meteorologia = st.checkbox("Coletar Meteorologia", value=True)
        
        if st.button("Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
        
        # Se habilitado, coleta e salva dados meteorológicos
        if coletar_meteorologia:
            dados_met = coletar_dados_meteorologicos()
            if dados_met:
                # Salva no banco a cada 10 minutos (para não sobrecarregar)
                if st.session_state.get('ultimo_salvamento_met', 0) + 600 < time.time():
                    if salvar_dados_meteorologicos(dados_met):
                        st.session_state.ultimo_salvamento_met = time.time()
                        st.success("Meteorologia salva!")
        
        st.markdown("---")
        st.header("Servidor")
        st.info(f"URL: {FLASK_SERVER_URL}")
        st.info(f"DB: {DatabaseConfig.HOST}")
        st.info(f"Schema: {DatabaseConfig.SCHEMA}")
    
    # Placeholder para status de conexão
    status_placeholder = st.empty()
    
    # Obtém dados dos sensores
    sensor_data = get_sensor_data()
    
    if sensor_data and sensor_data.get('dados'):
        # Status de conexão
        status_placeholder.success(f"Conectado - {sensor_data.get('total_registros', 0)} registros")
        
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
            st.header("Dados Atuais")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                temp_value = ultimo_registro.get('temperatura', 0)
                try:
                    temp_float = float(temp_value)
                    temp_display = f"{temp_float:.1f}°C"
                except:
                    temp_display = f"{temp_value}°C"
                
                st.metric(
                    label="Temperatura",
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
                    label="Umidade",
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
                    label="pH",
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
                    label="Bomba",
                    value="Ligada" if bomba_ligada else "Desligada",
                    delta=None
                )
            
            # === SEÇÃO 2: STATUS DOS NUTRIENTES ===
            st.header("Nutrientes")
            col1, col2 = st.columns(2)
            
            with col1:
                fosforo_value = ultimo_registro.get('fosforo', False)
                if isinstance(fosforo_value, str):
                    fosforo_presente = fosforo_value.lower() in ['true', 'presente', '1']
                else:
                    fosforo_presente = bool(fosforo_value)
                
                if fosforo_presente:
                    st.success("Fósforo: Presente")
                else:
                    st.error("Fósforo: Ausente")
            
            with col2:
                potassio_value = ultimo_registro.get('potassio', False)
                if isinstance(potassio_value, str):
                    potassio_presente = potassio_value.lower() in ['true', 'presente', '1']
                else:
                    potassio_presente = bool(potassio_value)
                
                if potassio_presente:
                    st.success("Potássio: Presente")
                else:
                    st.error("Potássio: Ausente")
            
            # === SEÇÃO 3: GRÁFICOS ===
            st.header("Tendências")
            
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
                                title='Umidade do Solo',
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
                                title='Temperatura do Solo',
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
                            title='Nível de pH',
                            labels={'ph': 'pH', 'data_hora_leitura': 'Horário'}
                        )
                        fig_ph.update_traces(line_color='#2ca02c')
                        fig_ph.add_hline(y=7, line_dash="dash", line_color="red", 
                                       annotation_text="pH Neutro (7)")
                        st.plotly_chart(fig_ph, use_container_width=True)
                else:
                    st.warning("Dados insuficientes para gráficos")
            
            # === SEÇÃO 4: DADOS CLIMÁTICOS ===
            st.header("Condições Climáticas")
            
            clima = get_clima_atual()
            
            if clima and clima.get('cidade') != 'Erro':
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info(f"**Cidade:** {clima['cidade']}")
                    st.info(f"**Temperatura:** {clima['temperatura']}°C")
                
                with col2:
                    st.info(f"**Umidade:** {clima['umidade']}%")
                    st.info(f"**Condição:** {clima['condicao']}")
                
                with col3:
                    st.info(f"**Vento:** {clima['vento']} m/s")
                    st.info(f"**Chuva:** {clima['chuva']} mm")
                
                # Alerta de chuva
                if clima['vai_chover']:
                    st.warning(f"**ALERTA:** Previsão de {clima['chuva']} mm de chuva! Manter bomba d'água desligada!")
                else:
                    st.success("Sem previsão de chuva nas próximas horas.")
            else:
                st.error("Erro ao obter dados climáticos")
    
            # === SEÇÃO 5: TABELA DE DADOS ===
            st.header("Histórico de Leituras")
            
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
                st.warning("Nenhum dado encontrado")
    
    # Mensagem de erro de conexão
    if not sensor_data or not sensor_data.get('dados'):
        status_placeholder.error("Erro ao conectar com o servidor ou sem dados")
        st.error("Verifique se o servidor Flask está rodando em http://127.0.0.1:8000")
    
    # Auto-refresh otimizado
    if auto_refresh:
        # Mostra próxima atualização
        with st.empty():
            for i in range(refresh_interval, 0, -1):
                st.caption(f"Próxima atualização em {i} segundos...")
                time.sleep(1)
        
        # Limpa cache e recarrega
        st.cache_data.clear()
        st.rerun()

# --- Execução principal ---
if __name__ == "__main__":
    main() 