"""
Script Python para inicialização do banco de dados FarmTech Solutions
Este script executa o arquivo SQL para inserir os dados iniciais necessários 
para o funcionamento do sistema CRUD com o ESP32.
"""

import cx_Oracle
import os
import sys
import re
from config import DB_CONFIG

# Conexão do banco de dados
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

def execute_sql_file(connection, sql_file_path):
    """Executa um arquivo SQL no banco de dados"""
    if not os.path.exists(sql_file_path):
        print(f"Arquivo {sql_file_path} não encontrado.")
        return False
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            # Ler o arquivo inteiro
            sql_content = file.read()
        
        # Remover comentários de múltiplas linhas se houver
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        # Dividir o conteúdo em comandos individuais
        # Esta é uma abordagem mais robusta para dividir por ponto e vírgula
        raw_commands = sql_content.split(';')
        
        cursor = connection.cursor()
        
        for raw_command in raw_commands:
            # Processar cada linha para remover comentários
            lines = []
            for line in raw_command.split('\n'):
                # Remover comentários inline (depois de --)
                if '--' in line:
                    line = line.split('--')[0]
                lines.append(line)
            
            # Juntar as linhas de volta em um comando
            command = ' '.join(line.strip() for line in lines if line.strip())
            
            # Executar apenas se houver um comando válido
            if command.strip():
                try:
                    cursor.execute(command)
                    if command.upper().strip().startswith('SELECT'):
                        rows = cursor.fetchall()
                        for row in rows:
                            print(row)
                except cx_Oracle.Error as error:
                    print(f"Erro ao executar comando SQL: {error}")
                    print(f"Comando problemático: {command}")
        
        connection.commit()
        cursor.close()
        print("Arquivo SQL executado com sucesso.")
        return True
    
    except Exception as e:
        print(f"Erro ao executar arquivo SQL: {e}")
        return False

def verificar_dados(connection):
    """Verifica se os dados foram inseridos corretamente"""
    try:
        cursor = connection.cursor()
        
        # Verifica unidades de medida
        cursor.execute("SELECT COUNT(*) FROM unidade_medida")
        count = cursor.fetchone()[0]
        print(f"Unidades de medida cadastradas: {count}")
        
        # Verifica tipos de sensores
        cursor.execute("SELECT COUNT(*) FROM tipo_sensor")
        count = cursor.fetchone()[0]
        print(f"Tipos de sensores cadastrados: {count}")
        
        # Verifica culturas
        cursor.execute("SELECT id_cultura, descricao_cultura FROM cultura")
        rows = cursor.fetchall()
        print("\nCulturas cadastradas:")
        for row in rows:
            print(f"ID: {row[0]}, Descrição: {row[1]}")
        
        # Verifica sensores
        cursor.execute("""
            SELECT s.id_sensor, s.numero_serie, ts.descricao, c.descricao_cultura 
            FROM sensor s
            JOIN sensor_tipo_sensor sts ON s.id_sensor = sts.id_sensor
            JOIN tipo_sensor ts ON sts.id_tipo_sensor = ts.id_tipo_sensor
            JOIN cultura c ON s.id_cultura = c.id_cultura
        """)
        rows = cursor.fetchall()
        print("\nSensores cadastrados:")
        for row in rows:
            print(f"ID: {row[0]}, Número Série: {row[1]}, Tipo: {row[2]}, Cultura: {row[3]}")
        
        cursor.close()
        return True
    
    except cx_Oracle.Error as error:
        print(f"Erro ao verificar dados: {error}")
        return False

def main():
    """Função principal"""
    print("\n====== FarmTech Solutions - Inicialização do Banco de Dados ======")
    
    # Conecta ao banco de dados
    global connection
    connection = connect_to_db()
    if not connection:
        print("Não foi possível conectar ao banco de dados. O programa será encerrado.")
        sys.exit(1)

    # Obtém o diretório onde o script Python está localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(script_dir, 'script_dados_iniciais.SQL')# Obtém o diretório onde o script Python está localizado
    # Solicita caminho do arquivo SQL
    custom_path = input(f"Caminho do arquivo SQL (pressione Enter para usar o padrão '{sql_file_path}'): ")
    if not custom_path:
        custom_path = sql_file_path
    
    # Executa o arquivo SQL
    result = execute_sql_file(connection, sql_file_path)
    
    if result:
        # Verifica se os dados foram inseridos corretamente
        print("\n====== Verificando dados inseridos ======")
        verificar_dados(connection)
    
    # Fecha a conexão
    connection.close()
    print("\n====== Inicialização concluída ======")
    print("Você pode agora executar o sistema CRUD FarmTech Solutions.")

if __name__ == "__main__":
    main()