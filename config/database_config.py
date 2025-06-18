"""
Configuração centralizada do banco de dados PostgreSQL
Farm Tech Solutions - FIAP Fase 4 Cap 1
"""

import psycopg2
import os

# === CONFIGURAÇÕES DO BANCO DE DADOS POSTGRESQL ===
class DatabaseConfig:
    HOST = "52.86.250.115"
    PORT = 5432
    DATABASE = "fiap"
    USER = "fiap"
    PASSWORD = "fiap123456"
    SCHEMA = "Fase4Cap1"
    
    # Para ambiente de desenvolvimento local (opcional)
    LOCAL_SQLITE = "leituras_sensores.db"
    
    @classmethod
    def get_connection_params(cls):
        """Retorna os parâmetros de conexão como dicionário."""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'database': cls.DATABASE,
            'user': cls.USER,
            'password': cls.PASSWORD
        }
    
    @classmethod
    def get_connection_string(cls):
        """Retorna string de conexão PostgreSQL."""
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"

# === FUNÇÕES UTILITÁRIAS DE CONEXÃO ===
def conectar_postgres():
    """
    Conecta ao banco PostgreSQL e configura o schema.
    Retorna: (conexão, cursor) ou (None, None) em caso de erro
    """
    try:
        conn = psycopg2.connect(**DatabaseConfig.get_connection_params())
        cursor = conn.cursor()
        
        # Define o schema de busca
        cursor.execute(f"SET search_path TO {DatabaseConfig.SCHEMA}, public")
        conn.commit()
        
        print(f"✅ Conectado ao PostgreSQL - Schema: {DatabaseConfig.SCHEMA}")
        return conn, cursor
        
    except psycopg2.Error as error:
        print(f"❌ Erro ao conectar ao PostgreSQL: {error}")
        return None, None

def criar_schema_e_tabela():
    """
    Cria o schema e tabela se não existirem.
    """
    conn, cursor = conectar_postgres()
    if conn and cursor:
        try:
            # Cria o schema se não existir
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {DatabaseConfig.SCHEMA}")
            
            # Cria a tabela no schema específico
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DatabaseConfig.SCHEMA}.leituras_sensores (
                    timestamp VARCHAR(255) PRIMARY KEY,
                    umidade DECIMAL,
                    temperatura DECIMAL,
                    ph DECIMAL,
                    fosforo VARCHAR(10),
                    potassio VARCHAR(10),
                    bomba_dagua VARCHAR(10)
                )
            """)
            conn.commit()
            print(f"✅ Schema e tabela '{DatabaseConfig.SCHEMA}.leituras_sensores' verificados/criados.")
            return True
            
        except psycopg2.Error as error:
            print(f"❌ Erro ao criar schema/tabela: {error}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                conn.close()
    return False

def testar_conexao():
    """
    Testa a conexão com o banco de dados.
    """
    print("🔍 Testando conexão com PostgreSQL...")
    conn, cursor = conectar_postgres()
    
    if conn and cursor:
        try:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✅ Conexão bem-sucedida!")
            print(f"📊 Versão PostgreSQL: {version}")
            
            # Testa se a tabela existe
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = '{DatabaseConfig.SCHEMA}' 
                AND table_name = 'leituras_sensores'
            """)
            table_exists = cursor.fetchone()[0] > 0
            print(f"📋 Tabela 'leituras_sensores' existe: {'✅ Sim' if table_exists else '❌ Não'}")
            
            return True
        except psycopg2.Error as error:
            print(f"❌ Erro no teste: {error}")
            return False
        finally:
            cursor.close()
            conn.close()
    else:
        print("❌ Falha na conexão.")
        return False

# === EXECUÇÃO DIRETA PARA TESTE ===
if __name__ == "__main__":
    print("🚀 Testando configuração do banco de dados...")
    print(f"🏗️ Schema: {DatabaseConfig.SCHEMA}")
    print(f"🖥️ Host: {DatabaseConfig.HOST}")
    print(f"💾 Database: {DatabaseConfig.DATABASE}")
    
    # Testa conexão
    if testar_conexao():
        # Cria schema e tabela se necessário
        criar_schema_e_tabela()
    else:
        print("❌ Configure as credenciais do banco antes de continuar.") 