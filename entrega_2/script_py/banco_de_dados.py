import sqlite3
from datetime import datetime

DATABASE_NAME = 'irrigacao.db'

def conectar_db():
    """Conecta ao banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    return conn, cursor

def criar_tabela():
    """Cria a tabela 'leituras_sensores' se ela não existir."""
    conn, cursor = conectar_db()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leituras_sensores (
            timestamp TEXT PRIMARY KEY,
            umidade REAL,
            ph REAL,
            fosforo_presente BOOLEAN,
            potassio_presente BOOLEAN,
            rele_ligado BOOLEAN
        )
    """)
    conn.commit()
    conn.close()

criar_tabela()

def inserir_dados(timestamp, umidade, ph, fosforo_presente, potassio_presente, rele_ligado):
    """Insere uma nova leitura de dados na tabela 'leituras_sensores'."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("""
            INSERT INTO leituras_sensores (timestamp, umidade, ph, fosforo_presente, potassio_presente, rele_ligado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, umidade, ph, fosforo_presente, potassio_presente, rele_ligado))
        conn.commit()
        print("Dados inseridos com sucesso!")
    except sqlite3.IntegrityError:
        print(f"Erro: Já existe uma leitura com o timestamp {timestamp}.")
    finally:
        conn.close()

def listar_dados():
    """Lista todas as leituras da tabela 'leituras_sensores'."""
    conn, cursor = conectar_db()
    cursor.execute("SELECT * FROM leituras_sensores")
    registros = cursor.fetchall()
    conn.close()

    if not registros:
        print("Não há dados de irrigação armazenados.")
        return False
    else:
        print("\n--- Todas as Leituras de Irrigação ---")
        for registro in registros:
            print(f"Timestamp: {registro[0]}, Umidade: {registro[1]}%, pH: {registro[2]}, Fósforo: {registro[3]}, Potássio: {registro[4]}, Relé: {registro[5]}")
        return True

def buscar_por_umidade_acima_de(umidade_limite):
    """Busca leituras na tabela com umidade acima do limite especificado."""
    conn, cursor = conectar_db()
    cursor.execute("SELECT * FROM leituras_sensores WHERE umidade > ?", (umidade_limite,))
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print(f"Não foram encontradas leituras com umidade acima de {umidade_limite}%.")
    else:
        print(f"\n--- Leituras com umidade acima de {umidade_limite}% ---")
        for registro in resultados:
            print(f"Timestamp: {registro[0]}, Umidade: {registro[1]}%, pH: {registro[2]}, Fósforo: {registro[3]}, Potássio: {registro[4]}, Relé: {registro[5]}")

def atualizar_leitura(timestamp_atual, nova_umidade, novo_ph, novo_fosforo, novo_potassio, novo_rele):
    """Atualiza uma leitura existente na tabela com base no timestamp."""
    conn, cursor = conectar_db()
    cursor.execute("""
        UPDATE leituras_sensores
        SET umidade = ?, ph = ?, fosforo_presente = ?, potassio_presente = ?, rele_ligado = ?
        WHERE timestamp = ?
    """, (nova_umidade, novo_ph, novo_fosforo, novo_potassio, novo_rele, timestamp_atual))
    conn.commit()
    linhas_afetadas = cursor.rowcount
    conn.close()

    if linhas_afetadas > 0:
        print(f"Leitura com timestamp {timestamp_atual} atualizada com sucesso!")
    else:
        print(f"Erro: Não foi encontrada nenhuma leitura com o timestamp {timestamp_atual}.")

def remover_leitura(timestamp_remover):
    """Remove uma leitura da tabela com base no timestamp."""
    conn, cursor = conectar_db()
    cursor.execute("DELETE FROM leituras_sensores WHERE timestamp = ?", (timestamp_remover,))
    conn.commit()
    linhas_afetadas = cursor.rowcount
    conn.close()

    if linhas_afetadas > 0:
        print(f"Leitura com timestamp {timestamp_remover} removida com sucesso!")
    else:
        print(f"Erro: Não foi encontrada nenhuma leitura com o timestamp {timestamp_remover}.")

def exibir_menu():
    print("""
    ---------------------------
        Menu de Operações CRUD
       Dados da Máquina Agrícola
    ---------------------------
    """)
    print("1 - Inserir Nova Leitura")
    print("2 - Listar Todas as Leituras")
    print("3 - Buscar Leituras por Umidade Acima De")
    print("4 - Atualizar Leitura")
    print("5 - Remover Leitura")
    print("0 - Sair")

def main():
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            timestamp_str = input("Digite a data e hora da coleta (AAAA-MM-DD HH:MM:SS): ")
            try:
                datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                umidade = float(input("Digite a umidade (%): "))
                ph = float(input("Digite o pH (0-14): "))
                fosforo = input("Fósforo presente? (True/False): ").lower() == 'true'
                potassio = input("Potássio presente? (True/False): ").lower() == 'true'
                rele = input("Relé ligado? (True/False): ").lower() == 'true'
                inserir_dados(timestamp_str, umidade, ph, fosforo, potassio, rele)
            except ValueError:
                print("Erro: Formato de data e hora inválido ou valor numérico incorreto.")
        elif opcao == '2':
            listar_dados()
        elif opcao == '3':
            try:
                limite = float(input("Digite o limite de umidade (%): "))
                buscar_por_umidade_acima_de(limite)
            except ValueError:
                print("Erro: Por favor, digite um valor numérico para o limite de umidade.")
        elif opcao == '4':
            listar_dados()
            timestamp_atualizar = input("Digite o timestamp da leitura que deseja atualizar: ")
            nova_umidade = float(input("Digite a nova umidade (%): "))
            novo_ph = float(input("Digite o novo pH (0-14): "))
            novo_fosforo = input("Novo fósforo presente? (True/False): ").lower() == 'true'
            novo_potassio = input("Novo potássio presente? (True/False): ").lower() == 'true'
            novo_rele = input("Novo relé ligado? (True/False): ").lower() == 'true'
            atualizar_leitura(timestamp_atualizar, nova_umidade, novo_ph, novo_fosforo, novo_potassio, novo_rele)
        elif opcao == '5':
            listar_dados()
            timestamp_remover = input("Digite o timestamp da leitura que deseja remover: ")
            remover_leitura(timestamp_remover)
        elif opcao == '0':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()