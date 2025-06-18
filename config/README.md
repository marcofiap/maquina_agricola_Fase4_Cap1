# 🔧 Farm Tech Solutions - Configurações

Este package contém todas as configurações centralizadas do sistema Farm Tech Solutions.

## 📁 Arquivos

### `database_config.py`
Configuração específica do banco PostgreSQL com funções utilitárias:
- `DatabaseConfig`: Classe com configurações do banco
- `conectar_postgres()`: Função para conectar ao PostgreSQL
- `criar_schema_e_tabela()`: Cria schema e tabela se não existirem
- `testar_conexao()`: Testa a conexão com o banco

### `settings.py`
Configurações gerais do sistema usando variáveis de ambiente:
- Configurações do PostgreSQL
- Configurações do Flask
- Configurações do ESP32
- Configurações de logging

## 🚀 Como Usar

### Importando a configuração do banco:
```python
from config.database_config import DatabaseConfig, conectar_postgres

# Conectar ao banco
conn, cursor = conectar_postgres()

# Usar configurações
schema = DatabaseConfig.SCHEMA
host = DatabaseConfig.HOST
```

### Usando settings com variáveis de ambiente:
```python
from config.settings import settings

# Acessar configurações
host = settings.POSTGRES_HOST
port = settings.POSTGRES_PORT

# Imprimir configuração atual
settings.print_config()
```

## 🌍 Variáveis de Ambiente

Você pode sobrescrever as configurações usando variáveis de ambiente:

```bash
# PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=meu_banco
export POSTGRES_USER=meu_usuario
export POSTGRES_PASSWORD=minha_senha
export POSTGRES_SCHEMA=MeuSchema

# Flask
export FLASK_HOST=127.0.0.1
export FLASK_PORT=8080
export FLASK_DEBUG=False

# ESP32
export ESP32_SERVERS=192.168.1.100:8000,192.168.1.101:8000

# Logging
export LOG_LEVEL=DEBUG
export LOG_FILE=debug.log
```

## 📝 Exemplo de arquivo .env

Crie um arquivo `.env` na raiz do projeto:

```
# === POSTGRESQL ===
POSTGRES_HOST=52.86.250.115
POSTGRES_PORT=5432
POSTGRES_DB=fiap
POSTGRES_USER=fiap
POSTGRES_PASSWORD=fiap123456
POSTGRES_SCHEMA=Fase4Cap1

# === FLASK ===
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_DEBUG=True

# === ESP32 ===
ESP32_SERVERS=192.168.0.12:8000,192.168.2.126:8000

# === LOGGING ===
LOG_LEVEL=INFO
LOG_FILE=farm_tech.log
```

## 🧪 Testando

Para testar as configurações:

```bash
# Testar configuração do banco
python3 -m config.database_config

# Testar settings
python3 -m config.settings
```

## 📦 Dependências

- `psycopg2-binary`: Para conexão PostgreSQL
- `python-dotenv`: Para carregar variáveis de ambiente (opcional) 