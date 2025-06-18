import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path para importar o config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.database_config import DatabaseConfig, conectar_postgres

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

        conn, cursor = conectar_postgres()
        if conn:
            cursor.execute(f"""
                INSERT INTO {DatabaseConfig.SCHEMA}.leituras_sensores (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba_dagua)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (timestamp, umidade, temperatura, ph, fosforo, potassio, bomba))
            conn.commit()
            print("✅ Dados inseridos com sucesso.")
    except ValueError:
        print("❌ Erro: valores numéricos inválidos.")
    except Exception as e:
        print("❌ Erro ao inserir:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()

# === LISTA TODAS AS LEITURAS ===
def listar_dados():
    print("\n📄 Listando dados...")
    conn, cursor = conectar_postgres()
    if conn:
        cursor.execute(f"SELECT * FROM {DatabaseConfig.SCHEMA}.leituras_sensores ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        if rows:
            print(f"\n{'='*80}")
            print(f"{'TIMESTAMP':<20} {'UMID':<6} {'TEMP':<6} {'PH':<6} {'FÓSF':<8} {'POT':<8} {'BOMBA':<8}")
            print(f"{'='*80}")
            for row in rows:
                print(f"{str(row[0]):<20} {row[1]:<6} {row[2]:<6} {row[3]:<6} {row[4]:<8} {row[5]:<8} {row[6]:<8}")
            print(f"{'='*80}")
            print(f"Total de registros: {len(rows)}")
        else:
            print("⚠️ Nenhum dado encontrado.")
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

        conn, cursor = conectar_postgres()
        if conn:
            cursor.execute(f"""
                UPDATE {DatabaseConfig.SCHEMA}.leituras_sensores
                SET umidade = %s, temperatura = %s, ph = %s, fosforo = %s, potassio = %s, bomba_dagua = %s
                WHERE timestamp = %s
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
    conn, cursor = conectar_postgres()
    if conn:
        cursor.execute(f"DELETE FROM {DatabaseConfig.SCHEMA}.leituras_sensores WHERE timestamp = %s", (timestamp,))
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

        conn, cursor = conectar_postgres()
        if conn:
            if condicao == 'acima':
                cursor.execute(f"SELECT * FROM {DatabaseConfig.SCHEMA}.leituras_sensores WHERE umidade > %s ORDER BY timestamp DESC", (limite,))
            else:
                cursor.execute(f"SELECT * FROM {DatabaseConfig.SCHEMA}.leituras_sensores WHERE umidade < %s ORDER BY timestamp DESC", (limite,))
            
            rows = cursor.fetchall()
            if rows:
                print(f"\n🔍 Leituras com umidade {condicao} de {limite}%:")
                print(f"{'='*80}")
                print(f"{'TIMESTAMP':<20} {'UMID':<6} {'TEMP':<6} {'PH':<6} {'FÓSF':<8} {'POT':<8} {'BOMBA':<8}")
                print(f"{'='*80}")
                for row in rows:
                    print(f"{str(row[0]):<20} {row[1]:<6} {row[2]:<6} {row[3]:<6} {row[4]:<8} {row[5]:<8} {row[6]:<8}")
                print(f"{'='*80}")
                print(f"Total encontrado: {len(rows)} registros")
            else:
                print("⚠️ Nenhuma leitura encontrada com esse critério.")
            cursor.close()
            conn.close()
    except ValueError:
        print("❌ Valor de umidade inválido.")

# === ESTATÍSTICAS DOS DADOS ===
def mostrar_estatisticas():
    print("\n📊 Estatísticas dos dados:")
    conn, cursor = conectar_postgres()
    if conn:
        try:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_registros,
                    AVG(umidade) as umidade_media,
                    MIN(umidade) as umidade_min,
                    MAX(umidade) as umidade_max,
                    AVG(temperatura) as temp_media,
                    MIN(temperatura) as temp_min,
                    MAX(temperatura) as temp_max,
                    AVG(ph) as ph_medio,
                    MIN(ph) as ph_min,
                    MAX(ph) as ph_max
                FROM {DatabaseConfig.SCHEMA}.leituras_sensores
            """)
            stats = cursor.fetchone()
            
            if stats and stats[0] > 0:
                print(f"{'='*60}")
                print(f"📈 ESTATÍSTICAS GERAIS")
                print(f"{'='*60}")
                print(f"Total de registros: {stats[0]}")
                print(f"")
                print(f"💧 UMIDADE:")
                print(f"   Média: {stats[1]:.1f}%")
                print(f"   Mínima: {stats[2]:.1f}%")
                print(f"   Máxima: {stats[3]:.1f}%")
                print(f"")
                print(f"🌡️ TEMPERATURA:")
                print(f"   Média: {stats[4]:.1f}°C")
                print(f"   Mínima: {stats[5]:.1f}°C")
                print(f"   Máxima: {stats[6]:.1f}°C")
                print(f"")
                print(f"⚗️ pH:")
                print(f"   Médio: {stats[7]:.1f}")
                print(f"   Mínimo: {stats[8]:.1f}")
                print(f"   Máximo: {stats[9]:.1f}")
                print(f"{'='*60}")
            else:
                print("⚠️ Nenhum dado disponível para estatísticas.")
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas: {e}")
        finally:
            cursor.close()
            conn.close()

# === MENU DO SISTEMA ===
def menu():
    while True:
        print(f"""
================ MENU CRUD - BANCO POSTGRESQL ================
🏗️ Schema: {DatabaseConfig.SCHEMA}
🖥️ Host: {DatabaseConfig.HOST}
💾 Database: {DatabaseConfig.DATABASE}
===============================================================
1 - Inserir nova leitura manualmente
2 - Listar todas as leituras enviadas pelo ESP32
3 - Atualizar uma leitura manualmente
4 - Remover uma leitura do banco de dados
5 - Excluir todos os dados do banco de dados
6 - Consultar leituras por umidade (acima/abaixo)
7 - Mostrar estatísticas dos dados
8 - Testar conexão com o banco
0 - Sair
===============================================================
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
            conn, cursor = conectar_postgres()
            if conn:
                confirm = input("⚠️ ATENÇÃO: Tem certeza que deseja apagar TODOS os dados? (digite 'CONFIRMAR'): ")
                if confirm == 'CONFIRMAR':
                    cursor.execute(f"DELETE FROM {DatabaseConfig.SCHEMA}.leituras_sensores")
                    deleted_count = cursor.rowcount
                    conn.commit()
                    print(f"🧹 {deleted_count} registros foram apagados.")
                else:
                    print("❌ Operação cancelada.")
                cursor.close()
                conn.close()
        elif opcao == '6':
            consultar_por_umidade()
        elif opcao == '7':
            mostrar_estatisticas()
        elif opcao == '8':
            from config.database_config import testar_conexao
            testar_conexao()
        elif opcao == '0':
            print("👋 Encerrando o programa. Até logo!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    print("🚀 Farm Tech Solutions - CRUD PostgreSQL")
    print(f"📊 Usando configuração centralizada")
    print(f"🏗️ Schema: {DatabaseConfig.SCHEMA}")
    
    # Testa conexão inicial
    print("\n🔍 Testando conexão inicial...")
    conn, cursor = conectar_postgres()
    if conn:
        cursor.close()
        conn.close()
        menu()
    else:
        print("❌ Não foi possível conectar ao banco. Verifique as configurações.")
