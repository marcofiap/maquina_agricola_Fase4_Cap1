"""
FarmTech Solutions - CRUD Application
Este script implementa um sistema CRUD simples para o banco de dados FarmTech Solutions
e integra com a simulação de um dispositivo ESP32 executando no Wokwi.

"""

import cx_Oracle
import datetime
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from threading import Thread
from config import DB_CONFIG, SERVER_CONFIG





# Variáveis globais para conexão e servidor
connection = None
server = None

# -------------------- CONEXÃO COM BANCO DE DADOS --------------------

def connect_to_db():
    """Estabelece conexão com o banco de dados Oracle usando configurações do config.py"""
    global connection
    try:
        connection = cx_Oracle.connect(
            DB_CONFIG["user"], 
            DB_CONFIG["password"], 
            DB_CONFIG["dsn"]
        )
        print("Conectado ao banco de dados Oracle com sucesso")
        return connection
    except cx_Oracle.Error as error:
        print(f"Erro ao conectar ao banco de dados Oracle: {error}")
        return None

# -------------------- RECEPTOR DE DADOS DO ESP32 --------------------

class ESP32Handler(BaseHTTPRequestHandler):
    """Manipulador de requisições HTTP para dados do ESP32"""
    
    def do_GET(self):
        """Trata requisições GET do ESP32"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Dados recebidos com sucesso!")
        
        # Analisa parâmetros da consulta
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        # Extrai dados
        try:
            umidade = float(params.get('umidade', ['0'])[0])
            temperatura = float(params.get('temperatura', ['0'])[0])
            ph = int(params.get('ph', ['0'])[0])
            fosforo = params.get('fosforo', ['ausente'])[0]
            potassio = params.get('potassio', ['ausente'])[0]
            rele = params.get('rele', ['off'])[0]
            
            # Exibe dados recebidos
            print(f"\nDados recebidos do ESP32:")
            print(f"Umidade: {umidade}%, Temperatura: {temperatura}°C, pH: {ph}")
            print(f"Fósforo: {fosforo}, Potássio: {potassio}, Relé: {rele}")
            
            # Salva no banco de dados
            save_sensor_data(temperatura, umidade, ph, fosforo, potassio, rele)
            
        except Exception as e:
            print(f"Erro ao processar dados do ESP32: {e}")

def save_sensor_data(temperatura, umidade, ph, fosforo, potassio, rele):
    """Salva dados dos sensores no banco de dados"""
    if not connection:
        print("Sem conexão com o banco de dados")
        return
    
    try:
        cursor = connection.cursor()
        now = datetime.datetime.now()
        
        # Para simplicidade, assumimos que sensores com IDs 1-6 já existem no banco
        
        # Obtém o próximo ID de monitoramento
        cursor.execute("SELECT NVL(MAX(id_monitoramento), 0) + 1 FROM monitoramento")
        id_monitoramento = cursor.fetchone()[0]
        
        # Salva temperatura (sensor ID 1)
        cursor.execute(
            "INSERT INTO monitoramento (id_monitoramento, id_sensor, valor, data_hora_monitoramento) VALUES (:1, :2, :3, :4)",
            [id_monitoramento, 1, temperatura, now]
        )
        
        # Salva umidade (sensor ID 2)
        cursor.execute(
            "INSERT INTO monitoramento (id_monitoramento, id_sensor, valor, data_hora_monitoramento) VALUES (:1, :2, :3, :4)",
            [id_monitoramento + 1, 2, umidade, now]
        )
        
        # Salva pH (sensor ID 3)
        cursor.execute(
            "INSERT INTO monitoramento (id_monitoramento, id_sensor, valor, data_hora_monitoramento) VALUES (:1, :2, :3, :4)",
            [id_monitoramento + 2, 3, ph, now]
        )
        
        # Converte valores de string para numérico para armazenamento no banco
        fosforo_value = 1 if fosforo == 'presente' else 0
        potassio_value = 1 if potassio == 'presente' else 0
        rele_value = 1 if rele == 'on' else 0
        
        # Salva status do fósforo (sensor ID 4)
        cursor.execute(
            "INSERT INTO monitoramento (id_monitoramento, id_sensor, valor, data_hora_monitoramento) VALUES (:1, :2, :3, :4)",
            [id_monitoramento + 3, 4, fosforo_value, now]
        )
        
        # Salva status do potássio (sensor ID 5)
        cursor.execute(
            "INSERT INTO monitoramento (id_monitoramento, id_sensor, valor, data_hora_monitoramento) VALUES (:1, :2, :3, :4)",
            [id_monitoramento + 4, 5, potassio_value, now]
        )
        
        # Salva status do relé (sensor ID 6)
        cursor.execute(
            "INSERT INTO monitoramento (id_monitoramento, id_sensor, valor, data_hora_monitoramento) VALUES (:1, :2, :3, :4)",
            [id_monitoramento + 5, 6, rele_value, now]
        )
        
        connection.commit()
        print("Dados dos sensores salvos com sucesso no banco de dados")
        
    except cx_Oracle.Error as error:
        print(f"Erro ao salvar dados dos sensores: {error}")

# -------------------- INICIALIZAÇÃO DO SERVIDOR --------------------

def start_server():
    """Inicia servidor HTTP para receber dados do ESP32"""
    global server
    server_address = (SERVER_CONFIG["host"], SERVER_CONFIG["port"])
    try:
        server = HTTPServer(server_address, ESP32Handler)
        print(f'Iniciando servidor na porta {SERVER_CONFIG["port"]} para receber dados do ESP32...')
        server_thread = Thread(target=server.serve_forever)
        server_thread.daemon = True  # Thread será encerrada quando o programa principal encerrar
        server_thread.start()
        return True
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        return False

# -------------------- OPERAÇÕES CRUD: CULTURA --------------------

def create_cultura():
    """Cria um novo registro de cultura"""
    print("\n--- Cadastrar Nova Cultura ---")
    
    descricao = input("Descrição da cultura: ")
    ativo = input("Ativo (S/N): ").upper()
    
    if ativo not in ['S', 'N']:
        print("Valor inválido para campo ativo. Utilizando 'S' como padrão.")
        ativo = 'S'
    
    area = input("Área plantada (m²): ")
    if area:
        try:
            area = float(area)
        except ValueError:
            print("Valor inválido para área. Utilizando 0 como padrão.")
            area = 0
    else:
        area = 0
    
    try:
        cursor = connection.cursor()
        
        # Obtém próximo ID
        cursor.execute("SELECT NVL(MAX(id_cultura), 0) + 1 FROM cultura")
        id_cultura = cursor.fetchone()[0]
        
        cursor.execute(
            "INSERT INTO cultura (id_cultura, descricao_cultura, ativo, area_plantada) VALUES (:1, :2, :3, :4)",
            [id_cultura, descricao, ativo, area]
        )
        connection.commit()
        print(f"Cultura cadastrada com sucesso! ID: {id_cultura}")
    except cx_Oracle.Error as error:
        print(f"Erro ao cadastrar cultura: {error}")

def read_cultura():
    """Lê todos os registros de cultura"""
    print("\n--- Listar Culturas ---")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM cultura ORDER BY id_cultura")
        rows = cursor.fetchall()
        
        if not rows:
            print("Nenhuma cultura cadastrada.")
            return
        
        print(f"{'ID':<5} {'Descrição':<30} {'Ativo':<6} {'Área (m²)':<10}")
        print("-" * 55)
        
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<30} {row[2]:<6} {row[3]:<10}")
            
    except cx_Oracle.Error as error:
        print(f"Erro ao listar culturas: {error}")

def update_cultura():
    """Atualiza um registro de cultura"""
    print("\n--- Atualizar Cultura ---")
    
    id_cultura = input("ID da cultura que deseja atualizar: ")
    try:
        id_cultura = int(id_cultura)
    except ValueError:
        print("ID inválido. Operação cancelada.")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM cultura WHERE id_cultura = :1", [id_cultura])
        row = cursor.fetchone()
        
        if not row:
            print(f"Cultura com ID {id_cultura} não encontrada.")
            return
        
        print(f"Cultura atual: ID: {row[0]}, Descrição: {row[1]}, Ativo: {row[2]}, Área: {row[3]}")
        print("Deixe em branco para manter o valor atual.")
        
        descricao = input(f"Nova descrição [{row[1]}]: ")
        ativo = input(f"Novo status (S/N) [{row[2]}]: ").upper()
        area = input(f"Nova área plantada [{row[3]}]: ")
        
        # Usa valores atuais se nenhum novo valor for fornecido
        if not descricao:
            descricao = row[1]
        
        if not ativo:
            ativo = row[2]
        elif ativo not in ['S', 'N']:
            print("Valor inválido para campo ativo. Mantendo valor atual.")
            ativo = row[2]
        
        if not area:
            area = row[3]
        else:
            try:
                area = float(area)
            except ValueError:
                print("Valor inválido para área. Mantendo valor atual.")
                area = row[3]
        
        cursor.execute(
            "UPDATE cultura SET descricao_cultura = :1, ativo = :2, area_plantada = :3 WHERE id_cultura = :4",
            [descricao, ativo, area, id_cultura]
        )
        connection.commit()
        print(f"Cultura atualizada com sucesso!")
        
    except cx_Oracle.Error as error:
        print(f"Erro ao atualizar cultura: {error}")

def delete_cultura():
    """Exclui um registro de cultura"""
    print("\n--- Excluir Cultura ---")
    
    id_cultura = input("ID da cultura que deseja excluir: ")
    try:
        id_cultura = int(id_cultura)
    except ValueError:
        print("ID inválido. Operação cancelada.")
        return
    
    try:
        cursor = connection.cursor()
        
        # Verifica se a cultura existe
        cursor.execute("SELECT 1 FROM cultura WHERE id_cultura = :1", [id_cultura])
        if not cursor.fetchone():
            print(f"Cultura com ID {id_cultura} não encontrada.")
            return
        
        # Verifica se há sensores relacionados
        cursor.execute("SELECT 1 FROM sensor WHERE id_cultura = :1", [id_cultura])
        if cursor.fetchone():
            print(f"Não é possível excluir a cultura ID {id_cultura} porque existem sensores associados a ela.")
            return
        
        confirm = input(f"Tem certeza que deseja excluir a cultura ID {id_cultura}? (S/N): ").upper()
        if confirm != 'S':
            print("Operação cancelada.")
            return
        
        cursor.execute("DELETE FROM cultura WHERE id_cultura = :1", [id_cultura])
        connection.commit()
        print(f"Cultura excluída com sucesso!")
        
    except cx_Oracle.Error as error:
        print(f"Erro ao excluir cultura: {error}")

# -------------------- OPERAÇÕES CRUD: SENSOR --------------------

def create_sensor():
    """Cria um novo registro de sensor"""
    print("\n--- Cadastrar Novo Sensor ---")
    
    # Lista culturas primeiro
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id_cultura, descricao_cultura FROM cultura WHERE ativo = 'S' ORDER BY id_cultura")
        culturas = cursor.fetchall()
        
        if not culturas:
            print("Não há culturas ativas cadastradas. Cadastre uma cultura primeiro.")
            return
        
        print("\nCulturas disponíveis:")
        for cultura in culturas:
            print(f"ID: {cultura[0]}, Descrição: {cultura[1]}")
        
        id_cultura = input("\nID da cultura para associar ao sensor: ")
        try:
            id_cultura = int(id_cultura)
        except ValueError:
            print("ID inválido. Operação cancelada.")
            return
        
        # Verifica se a cultura existe
        cursor.execute("SELECT 1 FROM cultura WHERE id_cultura = :1", [id_cultura])
        if not cursor.fetchone():
            print(f"Cultura com ID {id_cultura} não encontrada.")
            return
        
        numero_serie = input("Número de série do sensor: ")
        if not numero_serie:
            print("Número de série é obrigatório.")
            return
        
        # Verifica se o número de série já existe
        cursor.execute("SELECT 1 FROM sensor WHERE numero_serie = :1", [numero_serie])
        if cursor.fetchone():
            print(f"Já existe um sensor com o número de série {numero_serie}.")
            return
        
        ativo = input("Ativo (S/N): ").upper()
        if ativo not in ['S', 'N']:
            print("Valor inválido para campo ativo. Utilizando 'S' como padrão.")
            ativo = 'S'
        
        # Obtém próximo ID de sensor
        cursor.execute("SELECT NVL(MAX(id_sensor), 0) + 1 FROM sensor")
        id_sensor = cursor.fetchone()[0]
        
        cursor.execute(
            "INSERT INTO sensor (id_sensor, id_cultura, numero_serie, ativo) VALUES (:1, :2, :3, :4)",
            [id_sensor, id_cultura, numero_serie, ativo]
        )
        connection.commit()
        print(f"Sensor cadastrado com sucesso! ID: {id_sensor}")
        
    except cx_Oracle.Error as error:
        print(f"Erro ao cadastrar sensor: {error}")

def read_sensor():
    """Lê todos os registros de sensor"""
    print("\n--- Listar Sensores ---")
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT s.id_sensor, s.numero_serie, s.ativo, c.id_cultura, c.descricao_cultura 
            FROM sensor s
            JOIN cultura c ON s.id_cultura = c.id_cultura
            ORDER BY s.id_sensor
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("Nenhum sensor cadastrado.")
            return
        
        print(f"{'ID':<5} {'Número Série':<20} {'Ativo':<6} {'ID Cultura':<10} {'Descrição Cultura':<30}")
        print("-" * 75)
        
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<6} {row[3]:<10} {row[4]:<30}")
            
    except cx_Oracle.Error as error:
        print(f"Erro ao listar sensores: {error}")

def update_sensor():
    """Atualiza um registro de sensor"""
    print("\n--- Atualizar Sensor ---")
    
    id_sensor = input("ID do sensor que deseja atualizar: ")
    try:
        id_sensor = int(id_sensor)
    except ValueError:
        print("ID inválido. Operação cancelada.")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT s.id_sensor, s.numero_serie, s.ativo, c.id_cultura, c.descricao_cultura 
            FROM sensor s
            JOIN cultura c ON s.id_cultura = c.id_cultura
            WHERE s.id_sensor = :1
        """, [id_sensor])
        row = cursor.fetchone()
        
        if not row:
            print(f"Sensor com ID {id_sensor} não encontrado.")
            return
        
        print(f"Sensor atual: ID: {row[0]}, Número Série: {row[1]}, Ativo: {row[2]}, Cultura: {row[4]} (ID: {row[3]})")
        print("Deixe em branco para manter o valor atual.")
        
        numero_serie = input(f"Novo número de série [{row[1]}]: ")
        ativo = input(f"Novo status (S/N) [{row[2]}]: ").upper()
        
        # Listar culturas disponíveis
        cursor.execute("SELECT id_cultura, descricao_cultura FROM cultura WHERE ativo = 'S' ORDER BY id_cultura")
        culturas = cursor.fetchall()
        
        if culturas:
            print("\nCulturas disponíveis:")
            for cultura in culturas:
                print(f"ID: {cultura[0]}, Descrição: {cultura[1]}")
            
            id_cultura = input(f"Nova cultura (ID) [{row[3]}]: ")
            if id_cultura:
                try:
                    id_cultura = int(id_cultura)
                    # Verificar se a cultura existe
                    cursor.execute("SELECT 1 FROM cultura WHERE id_cultura = :1", [id_cultura])
                    if not cursor.fetchone():
                        print(f"Cultura com ID {id_cultura} não encontrada. Mantendo cultura atual.")
                        id_cultura = row[3]
                except ValueError:
                    print("ID inválido. Mantendo cultura atual.")
                    id_cultura = row[3]
            else:
                id_cultura = row[3]
        else:
            print("Não há culturas ativas disponíveis.")
            id_cultura = row[3]
        
        # Verifica número de série
        if numero_serie:
            cursor.execute("SELECT 1 FROM sensor WHERE numero_serie = :1 AND id_sensor != :2", [numero_serie, id_sensor])
            if cursor.fetchone():
                print(f"Já existe outro sensor com o número de série {numero_serie}. Mantendo número atual.")
                numero_serie = row[1]
        else:
            numero_serie = row[1]
        
        # Verifica status ativo
        if not ativo:
            ativo = row[2]
        elif ativo not in ['S', 'N']:
            print("Valor inválido para campo ativo. Mantendo valor atual.")
            ativo = row[2]
        
        cursor.execute(
            "UPDATE sensor SET numero_serie = :1, ativo = :2, id_cultura = :3 WHERE id_sensor = :4",
            [numero_serie, ativo, id_cultura, id_sensor]
        )
        connection.commit()
        print(f"Sensor atualizado com sucesso!")
        
    except cx_Oracle.Error as error:
        print(f"Erro ao atualizar sensor: {error}")

def delete_sensor():
    """Exclui um registro de sensor"""
    print("\n--- Excluir Sensor ---")
    
    id_sensor = input("ID do sensor que deseja excluir: ")
    try:
        id_sensor = int(id_sensor)
    except ValueError:
        print("ID inválido. Operação cancelada.")
        return
    
    try:
        cursor = connection.cursor()
        
        # Verifica se o sensor existe
        cursor.execute("SELECT 1 FROM sensor WHERE id_sensor = :1", [id_sensor])
        if not cursor.fetchone():
            print(f"Sensor com ID {id_sensor} não encontrado.")
            return
        
        # Verifica se há monitoramentos associados ao sensor
        cursor.execute("SELECT COUNT(*) FROM monitoramento WHERE id_sensor = :1", [id_sensor])
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Este sensor possui {count} registros de monitoramento.")
            confirm = input(f"Excluir o sensor irá remover também todos os registros de monitoramento. Continuar? (S/N): ").upper()
            if confirm != 'S':
                print("Operação cancelada.")
                return
            
            # Remove os registros de monitoramento primeiro
            cursor.execute("DELETE FROM monitoramento WHERE id_sensor = :1", [id_sensor])
            print(f"{count} registros de monitoramento excluídos.")
        
        # Remove associações com tipos de sensor
        cursor.execute("DELETE FROM sensor_tipo_sensor WHERE id_sensor = :1", [id_sensor])
        
        # Remove calibrações de sensor
        cursor.execute("DELETE FROM calibracao_sensor WHERE id_sensor = :1", [id_sensor])
        
        # Remove o sensor
        cursor.execute("DELETE FROM sensor WHERE id_sensor = :1", [id_sensor])
        connection.commit()
        print(f"Sensor excluído com sucesso!")
        
    except cx_Oracle.Error as error:
        print(f"Erro ao excluir sensor: {error}")

# -------------------- OPERAÇÕES CRUD: MONITORAMENTO --------------------

def list_recent_monitoramentos():
    """Lista registros recentes de monitoramento"""
    print("\n--- Últimos Registros de Monitoramento ---")
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT m.id_monitoramento, m.id_sensor, ts.descricao, m.valor, um.abreviacao, 
                   TO_CHAR(m.data_hora_monitoramento, 'DD/MM/YYYY HH24:MI:SS'), c.descricao_cultura
            FROM monitoramento m
            JOIN sensor s ON m.id_sensor = s.id_sensor
            JOIN cultura c ON s.id_cultura = c.id_cultura
            JOIN sensor_tipo_sensor sts ON s.id_sensor = sts.id_sensor
            JOIN tipo_sensor ts ON sts.id_tipo_sensor = ts.id_tipo_sensor
            JOIN unidade_medida um ON ts.id_unidade_medida = um.id_unidade_medida
            ORDER BY m.data_hora_monitoramento DESC
            FETCH FIRST 20 ROWS ONLY
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("Nenhum registro de monitoramento encontrado.")
            return
        
        print(f"{'ID':<6} {'Sensor':<10} {'Tipo':<15} {'Valor':<8} {'Unidade':<8} {'Data/Hora':<20} {'Cultura':<20}")
        print("-" * 90)
        
        for row in rows:
            print(f"{row[0]:<6} {row[1]:<10} {row[2]:<15} {row[3]:<8.2f} {row[4]:<8} {row[5]:<20} {row[6]:<20}")
            
    except cx_Oracle.Error as error:
        print(f"Erro ao listar monitoramentos: {error}")

# -------------------- MENU PRINCIPAL --------------------

def show_menu():
    """Exibe o menu principal do sistema"""
    print("\n========== FarmTech Solutions CRUD ==========")
    print("1. Cadastrar Cultura")
    print("2. Listar Culturas")
    print("3. Atualizar Cultura")
    print("4. Excluir Cultura")
    print("5. Cadastrar Sensor")
    print("6. Listar Sensores")
    print("7. Atualizar Sensor")
    print("8. Excluir Sensor")
    print("9. Visualizar Últimos Monitoramentos")
    print("0. Sair")
    print("===========================================")
    return input("Escolha uma opção: ")

def main():
    """Função principal do programa"""
    print("\n====== FarmTech Solutions - Sistema CRUD ======")
    print("Iniciando aplicação...")
    
    # Conecta ao banco de dados
    global connection
    if not connect_to_db():
        print("Não foi possível conectar ao banco de dados. O programa será encerrado.")
        sys.exit(1)
    
    # Inicia o servidor para receber dados do ESP32
    global server
    if not start_server():
        print("Não foi possível iniciar o servidor HTTP. Algumas funcionalidades podem não estar disponíveis.")
    
    print("\nSistema iniciado com sucesso! Aguardando dados do ESP32...")
    
    # Loop principal do menu
    while True:
        try:
            opcao = show_menu()
            
            if opcao == '1':
                create_cultura()
            elif opcao == '2':
                read_cultura()
            elif opcao == '3':
                update_cultura()
            elif opcao == '4':
                delete_cultura()
            elif opcao == '5':
                create_sensor()
            elif opcao == '6':
                read_sensor()
            elif opcao == '7':
                update_sensor()
            elif opcao == '8':
                delete_sensor()
            elif opcao == '9':
                list_recent_monitoramentos()
            elif opcao == '0':
                break
            else:
                print("Opção inválida. Tente novamente.")
                
        except Exception as e:
            print(f"Erro inesperado: {e}")
    
    # Finaliza conexões e servidor
    if connection:
        connection.close()
        print("Conexão com banco de dados encerrada.")
    
    if server:
        server.shutdown()
        print("Servidor HTTP encerrado.")
    
    print("Programa finalizado. Obrigado por utilizar o sistema FarmTech Solutions!")

if __name__ == "__main__":
    main()