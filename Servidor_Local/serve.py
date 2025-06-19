from flask import Flask, request, jsonify, Response
import sys
import os
from datetime import datetime
import pytz
import random
import math
import psycopg2
from psycopg2 import sql, pool
import threading
import time
import atexit

# --- INÍCIO: Adicionado para o Plotter ---
# Template HTML para a página do plotter.
# Contém HTML, CSS e JavaScript (com Chart.js) em um só lugar.
PLOTTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farm Tech - Live Plotter</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        /* Estilo inspirado no Streamlit */
        body { 
            font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #262730; 
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        h1 { 
            color: #ff6b6b; 
            font-weight: 600;
            font-size: 2.5rem;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .subtitle {
            color: #555;
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }
        
        .navigation {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .btn-dashboard {
            background: #ff6b6b;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(255, 107, 107, 0.3);
        }
        
        .btn-dashboard:hover {
            background: #ff5252;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(255, 107, 107, 0.4);
        }
        
        .chart-container {
            width: 90%;
            max-width: 1000px;
            margin: 20px auto;
            padding: 25px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-left: 4px solid #ff6b6b;
            transition: transform 0.2s ease;
        }
        
        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        }
        
        .chart-container h2 {
            color: #262730;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            font-size: 1.4rem;
        }
        
        .chart-container h2::before {
            content: "📊";
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        /* Estilos específicos para cada tipo de gráfico */
        .chart-container:nth-child(3) h2::before { content: "🌡️💧"; }
        .chart-container:nth-child(4) h2::before { content: "⚗️"; }
        .chart-container:nth-child(5) h2::before { content: "🔧"; }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .chart-container {
                width: 95%;
                padding: 15px;
                margin: 15px auto;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            body {
                padding: 10px;
            }
        }
        
        /* Loading animation */
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
            font-style: italic;
        }
        
        /* Status indicator */
        .status-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
            z-index: 1000;
        }
        
        .status-indicator::before {
            content: "🟢";
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <!-- Status indicator -->
    <div class="status-indicator">Live Data</div>
    
    <!-- Header section -->
    <div class="header">
        <h1>🌱 Farm Tech Solutions</h1>
        <div class="subtitle">Live Data Plotter - Visualização Avançada</div>
    </div>
    
    <!-- Navigation -->
    <div class="navigation">
        <a href="http://localhost:8501" class="btn-dashboard" target="_self">
            ← Voltar ao Dashboard Principal
        </a>
    </div>

    <div class="chart-container">
        <h2>Temperatura & Umidade</h2>
        <canvas id="tempHumidityChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>Nível de pH</h2>
        <canvas id="phChart"></canvas>
    </div>
    
    <div class="chart-container">
        <h2>Status dos Componentes</h2>
        <canvas id="statusChart"></canvas>
    </div>

    <script>
        // Função para converter booleano de string ('true'/'false') para número (1/0)
        const boolToNum = (val) => val === true || val === 'true' ? 1 : 0;

        // Configuração inicial dos gráficos
        const tempHumidityCtx = document.getElementById('tempHumidityChart').getContext('2d');
        const tempHumidityChart = new Chart(tempHumidityCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Temperatura (°C)',
                        data: [],
                        borderColor: '#ff6b6b',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        yAxisID: 'yTemp',
                        tension: 0.3,
                        borderWidth: 3,
                        pointBackgroundColor: '#ff6b6b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    },
                    {
                        label: 'Umidade (%)',
                        data: [],
                        borderColor: '#4ecdc4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        yAxisID: 'yHumidity',
                        tension: 0.3,
                        borderWidth: 3,
                        pointBackgroundColor: '#4ecdc4',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }
                ]
            },
            options: {
                scales: {
                    x: { 
                        type: 'time', 
                        time: { unit: 'second', displayFormats: { second: 'HH:mm:ss' } },
                        title: { display: true, text: 'Horário da Leitura' }
                    },
                    yTemp: {
                        type: 'linear',
                        position: 'left',
                        title: { display: true, text: 'Temperatura (°C)' }
                    },
                    yHumidity: {
                        type: 'linear',
                        position: 'right',
                        title: { display: true, text: 'Umidade (%)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });

        const phCtx = document.getElementById('phChart').getContext('2d');
        const phChart = new Chart(phCtx, {
            type: 'line',
            data: {
                labels: [],
                            datasets: [{
                label: 'pH',
                data: [],
                borderColor: '#45b7d1',
                backgroundColor: 'rgba(69, 183, 209, 0.1)',
                tension: 0.3,
                borderWidth: 3,
                pointBackgroundColor: '#45b7d1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
            },
            options: { scales: { x: { type: 'time', time: { unit: 'second', displayFormats: { second: 'HH:mm:ss' } } } } }
        });
        
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        const statusChart = new Chart(statusCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { 
                        label: 'Bomba', 
                        data: [], 
                        borderColor: '#ff6b6b', 
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        stepped: true,
                        borderWidth: 3,
                        pointBackgroundColor: '#ff6b6b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    },
                    { 
                        label: 'Fósforo', 
                        data: [], 
                        borderColor: '#ffa726', 
                        backgroundColor: 'rgba(255, 167, 38, 0.1)',
                        stepped: true,
                        borderWidth: 3,
                        pointBackgroundColor: '#ffa726',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    },
                    { 
                        label: 'Potássio', 
                        data: [], 
                        borderColor: '#66bb6a', 
                        backgroundColor: 'rgba(102, 187, 106, 0.1)',
                        stepped: true,
                        borderWidth: 3,
                        pointBackgroundColor: '#66bb6a',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6
                    }
                ]
            },
            options: {
                scales: {
                    x: { type: 'time', time: { unit: 'second', displayFormats: { second: 'HH:mm:ss' } } },
                    y: {
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return value === 1 ? 'Ligado/Detectado' : 'Desligado';
                            }
                        },
                        max: 1.2,
                        min: -0.2
                    }
                }
            }
        });


        // Função para buscar dados e atualizar os gráficos
        async function updateCharts() {
            try {
                // Mostra indicador de loading
                document.querySelector('.status-indicator').textContent = '🔄 Atualizando...';
                
                const response = await fetch('/get_data');
                const result = await response.json();
                let data = result.dados;

                // Os dados vêm em ordem decrescente, vamos invertê-los para o gráfico
                data.reverse();
                
                // Limita a 20 pontos de dados para não sobrecarregar a tela
                const maxDataPoints = 20;
                if(data.length > maxDataPoints) {
                    data = data.slice(data.length - maxDataPoints);
                }

                // Extrai os dados para os gráficos
                const labels = data.map(d => new Date(d.data_hora_leitura));
                const temperatures = data.map(d => d.temperatura);
                const humidities = data.map(d => d.umidade);
                const phs = data.map(d => d.ph);
                const pumpStatus = data.map(d => boolToNum(d.bomba_dagua));
                const phosphorusStatus = data.map(d => boolToNum(d.fosforo));
                const potassiumStatus = data.map(d => boolToNum(d.potassio));

                // Atualiza o gráfico de Temperatura e Umidade
                tempHumidityChart.data.labels = labels;
                tempHumidityChart.data.datasets[0].data = temperatures;
                tempHumidityChart.data.datasets[1].data = humidities;
                tempHumidityChart.update();

                // Atualiza o gráfico de pH
                phChart.data.labels = labels;
                phChart.data.datasets[0].data = phs;
                phChart.update();
                
                // Atualiza o gráfico de Status
                statusChart.data.labels = labels;
                statusChart.data.datasets[0].data = pumpStatus;
                statusChart.data.datasets[1].data = phosphorusStatus;
                statusChart.data.datasets[2].data = potassiumStatus;
                statusChart.update();
                
                // Atualiza indicador de sucesso
                document.querySelector('.status-indicator').textContent = '🟢 Live Data';

            } catch (error) {
                console.error('Erro ao buscar ou atualizar dados:', error);
                document.querySelector('.status-indicator').textContent = '🔴 Erro';
                document.querySelector('.status-indicator').style.background = '#f44336';
            }
        }

        // Inicia a atualização e a repete a cada 5 segundos
        updateCharts();
        setInterval(updateCharts, 5000); // 5000 ms = 5 segundos
    </script>
</body>
</html>
"""
# --- FIM: Adicionado para o Plotter ---

# Adiciona o diretório raiz ao path para importar o config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.database_config import _config as DatabaseConfig, conectar_postgres, criar_schema_e_tabela

# Timezone brasileiro
BRASIL_TZ = pytz.timezone('America/Sao_Paulo')

app = Flask(__name__)

# Tenta inicializar schema e tabela, mas não trava se falhar
print("🚀 Iniciando servidor Flask...")
try:
    criar_schema_e_tabela()
    print("✅ Banco de dados inicializado com sucesso!")
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível conectar ao banco: {e}")
    print("🔄 Servidor continuará rodando. Você pode configurar o banco depois.")

# === POOL DE CONEXÕES PARA PERFORMANCE ===
connection_pool = None

def inicializar_pool_conexoes():
    """Inicializa pool de conexões para performance ultra-rápida."""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,  # Mínimo 2 conexões sempre abertas
            maxconn=10, # Máximo 10 conexões simultâneas
            **DatabaseConfig.get_connection_params()
        )
        print("🚀 Pool de conexões PostgreSQL inicializado (2-10 conexões)")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar pool: {e}")
        return False

def obter_conexao_pool():
    """Obtém conexão do pool (ULTRA-RÁPIDO)."""
    global connection_pool
    if connection_pool:
        try:
            conn = connection_pool.getconn()
            if conn:
                cursor = conn.cursor()
                # Configurações rápidas
                cursor.execute(f"SET search_path TO {DatabaseConfig.SCHEMA}, public")
                return conn, cursor
        except Exception as e:
            print(f"⚠️ Erro ao obter conexão do pool: {e}")
    return None, None

def devolver_conexao_pool(conn):
    """Devolve conexão para o pool."""
    global connection_pool
    if connection_pool and conn:
        connection_pool.putconn(conn)

def fechar_pool_conexoes():
    """Fecha o pool de conexões."""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("🔒 Pool de conexões fechado")

# Registra função para fechar pool ao encerrar aplicação
atexit.register(fechar_pool_conexoes)

def converter_para_boolean(valor):
    """
    Converte string para boolean.
    ESP32 pode enviar: 'true'/'false', 'presente'/'ausente', 'on'/'off'
    """
    if isinstance(valor, bool):
        return valor
    
    if isinstance(valor, str):
        valor = valor.lower().strip()
        return valor in ['true', 'presente', 'on', '1', 'yes', 'sim']
    
    # Default para False se não conseguir determinar
    return False

def inserir_dados(umidade, temperatura, ph, fosforo, potassio, bomba_dagua, timestamp_esp32=None):
    """Insere uma nova leitura de dados na tabela 'leituras_sensores' do PostgreSQL."""
    conn, cursor = conectar_postgres()
    if conn and cursor:
        # Usa timestamp do ESP32 se fornecido, senão usa timestamp do servidor
        if timestamp_esp32:
            # Converte string para timestamp se necessário
            if isinstance(timestamp_esp32, str):
                try:
                    # Tenta formato ISO primeiro (YYYY-MM-DDTHH:MM:SS)
                    data_hora_leitura = datetime.strptime(timestamp_esp32, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    try:
                        # Fallback para formato com espaço
                        data_hora_leitura = datetime.strptime(timestamp_esp32, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"⚠️ Formato de timestamp inválido: {timestamp_esp32}")
                        data_hora_leitura = datetime.now()
            else:
                data_hora_leitura = timestamp_esp32
            timestamp_source = "ESP32"
        else:
            data_hora_leitura = datetime.now()
            timestamp_source = "Servidor"
            
        try:
            # Nova estrutura: id (autoincremento), data_hora_leitura, criacaots (auto), dados sensores
            # Força timestamp brasileiro para criacaots
            timestamp_brasil = datetime.now(BRASIL_TZ)
            
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.leituras_sensores 
                (data_hora_leitura, criacaots, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (data_hora_leitura, timestamp_brasil, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
            )
            conn.commit()
            print(f"✅ Dados inseridos no PostgreSQL ({DatabaseConfig.SCHEMA}) em {data_hora_leitura}!")
            print(f"🕐 Timestamp fonte: {timestamp_source}")
            print(f"📊 Umidade: {umidade}% | Temperatura: {temperatura}°C | pH: {ph}")
            print(f"📊 Fósforo: {'✅ Detectado' if fosforo else '❌ Não detectado'}")
            print(f"📊 Potássio: {'✅ Detectado' if potassio else '❌ Não detectado'}")
            print(f"🚰 Bomba: {'✅ Ligada' if bomba_dagua else '❌ Desligada'}")
            print("🆔 ID gerado automaticamente pelo banco | ⏰ Timestamp de criação definido automaticamente")
            return True
        except Exception as error:
            print(f"❌ Erro ao inserir dados no PostgreSQL: {error}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    else:
        print("❌ Não foi possível conectar ao banco de dados.")
        return False

def listar_dados():
    """Lista todas as leituras da tabela 'leituras_sensores' do PostgreSQL."""
    conn, cursor = conectar_postgres()
    registros = []
    if conn and cursor:
        try:
            cursor.execute(f"""
                SELECT id, data_hora_leitura, criacaots, umidade, temperatura, ph, fosforo, potassio, bomba_dagua 
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores 
                ORDER BY data_hora_leitura DESC
            """)
            colunas = [desc[0] for desc in cursor.description]
            for row in cursor:
                registro = dict(zip(colunas, row))
                # Converte timestamps para string para serialização JSON
                if registro['data_hora_leitura']:
                    registro['data_hora_leitura'] = registro['data_hora_leitura'].isoformat()
                if registro['criacaots']:
                    registro['criacaots'] = registro['criacaots'].isoformat()
                # Boolean já é serializado corretamente pelo JSON
                registros.append(registro)
        except Exception as error:
            print(f"❌ Erro ao listar dados do PostgreSQL: {error}")
        finally:
            cursor.close()
            conn.close()
    return registros

# --- ROTA PARA O PLOTTER ---
@app.route('/plotter')
def plotter():
    """Serve a página HTML do plotter."""
    return Response(PLOTTER_HTML, mimetype='text/html')

@app.route('/get_data', methods=['GET'])
def get_all_data():
    """Retorna todos os dados em formato JSON."""
    dados = listar_dados()
    return jsonify({
        "schema": DatabaseConfig.SCHEMA,
        "host": DatabaseConfig.HOST,
        "database": DatabaseConfig.DATABASE,
        "total_registros": len(dados),
        "dados": dados
    })

def processar_meteorologia_background(umidade, temperatura, ph, fosforo, potassio, bomba_dagua, timestamp):
    """
    Processa dados meteorológicos em background thread.
    Não bloqueia a resposta para o ESP32.
    """
    try:
        print("🌤️ BACKGROUND: Iniciando processamento meteorológico...")
        
        # Pequeno delay para garantir que dados básicos foram salvos
        time.sleep(0.1)
        
        # Usa timestamp do ESP32 se fornecido
        if timestamp:
            if isinstance(timestamp, str):
                data_hora = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            else:
                data_hora = timestamp
        else:
            data_hora = datetime.now()
        
        # Organiza dados dos sensores
        dados_sensores = {
            'umidade': umidade,
            'temperatura': temperatura,
            'ph': ph,
            'fosforo': fosforo,
            'potassio': potassio,
            'bomba_dagua': bomba_dagua
        }
        
        # Coleta dados meteorológicos
        dados_meteo = coletar_dados_meteorologicos()
        
        # Conecta ao banco para salvar dados meteorológicos e integrados
        conn, cursor = conectar_postgres()
        if conn and cursor:
            try:
                # Salva dados meteorológicos
                cursor.execute(f"""
                    INSERT INTO {DatabaseConfig.SCHEMA}.dados_meteorologicos 
                    (data_hora_coleta, temperatura_externa, umidade_ar, pressao_atmosferica, 
                     velocidade_vento, direcao_vento, condicao_clima, probabilidade_chuva, 
                     quantidade_chuva, indice_uv, visibilidade, cidade, fonte_dados)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data_hora,
                    dados_meteo['temperatura_externa'],
                    dados_meteo['umidade_ar'],
                    dados_meteo['pressao_atmosferica'],
                    dados_meteo['velocidade_vento'],
                    dados_meteo['direcao_vento'],
                    dados_meteo['condicao_clima'],
                    dados_meteo['probabilidade_chuva'],
                    dados_meteo['quantidade_chuva'],
                    dados_meteo['indice_uv'],
                    dados_meteo['visibilidade'],
                    dados_meteo['cidade'],
                    dados_meteo['fonte_dados']
                ))
                
                # Calcula fatores derivados
                diferenca_temp = dados_meteo['temperatura_externa'] - dados_sensores['temperatura']
                deficit_umidade = dados_meteo['umidade_ar'] - dados_sensores['umidade']
                fator_evapo = (
                    (dados_meteo['temperatura_externa'] * 0.4) +
                    (dados_meteo['velocidade_vento'] * 0.3) +
                    ((100 - dados_meteo['umidade_ar']) * 0.3)
                ) / 10
                
                # Salva dados integrados
                cursor.execute(f"""
                    INSERT INTO {DatabaseConfig.SCHEMA}.leituras_integradas 
                    (data_hora_leitura, umidade_solo, temperatura_solo, ph_solo, fosforo, potassio, bomba_dagua,
                     temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento, condicao_clima,
                     probabilidade_chuva, quantidade_chuva, diferenca_temperatura, deficit_umidade, fator_evapotranspiracao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data_hora,
                    dados_sensores['umidade'],
                    dados_sensores['temperatura'],
                    dados_sensores['ph'],
                    dados_sensores['fosforo'],
                    dados_sensores['potassio'],
                    dados_sensores['bomba_dagua'],
                    dados_meteo['temperatura_externa'],
                    dados_meteo['umidade_ar'],
                    dados_meteo['pressao_atmosferica'],
                    dados_meteo['velocidade_vento'],
                    dados_meteo['condicao_clima'],
                    dados_meteo['probabilidade_chuva'],
                    dados_meteo['quantidade_chuva'],
                    round(diferenca_temp, 2),
                    round(deficit_umidade, 2),
                    round(fator_evapo, 2)
                ))
                
                conn.commit()
                print(f"✅ BACKGROUND: Dados meteorológicos e integrados salvos! ({dados_meteo['condicao_clima']})")
                
            except Exception as e:
                print(f"❌ BACKGROUND: Erro ao salvar dados meteorológicos: {e}")
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
        else:
            print("❌ BACKGROUND: Erro de conexão com banco")
            
    except Exception as e:
        print(f"❌ BACKGROUND: Erro geral no processamento: {e}")

@app.route('/data', methods=['GET'])
def receive_data():
    """Recebe dados do ESP32 via GET parameters com RESPOSTA ULTRA-RÁPIDA."""
    if request.method == 'GET':
        timestamp = request.args.get('timestamp')    # Timestamp do ESP32
        umidade = request.args.get('umidade')
        temperatura = request.args.get('temperatura')
        ph = request.args.get('ph')
        fosforo = request.args.get('fosforo')
        potassio = request.args.get('potassio')
        rele = request.args.get('rele')
        bomba_dagua = request.args.get('bomba_dagua')
        
        # Compatibilidade: aceita tanto 'rele' quanto 'bomba_dagua'
        bomba_param = rele if rele is not None else bomba_dagua

        # LOG MÍNIMO
        print(f"⚡ ESP32: {umidade}%/{temperatura}°C/pH{ph}")

        if umidade and temperatura and ph and fosforo and potassio and bomba_param:
            # Converte para tipos corretos (minimal processing)
            fosforo_bool = converter_para_boolean(fosforo)
            potassio_bool = converter_para_boolean(potassio)
            bomba_bool = converter_para_boolean(bomba_param)
            
            # RESPOSTA ULTRA-RÁPIDA: Pool de conexões
            sucesso_basico = inserir_dados_ultra_rapido(float(umidade), float(temperatura), float(ph), 
                                                       fosforo_bool, potassio_bool, bomba_bool, timestamp)
            
            if sucesso_basico:
                # INICIA PROCESSAMENTO EM BACKGROUND (NÃO BLOQUEIA RESPOSTA)
                thread_meteorologia = threading.Thread(
                    target=processar_meteorologia_background,
                    args=(float(umidade), float(temperatura), float(ph), 
                          fosforo_bool, potassio_bool, bomba_bool, timestamp),
                    daemon=True
                )
                thread_meteorologia.start()
                
                # RESPOSTA MÍNIMA E RÁPIDA
                return "OK", 200
            else:
                return "ERROR", 500
        else:
            return "MISSING_PARAMS", 400

@app.route('/', methods=['GET'])
def home():
    """Página inicial com informações da API."""
    return f'''
    <h1>🌱 Farm Tech Solutions - API PostgreSQL</h1>
    <h2>📡 Endpoints Disponíveis:</h2>
    <ul>
        <li><strong>GET /data</strong> - Recebe dados do ESP32</li>
        <li><strong>GET /get_data</strong> - Lista todos os dados armazenados</li>
        <li><strong>GET /status</strong> - Status do sistema</li>
        <li><strong>GET /stats</strong> - Estatísticas dos dados</li>
    </ul>
    <h2>📊 Configuração:</h2>
    <p>✅ Servidor rodando</p>
    <p>💾 Banco: PostgreSQL</p>
    <p>🖥️ Host: <strong>{DatabaseConfig.HOST}</strong></p>
    <p>🏗️ Schema: <strong>{DatabaseConfig.SCHEMA}</strong></p>
    <p>📁 Database: <strong>{DatabaseConfig.DATABASE}</strong></p>
    '''

@app.route('/status', methods=['GET'])
def status():
    """Retorna status do sistema."""
    dados = listar_dados()
    
    # Testa conexão
    conn, cursor = conectar_postgres()
    conexao_ok = conn is not None
    if conn:
        cursor.close()
        conn.close()
    
    return jsonify({
        "status": "online",
        "banco": "PostgreSQL",
        "host": DatabaseConfig.HOST,
        "database": DatabaseConfig.DATABASE,
        "schema": DatabaseConfig.SCHEMA,
        "conexao_ok": conexao_ok,
        "total_registros": len(dados),
        "ultimo_registro": dados[0] if dados else None
    })

@app.route('/stats', methods=['GET'])
def get_statistics():
    """Retorna estatísticas dos dados incluindo dados integrados."""
    conn, cursor = conectar_postgres()
    stats = {}
    
    if conn and cursor:
        try:
            # Estatísticas da tabela básica
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
            result = cursor.fetchone()
            
            # Estatísticas da tabela meteorológica
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_meteo,
                    AVG(temperatura_externa) as temp_ext_media,
                    AVG(umidade_ar) as umidade_ar_media,
                    AVG(probabilidade_chuva) as prob_chuva_media
                FROM {DatabaseConfig.SCHEMA}.dados_meteorologicos
            """)
            meteo_result = cursor.fetchone()
            
            # Estatísticas da tabela integrada
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_integrado,
                    AVG(fator_evapotranspiracao) as evapo_media,
                    COUNT(CASE WHEN probabilidade_chuva > 70 THEN 1 END) as previsoes_chuva
                FROM {DatabaseConfig.SCHEMA}.leituras_integradas
            """)
            integrado_result = cursor.fetchone()
            
            if result and result[0] > 0:
                stats = {
                    "sensores": {
                        "total_registros": result[0],
                        "umidade": {
                            "media": round(float(result[1]), 1) if result[1] else 0,
                            "minima": round(float(result[2]), 1) if result[2] else 0,
                            "maxima": round(float(result[3]), 1) if result[3] else 0
                        },
                        "temperatura": {
                            "media": round(float(result[4]), 1) if result[4] else 0,
                            "minima": round(float(result[5]), 1) if result[5] else 0,
                            "maxima": round(float(result[6]), 1) if result[6] else 0
                        },
                        "ph": {
                            "medio": round(float(result[7]), 1) if result[7] else 0,
                            "minimo": round(float(result[8]), 1) if result[8] else 0,
                            "maximo": round(float(result[9]), 1) if result[9] else 0
                        }
                    },
                    "meteorologia": {
                        "total_registros": meteo_result[0] if meteo_result else 0,
                        "temperatura_externa_media": round(float(meteo_result[1]), 1) if meteo_result and meteo_result[1] else 0,
                        "umidade_ar_media": round(float(meteo_result[2]), 1) if meteo_result and meteo_result[2] else 0,
                        "probabilidade_chuva_media": round(float(meteo_result[3]), 1) if meteo_result and meteo_result[3] else 0
                    },
                    "integrado": {
                        "total_registros": integrado_result[0] if integrado_result else 0,
                        "evapotranspiracao_media": round(float(integrado_result[1]), 1) if integrado_result and integrado_result[1] else 0,
                        "previsoes_chuva": integrado_result[2] if integrado_result else 0
                    },
                    "status_integracao": "✅ Ativo" if (meteo_result and meteo_result[0] > 0) else "⚠️ Sem dados meteorológicos"
                }
            else:
                stats = {"erro": "Nenhum dado disponível"}
                
        except Exception as e:
            stats = {"erro": f"Erro ao calcular estatísticas: {e}"}
        finally:
            cursor.close()
            conn.close()
    else:
        stats = {"erro": "Erro de conexão com banco"}
    
    return jsonify(stats)

@app.route('/test_integration', methods=['GET'])
def test_integration():
    """
    Rota para testar o sistema de integração automática.
    Simula uma leitura completa de sensores + meteorologia.
    """
    print("\n🧪 TESTE DE INTEGRAÇÃO AUTOMÁTICA:")
    
    # Dados simulados do ESP32
    dados_teste = {
        'umidade': 65.5,
        'temperatura': 24.2,
        'ph': 6.8,
        'fosforo': True,
        'potassio': False,
        'bomba_dagua': False
    }
    
    print("🔬 Simulando leitura do ESP32:")
    for key, value in dados_teste.items():
        emoji = "🌡️" if key == "temperatura" else "💧" if key == "umidade" else "⚗️" if key == "ph" else "🧪" if "fosforo" in key or "potassio" in key else "🚰"
        print(f"   {emoji} {key}: {value}")
    
    # Executa o processo integrado
    sucesso = inserir_dados_completo(
        dados_teste['umidade'],
        dados_teste['temperatura'], 
        dados_teste['ph'],
        dados_teste['fosforo'],
        dados_teste['potassio'],
        dados_teste['bomba_dagua']
    )
    
    if sucesso:
        return jsonify({
            "status": "sucesso",
            "message": "✅ Teste de integração concluído com sucesso!",
            "dados_testados": dados_teste,
            "processos_executados": [
                "1. Salvamento dados sensores",
                "2. Coleta dados meteorológicos",
                "3. Salvamento dados meteorológicos", 
                "4. Cálculo fatores ML",
                "5. Criação entrada integrada"
            ],
            "tabelas_afetadas": ["leituras_sensores", "dados_meteorologicos", "leituras_integradas"]
        })
    else:
        return jsonify({
            "status": "erro",
            "message": "❌ Falha no teste de integração",
            "dados_testados": dados_teste
        }), 500

@app.route('/integrated_data', methods=['GET'])
def get_integrated_data():
    """Retorna dados da tabela integrada para análise ML."""
    conn, cursor = conectar_postgres()
    registros = []
    
    if conn and cursor:
        try:
            cursor.execute(f"""
                SELECT * FROM {DatabaseConfig.SCHEMA}.view_ml_completa 
                ORDER BY data_hora_leitura DESC
                LIMIT 50
            """)
            colunas = [desc[0] for desc in cursor.description]
            for row in cursor:
                registro = dict(zip(colunas, row))
                # Converte timestamps para string
                if registro.get('data_hora_leitura'):
                    registro['data_hora_leitura'] = registro['data_hora_leitura'].isoformat()
                registros.append(registro)
                
        except Exception as error:
            print(f"❌ Erro ao listar dados integrados: {error}")
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({
        "schema": DatabaseConfig.SCHEMA,
        "view": "view_ml_completa",
        "total_features": len(registros[0]) if registros else 0,
        "total_registros": len(registros),
        "dados": registros
    })

# === NOVAS FUNÇÕES PARA DADOS METEOROLÓGICOS AUTOMÁTICOS ===
def coletar_dados_meteorologicos():
    """
    Coleta dados meteorológicos usando a MESMA LÓGICA do dashboard.
    Garante consistência entre dashboard e sistema de integração.
    """
    try:
        # USA A MESMA LÓGICA DO DASHBOARD (get_clima_atual)
        # Para manter consistência entre os sistemas
        
        import random
        from datetime import datetime
        
        # Simula condições climáticas variáveis (MESMA LÓGICA DO DASHBOARD)
        hora_atual = datetime.now().hour
        
        # Temperatura varia conforme o horário (SINCRONIZADO COM DASHBOARD)
        if 6 <= hora_atual <= 12:  # Manhã
            temp_base = 24 + random.uniform(-2, 3)
        elif 12 <= hora_atual <= 18:  # Tarde
            temp_base = 29 + random.uniform(-3, 4)
        elif 18 <= hora_atual <= 22:  # Noite
            temp_base = 26 + random.uniform(-2, 2)
        else:  # Madrugada
            temp_base = 22 + random.uniform(-1, 2)
        
        # Umidade do ar inversamente relacionada à temperatura (MESMA LÓGICA)
        umidade_ar = max(45, min(95, 85 - (temp_base - 22) * 2 + random.uniform(-5, 5)))
        
        # Pressão atmosférica com variação realista (MESMA LÓGICA)
        pressao = 1013.25 + random.uniform(-15, 15)
        
        # Vento com padrões diurnos (MESMA LÓGICA)
        if 10 <= hora_atual <= 16:  # Ventos mais fortes durante o dia
            vento = random.uniform(8, 18)
        else:  # Ventos mais calmos à noite
            vento = random.uniform(3, 12)
        
        # Probabilidade de chuva baseada em umidade e pressão (MESMA LÓGICA)
        if umidade_ar > 80 and pressao < 1010:
            prob_chuva = random.uniform(60, 95)
        elif umidade_ar > 70:
            prob_chuva = random.uniform(20, 60)
        else:
            prob_chuva = random.uniform(0, 20)
        
        # Quantidade de chuva se probabilidade for alta (MESMA LÓGICA)
        if prob_chuva > 70:
            chuva = random.uniform(0.5, 8.0)
        elif prob_chuva > 40:
            chuva = random.uniform(0.0, 2.0)
        else:
            chuva = 0.0
        
        # Condições climáticas baseadas em chuva e temperatura (MESMA LÓGICA)
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
        
        # Direção do vento (MESMA LÓGICA)
        direcoes = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        direcao_vento = random.choice(direcoes)
        
        # Índice UV baseado na hora e condições (MESMA LÓGICA)
        if 10 <= hora_atual <= 16 and "Ensolarado" in condicao:
            indice_uv = random.uniform(6, 11)
        elif 8 <= hora_atual <= 18:
            indice_uv = random.uniform(2, 8)
        else:
            indice_uv = random.uniform(0, 2)
        
        # Visibilidade baseada em chuva e umidade (MESMA LÓGICA)
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
            'cidade': 'Camopi (Sistema Integrado)',
            'fonte_dados': 'Sistema Unificado Dashboard+API'
        }
        
        print(f"🌤️ Dados meteorológicos coletados (SISTEMA INTEGRADO): {dados_meteorologicos['condicao_clima']}, "
              f"{dados_meteorologicos['temperatura_externa']}°C, "
              f"Chuva: {dados_meteorologicos['probabilidade_chuva']}%")
        
        return dados_meteorologicos
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados meteorológicos: {e}")
        # Retorna dados padrão em caso de erro
        return {
            'temperatura_externa': 25.0,
            'umidade_ar': 70.0,
            'pressao_atmosferica': 1013.25,
            'velocidade_vento': 5.0,
            'direcao_vento': 'E',
            'condicao_clima': 'Não disponível',
            'probabilidade_chuva': 30.0,
            'quantidade_chuva': 0.0,
            'indice_uv': 5.0,
            'visibilidade': 10.0,
            'cidade': 'Camopi',
            'fonte_dados': 'Dados Padrão'
        }

def salvar_dados_meteorologicos(dados_meteo, timestamp=None):
    """
    Salva dados meteorológicos na tabela dados_meteorologicos.
    """
    conn, cursor = conectar_postgres()
    if conn and cursor:
        try:
            data_coleta = timestamp if timestamp else datetime.now(BRASIL_TZ)
            
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.dados_meteorologicos 
                (data_hora_coleta, temperatura_externa, umidade_ar, pressao_atmosferica, 
                 velocidade_vento, direcao_vento, condicao_clima, probabilidade_chuva, 
                 quantidade_chuva, indice_uv, visibilidade, cidade, fonte_dados)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data_coleta,
                dados_meteo['temperatura_externa'],
                dados_meteo['umidade_ar'],
                dados_meteo['pressao_atmosferica'],
                dados_meteo['velocidade_vento'],
                dados_meteo['direcao_vento'],
                dados_meteo['condicao_clima'],
                dados_meteo['probabilidade_chuva'],
                dados_meteo['quantidade_chuva'],
                dados_meteo['indice_uv'],
                dados_meteo['visibilidade'],
                dados_meteo['cidade'],
                dados_meteo['fonte_dados']
            ))
            
            conn.commit()
            print("✅ Dados meteorológicos salvos no banco!")
            return True
            
        except Exception as error:
            print(f"❌ Erro ao salvar dados meteorológicos: {error}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def calcular_fatores_avancados(dados_sensores, dados_meteo):
    """
    Calcula fatores derivados para análise ML avançada.
    """
    try:
        # Diferença de temperatura (externa - solo)
        diferenca_temp = dados_meteo['temperatura_externa'] - dados_sensores['temperatura']
        
        # Déficit de umidade (ar - solo)
        deficit_umidade = dados_meteo['umidade_ar'] - dados_sensores['umidade']
        
        # Fator de evapotranspiração simplificado
        # Baseado em temperatura, vento e umidade
        fator_evapo = (
            (dados_meteo['temperatura_externa'] * 0.4) +
            (dados_meteo['velocidade_vento'] * 0.3) +
            ((100 - dados_meteo['umidade_ar']) * 0.3)
        ) / 10
        
        return {
            'diferenca_temperatura': round(diferenca_temp, 2),
            'deficit_umidade': round(deficit_umidade, 2),
            'fator_evapotranspiracao': round(fator_evapo, 2)
        }
        
    except Exception as e:
        print(f"⚠️ Erro ao calcular fatores: {e}")
        return {
            'diferenca_temperatura': 0.0,
            'deficit_umidade': 0.0,
            'fator_evapotranspiracao': 5.0
        }

def criar_leitura_integrada(dados_sensores, dados_meteo, fatores, timestamp=None):
    """
    Cria uma entrada na tabela leituras_integradas combinando todos os dados.
    """
    conn, cursor = conectar_postgres()
    if conn and cursor:
        try:
            data_leitura = timestamp if timestamp else datetime.now(BRASIL_TZ)
            
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.leituras_integradas 
                (data_hora_leitura, umidade_solo, temperatura_solo, ph_solo, fosforo, potassio, bomba_dagua,
                 temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento, condicao_clima,
                 probabilidade_chuva, quantidade_chuva, diferenca_temperatura, deficit_umidade, fator_evapotranspiracao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data_leitura,
                dados_sensores['umidade'],
                dados_sensores['temperatura'],
                dados_sensores['ph'],
                dados_sensores['fosforo'],
                dados_sensores['potassio'],
                dados_sensores['bomba_dagua'],
                dados_meteo['temperatura_externa'],
                dados_meteo['umidade_ar'],
                dados_meteo['pressao_atmosferica'],
                dados_meteo['velocidade_vento'],
                dados_meteo['condicao_clima'],
                dados_meteo['probabilidade_chuva'],
                dados_meteo['quantidade_chuva'],
                fatores['diferenca_temperatura'],
                fatores['deficit_umidade'],
                fatores['fator_evapotranspiracao']
            ))
            
            conn.commit()
            print("✅ Leitura integrada (sensores + meteorologia) salva!")
            return True
            
        except Exception as error:
            print(f"❌ Erro ao salvar leitura integrada: {error}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def inserir_dados_completo(umidade, temperatura, ph, fosforo, potassio, bomba_dagua, timestamp_esp32=None):
    """
    Versão OTIMIZADA que salva dados de sensores + meteorologia rapidamente.
    
    FLUXO OTIMIZADO:
    1. Uma única conexão ao banco
    2. Processamento paralelo de dados
    3. Transação única para garantir consistência
    4. Resposta rápida para o ESP32
    """
    # Usa timestamp do ESP32 se fornecido, senão usa timestamp do servidor
    if timestamp_esp32:
        if isinstance(timestamp_esp32, str):
            try:
                data_hora_leitura = datetime.strptime(timestamp_esp32, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                try:
                    data_hora_leitura = datetime.strptime(timestamp_esp32, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print(f"⚠️ Formato de timestamp inválido: {timestamp_esp32}")
                    data_hora_leitura = datetime.now()
        else:
            data_hora_leitura = timestamp_esp32
    else:
        data_hora_leitura = datetime.now()
        
    # Organiza dados dos sensores
    dados_sensores = {
        'umidade': umidade,
        'temperatura': temperatura,
        'ph': ph,
        'fosforo': fosforo,
        'potassio': potassio,
        'bomba_dagua': bomba_dagua
    }
    
    print(f"🚀 PROCESSO OTIMIZADO: Salvando dados em transação única...")
    
    # OTIMIZAÇÃO: Uma única conexão para tudo
    conn, cursor = conectar_postgres()
    if not conn or not cursor:
        print("❌ Erro de conexão com banco!")
        return False
    
    try:
        # Inicia transação
        cursor.execute("BEGIN")
        
        # 1. Salva dados dos sensores (RÁPIDO)
        cursor.execute(f"""
            INSERT INTO {DatabaseConfig.SCHEMA}.leituras_sensores 
            (data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua
        ))
        
        # 2. Coleta dados meteorológicos (RÁPIDO - sem I/O)
        dados_meteo = coletar_dados_meteorologicos()
        
        # 3. Salva dados meteorológicos (RÁPIDO)
        cursor.execute(f"""
            INSERT INTO {DatabaseConfig.SCHEMA}.dados_meteorologicos 
            (data_hora_coleta, temperatura_externa, umidade_ar, pressao_atmosferica, 
             velocidade_vento, direcao_vento, condicao_clima, probabilidade_chuva, 
             quantidade_chuva, indice_uv, visibilidade, cidade, fonte_dados)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data_hora_leitura,
            dados_meteo['temperatura_externa'],
            dados_meteo['umidade_ar'],
            dados_meteo['pressao_atmosferica'],
            dados_meteo['velocidade_vento'],
            dados_meteo['direcao_vento'],
            dados_meteo['condicao_clima'],
            dados_meteo['probabilidade_chuva'],
            dados_meteo['quantidade_chuva'],
            dados_meteo['indice_uv'],
            dados_meteo['visibilidade'],
            dados_meteo['cidade'],
            dados_meteo['fonte_dados']
        ))
        
        # 4. Calcula fatores derivados (RÁPIDO - apenas matemática)
        diferenca_temp = dados_meteo['temperatura_externa'] - dados_sensores['temperatura']
        deficit_umidade = dados_meteo['umidade_ar'] - dados_sensores['umidade']
        fator_evapo = (
            (dados_meteo['temperatura_externa'] * 0.4) +
            (dados_meteo['velocidade_vento'] * 0.3) +
            ((100 - dados_meteo['umidade_ar']) * 0.3)
        ) / 10
        
        # 5. Cria entrada integrada (RÁPIDO)
        cursor.execute(f"""
            INSERT INTO {DatabaseConfig.SCHEMA}.leituras_integradas 
            (data_hora_leitura, umidade_solo, temperatura_solo, ph_solo, fosforo, potassio, bomba_dagua,
             temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento, condicao_clima,
             probabilidade_chuva, quantidade_chuva, diferenca_temperatura, deficit_umidade, fator_evapotranspiracao)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data_hora_leitura,
            dados_sensores['umidade'],
            dados_sensores['temperatura'],
            dados_sensores['ph'],
            dados_sensores['fosforo'],
            dados_sensores['potassio'],
            dados_sensores['bomba_dagua'],
            dados_meteo['temperatura_externa'],
            dados_meteo['umidade_ar'],
            dados_meteo['pressao_atmosferica'],
            dados_meteo['velocidade_vento'],
            dados_meteo['condicao_clima'],
            dados_meteo['probabilidade_chuva'],
            dados_meteo['quantidade_chuva'],
            round(diferenca_temp, 2),
            round(deficit_umidade, 2),
            round(fator_evapo, 2)
        ))
        
        # Confirma transação
        conn.commit()
        
        print(f"✅ OTIMIZADO: Dados salvos em 3 tabelas simultaneamente!")
        print(f"🌤️ Meteorologia: {dados_meteo['condicao_clima']}, {dados_meteo['temperatura_externa']}°C")
        
        return True
        
    except Exception as error:
        print(f"❌ Erro na transação otimizada: {error}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def inserir_dados_ultra_rapido(umidade, temperatura, ph, fosforo, potassio, bomba_dagua, timestamp_esp32=None):
    """Versão ULTRA-RÁPIDA usando pool de conexões."""
    conn, cursor = obter_conexao_pool()
    if conn and cursor:
        # Timestamp processing (minimal)
        if timestamp_esp32 and isinstance(timestamp_esp32, str):
            try:
                data_hora_leitura = datetime.strptime(timestamp_esp32, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                data_hora_leitura = datetime.now()
        else:
            data_hora_leitura = datetime.now()
            
        try:
            # Ultra-fast insert usando pool
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.leituras_sensores 
                (data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (data_hora_leitura, umidade, temperatura, ph, fosforo, potassio, bomba_dagua))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            cursor.close()
            devolver_conexao_pool(conn)
    return False

if __name__ == '__main__':
    print("🚀 Iniciando Farm Tech Solutions - Servidor PostgreSQL")
    print(f"📊 Usando configuração centralizada")
    print(f"💾 Database: {DatabaseConfig.DATABASE}")
    print(f"🏗️ Schema: {DatabaseConfig.SCHEMA}")
    print(f"🖥️ Host: {DatabaseConfig.HOST}")
    
    # Inicializa pool de conexões para performance
    if inicializar_pool_conexoes():
        print("⚡ Sistema otimizado para resposta ultra-rápida ao ESP32!")
    else:
        print("⚠️ Pool não inicializado, usando conexões individuais")
    
    print("🌐 Servidor disponível em:")
    print("   - http://127.0.0.1:8000")
    print("   - http://192.168.2.126:8000")
    print("\n📡 Aguardando dados do ESP32...")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
