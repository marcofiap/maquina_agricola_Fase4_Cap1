"""
Configurações do sistema usando variáveis de ambiente
Farm Tech Solutions - FIAP Fase 4 Cap 1
"""

import os

# Tenta carregar variáveis do arquivo .env se o módulo dotenv estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variáveis de ambiente carregadas do .env")
except ImportError:
    print("ℹ️ python-dotenv não instalado. Usando apenas variáveis de ambiente do sistema.")

class Settings:
    """Configurações do sistema que podem ser sobrescritas por variáveis de ambiente."""
    
    # Configurações do PostgreSQL
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', '52.86.250.115')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'fiap')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'fiap')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'fiap123456')
    POSTGRES_SCHEMA = os.getenv('POSTGRES_SCHEMA', 'Fase4Cap1')
    
    # Configurações do Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '8000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Configurações do ESP32
    ESP32_SERVERS = os.getenv('ESP32_SERVERS', '192.168.0.12:8000,192.168.2.126:8000').split(',')
    
    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'farm_tech.log')
    
    @classmethod
    def get_postgres_url(cls):
        """Retorna URL de conexão PostgreSQL."""
        return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
    
    @classmethod
    def get_connection_params(cls):
        """Retorna parâmetros de conexão como dicionário."""
        return {
            'host': cls.POSTGRES_HOST,
            'port': cls.POSTGRES_PORT,
            'database': cls.POSTGRES_DB,
            'user': cls.POSTGRES_USER,
            'password': cls.POSTGRES_PASSWORD
        }
    
    @classmethod
    def print_config(cls):
        """Imprime configuração atual (sem mostrar senha)."""
        print("🔧 CONFIGURAÇÃO ATUAL:")
        print(f"   PostgreSQL: {cls.POSTGRES_USER}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}")
        print(f"   Schema: {cls.POSTGRES_SCHEMA}")
        print(f"   Flask: {cls.FLASK_HOST}:{cls.FLASK_PORT} (Debug: {cls.FLASK_DEBUG})")
        print(f"   ESP32 Servers: {', '.join(cls.ESP32_SERVERS)}")
        print(f"   Log Level: {cls.LOG_LEVEL}")

# Instância global das configurações
settings = Settings()

if __name__ == "__main__":
    print("🚀 Farm Tech Solutions - Configurações")
    settings.print_config() 