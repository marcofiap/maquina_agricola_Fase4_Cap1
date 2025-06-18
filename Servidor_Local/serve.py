from flask import Flask, request, jsonify
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path para importar o config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.database_config import DatabaseConfig, conectar_postgres, criar_schema_e_tabela

app = Flask(__name__)

# Inicializa schema e tabela
criar_schema_e_tabela()

def inserir_dados(umidade, temperatura, ph, fosforo, potassio, bomba_dagua):
    """Insere uma nova leitura de dados na tabela 'leituras_sensores' do PostgreSQL."""
    conn, cursor = conectar_postgres()
    if conn and cursor:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.leituras_sensores (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (timestamp_str, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
            )
            conn.commit()
            print(f"✅ Dados inseridos no PostgreSQL ({DatabaseConfig.SCHEMA}) em {timestamp_str}!")
            print(f"📊 Umidade: {umidade}% | Temperatura: {temperatura}°C | pH: {ph} | Bomba: {bomba_dagua}")
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
            cursor.execute(f"SELECT timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua FROM {DatabaseConfig.SCHEMA}.leituras_sensores ORDER BY timestamp DESC")
            colunas = [desc[0] for desc in cursor.description]
            for row in cursor:
                registros.append(dict(zip(colunas, row)))
        except Exception as error:
            print(f"❌ Erro ao listar dados do PostgreSQL: {error}")
        finally:
            cursor.close()
            conn.close()
    return registros

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

@app.route('/data', methods=['GET'])
def receive_data():
    """Recebe dados do ESP32 via GET parameters."""
    if request.method == 'GET':
        umidade = request.args.get('umidade')
        temperatura = request.args.get('temperatura')
        ph = request.args.get('ph')
        fosforo = request.args.get('fosforo')
        potassio = request.args.get('potassio')
        rele = request.args.get('rele')

        print("\n🔄 DADOS RECEBIDOS DO ESP32:")
        print(f"🌡️  Temperatura: {temperatura}°C")
        print(f"💧 Umidade: {umidade}%")
        print(f"⚗️  pH: {ph}")
        print(f"🧪 Fósforo: {fosforo} | Potássio: {potassio}")
        print(f"🚰 Bomba: {rele}")

        if umidade and temperatura and ph and fosforo and potassio and rele:
            sucesso = inserir_dados(float(umidade), float(temperatura), float(ph), fosforo, potassio, rele)
            if sucesso:
                return f"✅ Dados recebidos e armazenados no PostgreSQL ({DatabaseConfig.SCHEMA}) com sucesso!", 200
            else:
                return "❌ Erro ao armazenar dados no PostgreSQL!", 500
        else:
            return "❌ Erro: Parâmetros ausentes na requisição!", 400

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
    """Retorna estatísticas dos dados."""
    conn, cursor = conectar_postgres()
    stats = {}
    
    if conn and cursor:
        try:
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
            
            if result and result[0] > 0:
                stats = {
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

if __name__ == '__main__':
    print("🚀 Iniciando Farm Tech Solutions - Servidor PostgreSQL")
    print(f"📊 Usando configuração centralizada")
    print(f"💾 Database: {DatabaseConfig.DATABASE}")
    print(f"🏗️ Schema: {DatabaseConfig.SCHEMA}")
    print(f"🖥️ Host: {DatabaseConfig.HOST}")
    print("🌐 Servidor disponível em:")
    print("   - http://127.0.0.1:8000")
    print("   - http://192.168.2.126:8000")
    print("\n📡 Aguardando dados do ESP32...")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
