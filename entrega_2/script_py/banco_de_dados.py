from datetime import datetime

dados_irrigacao = []

def inserir_dados(timestamp, umidade, ph, fosforo_presente, potassio_presente, rele_ligado):
    """Adiciona uma nova leitura de dados de irrigação com um timestamp fornecido."""
    nova_leitura = {
        "timestamp": timestamp,
        "umidade": umidade,
        "ph": ph,
        "fosforo_presente": fosforo_presente,
        "potassio_presente": potassio_presente,
        "rele_ligado": rele_ligado
    }
    dados_irrigacao.append(nova_leitura)
    print("Dados inseridos com sucesso!")

def listar_dados():
    """Lista todos os dados armazenados."""
    if not dados_irrigacao:
        print("Não há dados de irrigação armazenados.")
    else:
        print("\n--- Todas as Leituras de Irrigação ---")
        for i, leitura in enumerate(dados_irrigacao):
            print(f"Leitura {i+1}: {leitura}")

def buscar_por_umidade_acima_de(umidade_limite):
    """Busca leituras com umidade acima do limite especificado."""
    resultados = [leitura for leitura in dados_irrigacao if leitura["umidade"] > umidade_limite]
    if not resultados:
        print(f"Não foram encontradas leituras com umidade acima de {umidade_limite}%.")
    else:
        print(f"\n--- Leituras com umidade acima de {umidade_limite}% ---")
        for i, leitura in enumerate(resultados):
            print(f"Leitura {i+1}: {leitura}")

def exibir_menu():
    print("\n--- Menu de Operações CRUD ---")
    print("1 - Inserir Nova Leitura")
    print("2 - Listar Todas as Leituras")
    print("3 - Buscar Leituras por Umidade Acima De (%)")
    print("4 - Atualizar Leitura (em breve)")
    print("5 - Remover Leitura (em breve)")
    print("0 - Sair")

def main():
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            timestamp_str = input("Digite a data e hora da coleta (AAAA-MM-DD HH:MM:SS): ")
            try:
                # Tenta converter a string para um objeto datetime para validar o formato
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
            print("Funcionalidade de atualização será implementada em breve.")
        elif opcao == '5':
            print("Funcionalidade de remoção será implementada em breve.")
        elif opcao == '0':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()