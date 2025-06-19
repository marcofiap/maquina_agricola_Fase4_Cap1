"""
Farm Tech Solutions - Configuration Package
FIAP Fase 4 Cap 1

Este package contém as configurações centralizadas do sistema,
incluindo configurações de banco de dados e outras constantes.
"""

from .database_config import _config as DatabaseConfig, conectar_postgres, criar_schema_e_tabela, testar_conexao
from .settings import settings

__version__ = "1.0.0"
__author__ = "Farm Tech Solutions" 