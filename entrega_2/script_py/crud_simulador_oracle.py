import oracledb
from datetime import datetime

# Configurações do Oracle
DB_USER = "system"
DB_PASSWORD = "Sua_Senha"
DB_DSN = "localhost:1521/xe"

def conectar_db():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()
        return conn, cursor
    except oracledb.Error as error:
        print("Erro na conexão:", error)
        return None, None

def inserir_dados():
    timestamp = input("Timestamp (YYYY-MM-DD HH:MM:SS): ")
    umidade = float(input("Umidade (%): "))
    temperatura = float(input("Temperatura (°C): "))
    ph = float(input("pH: "))
    fosforo = input("Fósforo (presente/ausente): ")
    potassio = input("Potássio (presente/ausente): ")
    bomba = input("Bomba (on/off): ")

    conn, cursor = conectar_db()
    if conn:
        try:
            cursor.execute("""
                INSERT INTO leituras_sensores (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba))
            conn.commit()
            print("✅ Dados inseridos com sucesso.")
        except oracledb.Error as e:
            print("Erro ao inserir:", e)
        finally:
            cursor.close()
            conn.close()

def listar_dados():
    conn, cursor = conectar_db()
    if conn:
        cursor.execute("SELECT * FROM leituras_sensores ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        cursor.close()
        conn.close()

def atualizar_dado():
    timestamp = input("Timestamp da leitura que deseja atualizar: ")
    nova_umidade = float(input("Nova umidade (%): "))
    nova_temperatura = float(input("Nova temperatura (°C): "))
    novo_ph = float(input("Novo pH: "))
    novo_fosforo = input("Novo fósforo (presente/ausente): ")
    novo_potassio = input("Novo potássio (presente/ausente): ")
    novo_bomba = input("Novo estado da bomba (on/off): ")

    conn, cursor = conectar_db()
    if conn:
        cursor.execute("""
            UPDATE leituras_sensores
            SET umidade = :1, temperatura = :2, ph = :3, fosforo = :4, potassio = :5, bomba_dagua = :6
            WHERE timestamp = :7
        """, (nova_umidade, nova_temperatura, novo_ph, novo_fosforo, novo_potassio, novo_bomba, timestamp))
        if cursor.rowcount:
            conn.commit()
            print("✅ Leitura atualizada.")
        else:
            print("❌ Timestamp não encontrado.")
        cursor.close()
        conn.close()

def remover_dado():
    timestamp = input("Timestamp da leitura a remover: ")
    conn, cursor = conectar_db()
    if conn:
        cursor.execute("DELETE FROM leituras_sensores WHERE timestamp = :1", (timestamp,))
        if cursor.rowcount:
            conn.commit()
            print("✅ Leitura removida.")
        else:
            print("❌ Timestamp não encontrado.")
        cursor.close()
        conn.close()

def menu():
    while True:
        print("""
========= MENU CRUD =========
1 - Inserir nova leitura
2 - Listar todas as leituras
3 - Atualizar uma leitura
4 - Remover uma leitura
5 - Excluir todos os dados
0 - Sair
============================
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
                cursor.execute("DELETE FROM leituras_sensores")
                conn.commit()
                print("✅ Todos os dados foram apagados da tabela.")
                cursor.close()
                conn.close()
        elif opcao == '0':
            print("Encerrando.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
