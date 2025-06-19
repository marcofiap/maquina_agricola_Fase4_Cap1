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
            
            # Cria tabela de dados meteorológicos
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {_config.SCHEMA}.dados_meteorologicos (
                    id SERIAL PRIMARY KEY,
                    data_hora_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    temperatura_externa DECIMAL(5,2),
                    umidade_ar DECIMAL(5,2),
                    pressao_atmosferica DECIMAL(8,2),
                    velocidade_vento DECIMAL(5,2),
                    direcao_vento VARCHAR(10),
                    condicao_clima VARCHAR(50),
                    probabilidade_chuva DECIMAL(5,2),
                    quantidade_chuva DECIMAL(5,2) DEFAULT 0.0,
                    indice_uv DECIMAL(4,2),
                    visibilidade DECIMAL(5,1),
                    cidade VARCHAR(100) DEFAULT 'Camopi',
                    fonte_dados VARCHAR(50) DEFAULT 'Simulado'
                )
            """)
            
            # Cria tabela de leituras integradas
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {_config.SCHEMA}.leituras_integradas (
                    id SERIAL PRIMARY KEY,
                    data_hora_leitura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    -- Dados dos sensores IoT
                    umidade_solo DECIMAL(5,2) NOT NULL,
                    temperatura_solo DECIMAL(5,2) NOT NULL,
                    ph_solo DECIMAL(4,2) NOT NULL,
                    fosforo BOOLEAN NOT NULL,
                    potassio BOOLEAN NOT NULL,
                    bomba_dagua BOOLEAN NOT NULL,
                    -- Dados meteorológicos
                    temperatura_externa DECIMAL(5,2),
                    umidade_ar DECIMAL(5,2),
                    pressao_atmosferica DECIMAL(8,2),
                    velocidade_vento DECIMAL(5,2),
                    condicao_clima VARCHAR(50),
                    probabilidade_chuva DECIMAL(5,2),
                    quantidade_chuva DECIMAL(5,2) DEFAULT 0.0,
                    -- Dados calculados
                    diferenca_temperatura DECIMAL(5,2), -- temp_externa - temp_solo
                    deficit_umidade DECIMAL(5,2), -- umidade_ar - umidade_solo
                    fator_evapotranspiracao DECIMAL(5,2) -- calculado com base em vento + temperatura
                )
            """)
            
            # Criar view para análise ML
            cursor.execute(f"""
                CREATE OR REPLACE VIEW {_config.SCHEMA}.view_ml_completa AS
                SELECT 
                    li.id,
                    li.data_hora_leitura,
                    li.umidade_solo,
                    li.temperatura_solo,
                    li.ph_solo,
                    li.fosforo::int as fosforo,
                    li.potassio::int as potassio,
                    li.bomba_dagua::int as bomba_dagua,
                    li.temperatura_externa,
                    li.umidade_ar,
                    li.pressao_atmosferica,
                    li.velocidade_vento,
                    li.probabilidade_chuva,
                    li.quantidade_chuva,
                    li.diferenca_temperatura,
                    li.deficit_umidade,
                    li.fator_evapotranspiracao,
                    EXTRACT(HOUR FROM li.data_hora_leitura) as hora_do_dia,
                    EXTRACT(DOW FROM li.data_hora_leitura) as dia_semana,
                    EXTRACT(MONTH FROM li.data_hora_leitura) as mes,
                    CASE 
                        WHEN li.probabilidade_chuva > 70 THEN 1 
                        ELSE 0 
                    END as vai_chover_hoje,
                    CASE 
                        WHEN li.velocidade_vento > 15 THEN 1 
                        ELSE 0 
                    END as vento_forte,
                    CASE 
                        WHEN li.temperatura_externa > 30 THEN 1 
                        ELSE 0 
                    END as dia_quente
                FROM {_config.SCHEMA}.leituras_integradas li
                ORDER BY li.data_hora_leitura DESC
            """)
            
            conn.commit()
            print(f"✅ Schema e tabelas '{_config.SCHEMA}' verificados/criados com nova estrutura.")
            print("📋 Estrutura das tabelas:")
            print("   • leituras_sensores - Dados básicos dos sensores")
            print("   • dados_meteorologicos - Dados do clima")
            print("   • leituras_integradas - Dados combinados para ML")
            print("   • view_ml_completa - View para análise com 20+ features")
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
        # Cria estrutura do banco
        print("\n🔄 Criando estrutura do banco...")
        criar_schema_e_tabela()
    else:
        print("❌ Configure as credenciais do banco antes de continuar.") 