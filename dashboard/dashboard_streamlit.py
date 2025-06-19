import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import time

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL do servidor Flask local
FLASK_SERVER_URL = "http://127.0.0.1:8000/get_data"

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
@st.cache_data(ttl=5)  # Cache por 5 segundos
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

# --- Interface principal ---
def main():
    # Título principal
    st.title("🌱 FarmTech Solutions Dashboard")
    
    # Botão de acesso rápido ao plotter
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            "📈 Ver Gráficos Avançados (Live Plotter)",
            "http://localhost:8000/plotter",
            help="Acessa visualizações interativas em tempo real com Chart.js",
            type="secondary",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Sidebar para controles
    with st.sidebar:
        st.header("⚙️ Controles")
        auto_refresh = st.checkbox("🔄 Atualização Automática", value=True)
        refresh_interval = st.slider("Intervalo (segundos)", 3, 30, 5)
        
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.header("📊 Visualizações")
        
        # Botão para abrir o plotter
        st.link_button(
            "📈 Abrir Plotter Avançado",
            "http://localhost:8000/plotter",
            help="Abre gráficos interativos em tempo real",
            type="primary"
        )
        
        st.markdown("---")
        st.header("📊 Servidor")
        st.info(f"URL: {FLASK_SERVER_URL}")
    
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
            st.warning("⚠️ Nenhum dado encontrado")
    
    else:
        status_placeholder.error("❌ Erro ao conectar com o servidor ou sem dados")
        st.error("Verifique se o servidor Flask está rodando em http://127.0.0.1:8000")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

# --- Execução principal ---
if __name__ == "__main__":
    main() 