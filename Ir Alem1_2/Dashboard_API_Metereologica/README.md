## Ir Além 1: Dashboard em Python para Visualização dos Dados

### Objetivo

Desenvolvimento de um dashboard interativo em Python para apresentar de forma clara e compreensível os dados coletados do sistema de irrigação simulado e dos sensores. O dashboard visa facilitar o entendimento do funcionamento do sistema, exibindo informações cruciais como níveis de umidade, estado da bomba, pH e nutrientes (P e K) através de visualizações intuitivas.

### Bibliotecas Utilizadas

Para a criação do dashboard, utilizamos a biblioteca **Dash** em Python. **Dash foi escolhido por sua capacidade de criar aplicativos web interativos com componentes visuais.**

### Funcionalidades do Dashboard

O dashboard implementado apresenta as seguintes visualizações:
* **Gráfico de Umidade do Solo:** Exibe a variação da umidade do solo ao longo do tempo, permitindo identificar padrões e necessidades de irrigação.
* **Gráfico de Estado do Relé (Bomba):** Indica os momentos em que a bomba de irrigação foi ativada (ON) e desativada (OFF), correlacionando com outros dados.
* **Gráfico de pH:** Mostra a simulação das leituras de pH ao longo do tempo.
* **Gráfico de Nutrientes (P e K):** Apresenta o estado (presença/ausência simulada) dos nutrientes Fósforo e Potássio. 
* **Tabela de Dados em Tempo Real:** Exibe os valores mais recentes de todos os sensores em formato tabular para uma visão detalhada.
* **Condições Climáticas Atuais:** Mostra as condições climáticas atuais (temperatura, umidade, vento, etc.) obtidas através de uma API.
* **Previsão de Chuva:** Exibe a previsão de chuva para as próximas horas, auxiliando na decisão de irrigar ou não.
* **Aviso de Desligamento da Bomba:** Apresenta um alerta visual quando há previsão de chuva, indicando que a bomba deve ser desligada.

### Integração com Dados

Os dados exibidos no dashboard são integrados diretamente do monitor serial (para simulação), de um arquivo CSV simulado, ou (se já implementado) de um banco de dados SQL]. 

### Atualizações e Simulações

Os dados são atualizados automaticamente a cada segundo.

### Capturas de Tela do Dashboard
![DashBoardCompletoeFuncionando](https://github.com/user-attachments/assets/a50a58ca-055b-48bd-b303-c76cdc0c4fba)

As capturas de tela acima ilustram a interface e as visualizações implementadas no dashboard.


## Ir Além 2: Integração Python com API Pública

### Objetivo

Criar uma integração entre o sistema de irrigação e uma fonte de dados meteorológicos reais utilizando uma API pública. Essa integração permite que o código Python busque informações diretamente de um site que oferece dados sobre o clima em tempo real (como temperatura, umidade e previsão de chuva). Esses dados externos auxiliam o sistema a decidir de maneira mais inteligente se a bomba de irrigação deve ser ligada ou não. Por exemplo, se a previsão mostrar que vai chover nas próximas horas, o sistema pode evitar o desperdício de água, mantendo a bomba desligada.

### API Utilizada

Foi escolhida a **API OpenWeatherMap** ([(https://api.openweathermap.org/data/2.5/weather?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br)]). 
Essa API fornece dados climáticos em tempo real e previsões para diversas localidades.

### Implementação

1.  **Requisição à API:** O código Python realiza uma requisição à **API OpenWeatherMap** para obter dados climáticos atuais e/ou previsão de chuva para Localidade, Porto Alegre.
2.  **Processamento dos Dados:** Os dados recebidos da API são processados para extrair as informações relevantes (ex: temperatura, umidade, previsão de chuva).
3.  **Lógica Condicional para Irrigação:** Foi implementada a seguinte lógica condicional para controlar a bomba de irrigação:

    * Se houver previsão de chuva nas próximas 12 horas, a bomba é desligada.
    * Se a umidade atual for superior a 40%, a bomba é desligada, mesmo que não haja previsão de chuva.
    * Se a temperatura for muito baixa (abaixo de 18°C), a bomba é desligada para evitar danos às plantas.

    ### Lógica Condicional para Irrigação Baseada em Dados Meteorológicos

A decisão de controlar a bomba de irrigação é influenciada pelos dados meteorológicos obtidos através da **API OpenWeatherMap**. Especificamente, o sistema analisa a [Parâmetro da previsão utilizado, previsão de chuva para as próximas 12 horas para determinar se a irrigação deve ser ativada ou desativada.

A seguinte lógica condicional foi implementada:

* **Condição de Desligamento por Previsão de Chuva:**
    * Se a previsão de chuva para as próximas 12 horas indicar Limiar ou condição para chuva, o sistema impede que a bomba seja ligada, ou seja, desliga a bomba caso esteja em funcionamento.

A implementação desta lógica visa otimizar o uso da água, evitando a irrigação desnecessária em períodos de chuva previstos e garantindo que a irrigação ocorra quando necessário, mesmo com previsões de chuva leve, considerando a umidade atual do solo.

### Código Python (Trecho Exemplo)

```python
# Exemplo de como obter e processar os dados da API
import requests

API_KEY = "CHAVE_DA_API"
CITY = "Porto Alegre"  # Ou a localidade desejada

url_atual = f"https://api.openweathermap.org/data/2.5/weather?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br"
url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br&cnt=4" # Previsão para 3 em 3 horas (próximas 12 horas)

try:
        response_atual = requests.get(url_atual)
        response_atual.raise_for_status()
        data_atual = response_atual.json()

        response_previsao = requests.get(url_previsao)
        response_previsao.raise_for_status()
        data_previsao = response_previsao.json()

        return {"atual": data_atual, "previsao": data_previsao}
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados meteorológicos: {e}")
        return None

# Lógica para verificar a previsão de chuva e exibir o aviso de desligar a bomba
        aviso_desligar = ""
        if weather_data and weather_data['previsao'] and 'list' in weather_data['previsao']:
            for item in weather_data['previsao']['list']:
                # Verifica se há indicação de chuva na previsão
                if 'rain' in item and item['rain'].get('3h', 0) > 0:
                    aviso_desligar = html.Div(
                        children="⚠️ AVISO: Previsão de chuva! A bomba de irrigação deve ser DESLIGADA.",
                        style={'color': 'white', 'backgroundColor': '#dc3545', 'padding': '10px', 'borderRadius': '5px'}
                    )
                    break
                elif 'weather' in item:
                    for condition in item['weather']:
                        if 'chuva' in condition['description'].lower():
                            aviso_desligar = html.Div(
                                children="⚠️ AVISO: Previsão de chuva! A bomba de irrigação deve ser DESLIGADA.",
                                style={'color': 'white', 'backgroundColor': '#dc3545', 'padding': '10px', 'borderRadius': '5px'}
                            )
                            break
                    if aviso_desligar:
                        break

### Considerações Finais
O dashboard desenvolvido em Python oferece uma maneira intuitiva de monitorar e analisar os dados do sistema de irrigação simulado, facilitando a compreensão do seu funcionamento e auxiliando em futuras decisões sobre o manejo da água e sua economia.
