"""
Configuração centralizada do banco de dados PostgreSQL
Farm Tech Solutions - FIAP Fase 4 Cap 1
"""

import psycopg2
import os
from .settings import settings

# === CONFIGURAÇÕES DO BANCO DE DADOS POSTGRESQL ===
class DatabaseConfig:
    """Configuração do banco que usa settings.py como fonte."""
    
    @property
    def HOST(self):
        return settings.POSTGRES_HOST
    
    @property
    def PORT(self):
        return settings.POSTGRES_PORT
    
    @property
    def DATABASE(self):
        return settings.POSTGRES_DB
    
    @property
    def USER(self):
        return settings.POSTGRES_USER
    
    @property
    def PASSWORD(self):
        return settings.POSTGRES_PASSWORD
    
    @property
    def SCHEMA(self):
        return settings.POSTGRES_SCHEMA
    
    # Para ambiente de desenvolvimento local (opcional)
    LOCAL_SQLITE = "leituras_sensores.db"
    
    @classmethod
    def get_connection_params(cls):
        """Retorna os parâmetros de conexão como dicionário."""
        config = cls()
        return {
            'host': config.HOST,
            'port': config.PORT,
            'database': config.DATABASE,
            'user': config.USER,
            'password': config.PASSWORD
        }
    
    @classmethod
    def get_connection_string(cls):
        """Retorna string de conexão PostgreSQL."""
        config = cls()
        return f"postgresql://{config.USER}:{config.PASSWORD}@{config.HOST}:{config.PORT}/{config.DATABASE}"

# Instância global para compatibilidade com código existente
_config = DatabaseConfig()

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
        cursor.execute(f"SET search_path TO {_config.SCHEMA}, public")
        # Define timezone para Brasil
        cursor.execute("SET timezone = 'America/Sao_Paulo'")
        conn.commit()
        
        print(f"✅ Conectado ao PostgreSQL - Schema: {_config.SCHEMA}")
        return conn, cursor
        
    except psycopg2.Error as error:
        print(f"❌ Erro ao conectar ao PostgreSQL: {error}")
        return None, None

def criar_schema_e_tabela():
    """
    Cria o schema e tabela se não existirem.
    Nova estrutura com id autoincremento, data_hora_leitura e criacaots.
    """
    conn, cursor = conectar_postgres()
    if conn and cursor:
        try:
            # Cria o schema se não existir
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {_config.SCHEMA}")
            
            # Cria a tabela no schema específico com nova estrutura
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {_config.SCHEMA}.leituras_sensores (
                    id SERIAL PRIMARY KEY,
                    data_hora_leitura TIMESTAMP NOT NULL,
                    criacaots TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'America/Sao_Paulo'),
                    umidade DECIMAL(5,2),
                    temperatura DECIMAL(5,2),
                    ph DECIMAL(4,2),
                    fosforo BOOLEAN,
                    potassio BOOLEAN,
                    bomba_dagua BOOLEAN
                )
            """)
            conn.commit()
            print(f"✅ Schema e tabela '{_config.SCHEMA}.leituras_sensores' verificados/criados com nova estrutura.")
            print("📋 Estrutura da tabela:")
            print("   • id (SERIAL PRIMARY KEY) - Chave primária autoincremento")
            print("   • data_hora_leitura (TIMESTAMP) - Horário da leitura do sensor")
            print("   • criacaots (TIMESTAMP DEFAULT CURRENT_TIMESTAMP) - Horário de inserção no banco")
            print("   • umidade, temperatura, ph (DECIMAL) - Valores numéricos dos sensores")
            print("   • fosforo, potassio, bomba_dagua (BOOLEAN) - Estados dos sensores e bomba (true/false)")
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
    print(f"📊 Configuração: {_config.USER}@{_config.HOST}:{_config.PORT}/{_config.DATABASE}")
    
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
                WHERE table_schema = '{_config.SCHEMA}' 
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
    print(f"🏗️ Schema: {_config.SCHEMA}")
    print(f"🖥️ Host: {_config.HOST}")
    print(f"💾 Database: {_config.DATABASE}")
    
    # Testa conexão
    if testar_conexao():
        # Executa migração para nova estrutura
        print("\n🔄 Verificando se é necessário migrar para nova estrutura...")
        migrar_tabela_para_nova_estrutura()
    else:
        print("❌ Configure as credenciais do banco antes de continuar.") 