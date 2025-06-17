"""
Inicializador de Estrutura do Banco de Dados - FarmTech Solutions
Este script executa o arquivo SCRIPT_DDL_Projeto_FarmTech_Solutions.SQL
para criar a estrutura do banco de dados Oracle.
"""

import cx_Oracle
import os
import sys
import time
from config import DB_CONFIG

def get_connection():
    """Estabelece e retorna uma conexão com o banco de dados Oracle"""
    try:
        connection = cx_Oracle.connect(DB_CONFIG["user"], DB_CONFIG["password"], DB_CONFIG["dsn"])
        return connection
    except cx_Oracle.Error as error:
        print(f"Erro ao conectar ao banco de dados Oracle: {error}")
        return None

def execute_ddl_script(script_path):
    """Executa o script DDL para criar a estrutura do banco de dados"""
    print(f"\nExecutando script DDL: {script_path}")
    
    if not os.path.exists(script_path):
        print(f"Erro: Arquivo {script_path} não encontrado.")
        return False
    
    connection = get_connection()
    if not connection:
        print("Não foi possível estabelecer conexão com o banco de dados.")
        return False
    
    try:
        # Lê o conteúdo do arquivo SQL
        with open(script_path, 'r') as file:
            script_content = file.read()
        
        # Divide o script em comandos individuais
        # No Oracle, comandos são tipicamente separados por ';'
        sql_commands = script_content.split(';')
        
        cursor = connection.cursor()
        success_count = 0
        error_count = 0
        
        print("\nIniciando execução dos comandos SQL...")
        
        for i, command in enumerate(sql_commands):
            # Remove espaços em branco e pula comandos vazios
            command = command.strip()
            if not command:
                continue
            
            try:
                # Executa o comando SQL
                cursor.execute(command)
                success_count += 1
                # Feedback a cada 5 comandos executados com sucesso
                if success_count % 5 == 0:
                    print(f"Progresso: {success_count} comandos executados com sucesso...")
            except cx_Oracle.Error as error:
                error_count += 1
                # Ignora erros de "tabela não existe" nos comandos DROP TABLE
                if "ORA-00942" in str(error) and "DROP TABLE" in command.upper():
                    print(f"Aviso: Tabela mencionada em DROP TABLE não existe (ignorando)...")
                else:
                    print(f"\nErro ao executar comando #{i+1}:")
                    print(f"Comando: {command[:100]}..." if len(command) > 100 else f"Comando: {command}")
                    print(f"Erro: {error}")
                    
                    # Pergunta se deseja continuar após erro
                    if error_count > 5:
                        print(f"\nMuitos erros detectados ({error_count}). Continuando automaticamente...")
                    else:
                        continue_option = input("\nDeseja continuar a execução? (S/N): ").upper()
                        if continue_option != 'S':
                            print("Execução interrompida pelo usuário.")
                            connection.close()
                            return False
        
        # Confirma as alterações
        connection.commit()
        print(f"\nExecução concluída!")
        print(f"Total de comandos executados com sucesso: {success_count}")
        print(f"Total de erros: {error_count}")
        
        return error_count == 0  # Retorna True apenas se não houver erros
    
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False
    
    finally:
        if connection:
            connection.close()
            print("Conexão com o banco de dados fechada.")

def verify_tables():
    """Verifica se as tabelas foram criadas com sucesso"""
    print("\nVerificando se as tabelas foram criadas corretamente...")
    
    connection = get_connection()
    if not connection:
        print("Não foi possível estabelecer conexão com o banco de dados para verificação.")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Lista de tabelas esperadas no banco
        expected_tables = [
            'AGUA_APLICADA', 'CALIBRACAO_SENSOR', 'CULTURA', 'MONITORAMENTO',
            'SENSOR', 'SENSOR_TIPO_SENSOR', 'TIPO_SENSOR', 'UNIDADE_MEDIDA',
            'VITAMINAS', 'VITAMINAS_APLICADAS'
        ]
        
        # Verifica cada tabela
        tables_found = []
        tables_missing = []
        
        for table in expected_tables:
            query = f"""
                SELECT table_name 
                FROM user_tables 
                WHERE table_name = '{table}'
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                tables_found.append(table)
            else:
                tables_missing.append(table)
        
        # Exibe o resultado da verificação
        print(f"\nTabelas encontradas ({len(tables_found)}/{len(expected_tables)}):")
        for table in tables_found:
            print(f"✓ {table}")
        
        if tables_missing:
            print(f"\nTabelas não encontradas ({len(tables_missing)}):")
            for table in tables_missing:
                print(f"✗ {table}")
            return False
        
        print("\nTodas as tabelas foram criadas com sucesso!")
        return True
    
    except cx_Oracle.Error as error:
        print(f"Erro ao verificar tabelas: {error}")
        return False
    
    finally:
        if connection:
            connection.close()

def main():
    """Função principal"""
    print("\n====== FarmTech Solutions - Inicialização da Estrutura do Banco de Dados ======")
    print("Este script irá criar todas as tabelas necessárias para o sistema.")
    print("ATENÇÃO: Se as tabelas já existirem, elas serão removidas e recriadas.")
    
    # Confirma a execução
    confirm = input("\nDeseja continuar? (S/N): ").upper()
    if confirm != 'S':
        print("Operação cancelada pelo usuário.")
        return
    
    # Obtém o diretório onde o script Python está localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, 'SCRIPT_DDL_Projeto_FarmTech_Solutions.SQL')
    
    # Solicita caminho do arquivo SQL
    script_path = input(f"\nCaminho do arquivo SQL DDL (pressione Enter para usar '{default_path}'): ")
    if not script_path:
        script_path = default_path

    
    # Testa a conexão com o banco
    print("\nTestando conexão com o banco de dados...")
    connection = get_connection()
    if not connection:
        print("Não foi possível estabelecer conexão com o banco de dados.")
        print("Verifique as credenciais e tente novamente.")
        return
    else:
        print("Conexão com o banco de dados estabelecida com sucesso.")
        connection.close()
    
    # Executar o script DDL
    print("\nIniciando criação da estrutura do banco de dados...")
    start_time = time.time()
    
    result = execute_ddl_script(script_path)
    
    # Verificar o resultado
    if result:
        print("\nEstrutura do banco de dados criada com sucesso!")
        
        # Verifica se as tabelas foram criadas
        verify_result = verify_tables()
        if verify_result:
            print("\nO banco de dados está pronto para uso!")
            print("\nAgora você pode executar o script 'inicializar_banco.py' para inserir os dados iniciais")
            print("e em seguida executar o programa principal 'farmtech_crud.py'.")
    else:
        print("\nOcorreram erros durante a criação da estrutura do banco de dados.")
        print("Verifique os erros acima e tente novamente.")
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nTempo de execução: {execution_time:.2f} segundos")

if __name__ == "__main__":
    main()