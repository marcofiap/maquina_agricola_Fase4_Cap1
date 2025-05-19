import oracledb
from datetime import datetime

# === CONFIGURAÇÃO DO BANCO DE DADOS ORACLE ===
DB_USER = "system"
DB_PASSWORD = "system"
DB_DSN = "localhost:1521/xe"

# === CONECTA AO BANCO DE DADOS ===
def conectar_db():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()
        return conn, cursor
    except oracledb.Error as error:
        print("❌ Erro na conexão:", error)
        return None, None

# === INSERE UMA NOVA LEITURA MANUAL ===
def inserir_dados():
    print("\n📥 Inserir nova leitura:")
    try:
        timestamp = input("Timestamp (YYYY-MM-DD HH:MM:SS): ")
        umidade = float(input("Umidade (%): "))
        temperatura = float(input("Temperatura (°C): "))
        ph = float(input("pH: "))
        fosforo = input("Fósforo (presente/ausente): ").lower()
        potassio = input("Potássio (presente/ausente): ").lower()
        bomba = input("Bomba (on/off): ").lower()

        # Validação de faixas (opcional)
        if not (0 <= umidade <= 100 and 0 <= ph <= 14):
            print("❌ Valores fora da faixa válida.")
            return

        conn, cursor = conectar_db()
        if conn:
            cursor.execute("""
                INSERT INTO leituras_sensores (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba))
            conn.commit()
            print("✅ Dados inseridos com sucesso.")
    except ValueError:
        print("❌ Erro: valores numéricos inválidos.")
    except oracledb.Error as e:
        print("❌ Erro ao inserir:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()

# === LISTA TODAS AS LEITURAS ===
def listar_dados():
    print("\n📄 Listando dados...")
    conn, cursor = conectar_db()
    if conn:
        cursor.execute("SELECT * FROM leituras_sensores ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        cursor.close()
        conn.close()

# === ATUALIZA UMA LEITURA EXISTENTE ===
def atualizar_dado():
    print("\n✏️ Atualizar leitura:")
    timestamp = input("Timestamp da leitura que deseja atualizar: ")
    try:
        nova_umidade = float(input("Nova umidade (%): "))
        nova_temperatura = float(input("Nova temperatura (°C): "))
        novo_ph = float(input("Novo pH: "))
        novo_fosforo = input("Novo fósforo (presente/ausente): ").lower()
        novo_potassio = input("Novo potássio (presente/ausente): ").lower()
        novo_bomba = input("Novo estado da bomba (on/off): ").lower()

        conn, cursor = conectar_db()
        if conn:
            cursor.execute("""
                UPDATE leituras_sensores
                SET umidade = :1, temperatura = :2, ph = :3, fosforo = :4, potassio = :5, bomba_dagua = :6
                WHERE timestamp = :7
            """, (nova_umidade, nova_temperatura, novo_ph, novo_fosforo, novo_potassio, novo_bomba, timestamp))
            if cursor.rowcount:
                conn.commit()
                print("✅ Leitura atualizada com sucesso.")
            else:
                print("⚠️ Nenhuma leitura encontrada com esse timestamp.")
    except ValueError:
        print("❌ Erro: valores numéricos inválidos.")
    finally:
        if conn:
            cursor.close()
            conn.close()

# === REMOVE UMA LEITURA PELO TIMESTAMP ===
def remover_dado():
    print("\n🗑️ Remover leitura:")
    timestamp = input("Timestamp da leitura a remover: ")
    conn, cursor = conectar_db()
    if conn:
        cursor.execute("DELETE FROM leituras_sensores WHERE timestamp = :1", (timestamp,))
        if cursor.rowcount:
            conn.commit()
            print("✅ Leitura removida com sucesso.")
        else:
            print("⚠️ Nenhuma leitura encontrada com esse timestamp.")
        cursor.close()
        conn.close()

# === CONSULTA POR UMIDADE ACIMA/ABAIXO DE UM VALOR ===
def consultar_por_umidade():
    print("\n🔎 Consulta por umidade:")
    try:
        limite = float(input("Digite o valor de referência (%): "))
        condicao = input("Deseja ver valores 'acima' ou 'abaixo' desse valor? ").strip().lower()

        if condicao not in ['acima', 'abaixo']:
            print("❌ Condição inválida. Use 'acima' ou 'abaixo'.")
            return

        conn, cursor = conectar_db()
        if conn:
            if condicao == 'acima':
                cursor.execute("SELECT * FROM leituras_sensores WHERE umidade > :1 ORDER BY timestamp DESC", (limite,))
            else:
                cursor.execute("SELECT * FROM leituras_sensores WHERE umidade < :1 ORDER BY timestamp DESC", (limite,))
            
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("⚠️ Nenhuma leitura encontrada com esse critério.")
            cursor.close()
            conn.close()
    except ValueError:
        print("❌ Valor de umidade inválido.")

# === MENU DO SISTEMA ===
def menu():
    while True:
        print("""
================ MENU CRUD - BANCO ORACLE ================
1 - Inserir nova leitura manualmente
2 - Listar todas as leituras enviadas pelo ESP32
3 - Atualizar uma leitura manualmente
4 - Remover uma leitura do banco de dados
5 - Excluir todos os dados do banco de dados
6 - Consultar leituras por umidade (acima/abaixo)
0 - Sair
===========================================================
        """)
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            inserir_dados()
        elif opcao == '2':
            listar_dados()
        elif opcao == '3':
            atualizar_dado()
        elif opcao == '4':
            remover_dado()
        elif opcao == '5':
            conn, cursor = conectar_db()
            if conn:
                confirm = input("Tem certeza que deseja apagar todos os dados? (s/n): ").lower()
                if confirm == 's':
                    cursor.execute("DELETE FROM leituras_sensores")
                    conn.commit()
                    print("🧹 Todos os dados foram apagados.")
                cursor.close()
                conn.close()
        elif opcao == '6':
            consultar_por_umidade()
        elif opcao == '0':
            print("👋 Encerrando o programa. Até logo!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    menu()
