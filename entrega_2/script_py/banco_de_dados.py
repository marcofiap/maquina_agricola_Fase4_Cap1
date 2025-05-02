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
    """Lista todos os dados armazenados com seus índices."""
    if not dados_irrigacao:
        print("Não há dados de irrigação armazenados.")
        return False
    else:
        print("\n--- Todas as Leituras de Irrigação ---")
        for i, leitura in enumerate(dados_irrigacao):
            print(f"Índice {i}: {leitura}")
        return True

def buscar_por_umidade_acima_de(umidade_limite):
    """Busca leituras com umidade acima do limite especificado."""
    resultados = [leitura for leitura in dados_irrigacao if leitura["umidade"] > umidade_limite]
    if not resultados:
        print(f"Não foram encontradas leituras com umidade acima de {umidade_limite}%.")
    else:
        print(f"\n--- Leituras com umidade acima de {umidade_limite}% ---")
        for i, leitura in enumerate(resultados):
            print(f"Leitura {i+1}: {leitura}")

def atualizar_leitura(indice, novo_timestamp, nova_umidade, novo_ph, novo_fosforo, novo_potassio, novo_rele):
    """Atualiza uma leitura existente no índice especificado."""
    if 0 <= indice < len(dados_irrigacao):
        dados_irrigacao[indice]["timestamp"] = novo_timestamp
        dados_irrigacao[indice]["umidade"] = nova_umidade
        dados_irrigacao[indice]["ph"] = novo_ph
        dados_irrigacao[indice]["fosforo_presente"] = novo_fosforo
        dados_irrigacao[indice]["potassio_presente"] = novo_potassio
        dados_irrigacao[indice]["rele_ligado"] = novo_rele
        print(f"Leitura com índice {indice} atualizada com sucesso!")
    else:
        print(f"Erro: Índice {indice} inválido.")

def remover_leitura(indice):
    """Remove a leitura no índice especificado."""
    if 0 <= indice < len(dados_irrigacao):
        leitura_removida = dados_irrigacao.pop(indice)
        print(f"Leitura com índice {indice} (timestamp: {leitura_removida['timestamp']}) removida com sucesso!")
    else:
        print(f"Erro: Índice {indice} inválido.")

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
            if listar_dados():
                try:
                    indice_atualizar = int(input("Digite o índice da leitura que deseja atualizar: "))
                    if 0 <= indice_atualizar < len(dados_irrigacao):
                        novo_timestamp = input("Digite a nova data e hora da coleta (AAAA-MM-DD HH:MM:SS): ")
                        datetime.strptime(novo_timestamp, "%Y-%m-%d %H:%M:%S")
                        nova_umidade = float(input("Digite a nova umidade (%): "))
                        novo_ph = float(input("Digite o novo pH (0-14): "))
                        novo_fosforo = input("Novo fósforo presente? (True/False): ").lower() == 'true'
                        novo_potassio = input("Novo potássio presente? (True/False): ").lower() == 'true'
                        novo_rele = input("Novo relé ligado? (True/False): ").lower() == 'true'
                        atualizar_leitura(indice_atualizar, novo_timestamp, nova_umidade, novo_ph, novo_fosforo, novo_potassio, novo_rele)
                    else:
                        print("Erro: Índice inválido.")
                except ValueError:
                    print("Erro: Por favor, digite um índice válido e valores nos formatos corretos.")
            else:
                print("Não há leituras para atualizar.")
        elif opcao == '5':
            if listar_dados():
                try:
                    indice_remover = int(input("Digite o índice da leitura que deseja remover: "))
                    remover_leitura(indice_remover)
                except ValueError:
                    print("Erro: Por favor, digite um índice válido.")
            else:
                print("Não há leituras para remover.")
        elif opcao == '0':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()