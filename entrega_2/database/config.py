"""
Arquivo de configuração para o sistema FarmTech Solutions
Contém parâmetros de conexão com o banco de dados e outras configurações do sistema
"""

# # Configuração do banco de dados Oracle
# DB_CONFIG = {
#     "user": "username",
#     "password": "password",
#     "dsn": "localhost:1521/orcl"
# }

DB_CONFIG = {
    "user": "rm563348",
    "password": "220982",
    "dsn": "oracle.fiap.com.br:1521/ORCL"
}

# Configuração do servidor HTTP
SERVER_CONFIG = {
    "host": "",  # Vazio para escutar em todas as interfaces
    "port": 8000
}

# Outras configurações do sistema
SYSTEM_CONFIG = {
    "debug_mode": False,
    "log_level": "INFO",
    "timeout": 30
}