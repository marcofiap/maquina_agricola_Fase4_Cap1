import oracledb
import pandas as pd

# Configurações do Oracle
DB_USER = "system"
DB_PASSWORD = "system"
DB_DSN = "localhost:1521/xe"

# Conectar ao banco
conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
cursor = conn.cursor()

# Consultar os dados da tabela leituras_sensores
query = "SELECT timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua FROM leituras_sensores"
cursor.execute(query)

# Obter os nomes das colunas
colunas = [desc[0].lower() for desc in cursor.description]

# Carregar os dados em um DataFrame
dados = cursor.fetchall()
df = pd.DataFrame(dados, columns=colunas)

# Exportar para CSV
df.to_csv("leituras_sensores.csv", index=False)

# Fechar conexões
cursor.close()
conn.close()

print("✅ Dados exportados para leituras_sensores.csv com sucesso!")
