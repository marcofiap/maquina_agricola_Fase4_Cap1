from flask import Flask, request, jsonify
import oracledb
from datetime import datetime

app = Flask(__name__)

# *** Configurações do Banco de Dados Oracle ***
DB_USER = "system"  # Substitua pelo seu nome de usuário Oracle
DB_PASSWORD = "system"  # Substitua pela sua senha Oracle
DB_DSN = "localhost:1521/xe"  # Substitua pela sua string de conexão DSN

def conectar_db():
    """Conecta ao banco de dados Oracle."""
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()
        return conn, cursor
    except oracledb.Error as error:
        print(f"Erro ao conectar ao Oracle: {error}")
        return None, None

def criar_tabela():
    """Cria a tabela 'leituras_sensores' no Oracle se ela não existir."""
    conn, cursor = conectar_db()
    if conn and cursor:
        try:
            cursor.execute("""
                CREATE TABLE leituras_sensores (
                    timestamp VARCHAR2(255) PRIMARY KEY,
                    umidade NUMBER,
                    temperatura NUMBER,
                    ph NUMBER,
                    fosforo VARCHAR2(10),
                    potassio VARCHAR2(10),
                    bomba_dagua VARCHAR2(10)
                )
            """)
            conn.commit()
            print("Tabela 'leituras_sensores' criada (se não existia).")
        except oracledb.Error as error:
            if error.args[0].code == 955:
                print("A tabela 'leituras_sensores' já existe.")
            else:
                print(f"Erro ao criar a tabela: {error}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()

criar_tabela()

def inserir_dados(umidade, temperatura, ph, fosforo, potassio, bomba_dagua):
    """Insere uma nova leitura de dados na tabela 'leituras_sensores' do Oracle."""
    conn, cursor = conectar_db()
    if conn and cursor:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute("""
                INSERT INTO leituras_sensores (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                VALUES (:timestamp, :umidade, :temperatura, :ph, :fosforo, :potassio, :bomba_dagua)
            """,
            timestamp=timestamp_str, umidade=umidade, temperatura=temperatura, ph=ph, fosforo=fosforo, potassio=potassio, bomba_dagua=bomba_dagua
            )
            conn.commit()
            print(f"Dados inseridos no Oracle em {timestamp_str}!")
            return True
        except oracledb.Error as error:
            print(f"Erro ao inserir dados no Oracle: {error}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    else:
        print("Não foi possível conectar ao banco de dados.")
        return False

def listar_dados():
    """Lista todas as leituras da tabela 'leituras_sensores' do Oracle."""
    conn, cursor = conectar_db()
    registros = []
    if conn and cursor:
        try:
            cursor.execute("SELECT timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua FROM leituras_sensores ORDER BY timestamp DESC")
            colunas = [desc[0] for desc in cursor.description]
            for row in cursor:
                registros.append(dict(zip(colunas, row)))
        except oracledb.Error as error:
            print(f"Erro ao listar dados do Oracle: {error}")
        finally:
            cursor.close()
            conn.close()
    return registros

@app.route('/get_data', methods=['GET'])
def get_all_data():
    dados = listar_dados()
    return jsonify(dados)

@app.route('/data', methods=['GET'])
def receive_data():
    if request.method == 'GET':
        umidade = request.args.get('umidade')
        temperatura = request.args.get('temperatura')
        ph = request.args.get('ph')
        fosforo = request.args.get('fosforo')
        potassio = request.args.get('potassio')
        rele = request.args.get('rele')

        print("DADOS RECEBIDOS:")
        print(f"Fósforo: {fosforo} | Potássio: {potassio}")

        if umidade and temperatura and ph and fosforo and potassio and rele:
            inserir_dados(float(umidade), float(temperatura), float(ph), fosforo, potassio, rele)
            return "Dados recebidos e armazenados no Oracle com sucesso!", 200
        else:
            return "Erro: Parâmetros ausentes na requisição!", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    print("Servidor Flask rodando na porta 8000...")