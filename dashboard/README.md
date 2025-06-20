# FarmTech Solutions - Fase 4

## Visão Geral do Projeto

Nesta quarta fase do projeto FarmTech Solutions, a aplicação de irrigação inteligente foi aprimorada com a incorporação de análise de dados avançada e Machine Learning. O sistema agora utiliza um dashboard interativo construído com **Streamlit**, um modelo preditivo com **Scikit-learn** para otimizar o uso da água, e uma suíte de análise estatística com **R**. Além disso, a simulação no Wokwi foi aprimorada com a inclusão de um display LCD, permitindo o monitoramento local dos dados. Também foram realizadas otimizações no uso de memória do ESP32 e a utilização do Serial Plotter para análise dos dados em tempo real, proporcionando maior eficiência e melhor visualização dos resultados.
---

## Grupo 65 - FIAP

**Integrantes:**
- Felipe Sabino da Silva
- Juan Felipe Voltolini
- Luiz Henrique Ribeiro de Oliveira
- Marco Aurélio Eberhardt Assimpção
- Paulo Henrique Senise

**Professores:**
- Tutor: Leonardo Ruiz Orabona
- Coordenador: André Godoi

---

## Funcionalidades Principais

-   **Dashboard Interativo (Streamlit):** Uma interface moderna para visualização de dados em tempo real, incluindo métricas de sensores, gráficos históricos e recomendações do modelo de IA.
-   **Machine Learning (Scikit-learn):** Um modelo de `Random Forest` que prevê a necessidade de irrigação com base em dados históricos e meteorológicos, oferecendo um sistema de recomendação inteligente.
-   **Análise Estatística com R:** Geração de relatórios estatísticos detalhados em formatos **PDF** e **CSV**, com gráficos e resumos quantitativos.
-   **Simulação no Wokwi:** O ESP32 agora exibe dados críticos (umidade, status) em um **display LCD I2C**, oferecendo feedback visual direto no hardware.
-   **Monitoramento com Serial Plotter:** Análise visual e em tempo real de variáveis como a umidade do solo, diretamente da simulação do Wokwi.
-   **Banco de Dados PostgreSQL:** Persistência de todos os dados coletados para análise histórica e treinamento dos modelos.

---

## Tecnologias Utilizadas

-   **Python 3.10+**
-   **Streamlit:** Para o dashboard interativo.
-   **Scikit-learn:** Para o modelo preditivo de Machine Learning.
-   **R:** Para análises estatísticas e geração de relatórios.
-   **Pandas:** Para manipulação de dados.
-   **Plotly:** Para a criação de gráficos.
-   **PostgreSQL:** Como banco de dados.
-   **Wokwi:** Para simulação do hardware (ESP32, sensores, display LCD).
-   **Flask:** Como servidor local para receber dados do ESP32.

---

## Como Executar o Projeto

**1. Pré-requisitos:**
-   Ter o **Python 3.10+** e o **R** instalados.
-   Instalar as dependências do projeto:
    ```bash
    pip install -r requirements.txt
    ```

**2. Servidor Local:**
-   Para receber os dados do ESP32, inicie o servidor Flask:
    ```bash
    python Servidor_Local/serve.py
    ```

**3. Dashboard Streamlit:**
-   Execute o dashboard com o seguinte comando:
    ```bash
    streamlit run dashboard/dashboard_streamlit.py
    ```
-   Acesse a aplicação em seu navegador no endereço `http://localhost:8501`.

---

## Como Gerar Relatórios com R

O dashboard permite gerar relatórios estatísticos em formato CSV e PDF utilizando a integração com a linguagem R. Siga os passos abaixo:

1.  **Acesse a Análise R**
    - Com o dashboard em execução, clique no botão **"Análise R"**.

2.  **Execute o Script**
    - Na tela de análise, selecione a opção **"Executar Análise Estatística Completa"** no menu suspenso.
    - Clique no botão **"2. Executar Script R"**.

3.  **Configurando o Caminho do R (se necessário)**
    - Se o R não estiver configurado no PATH do seu sistema, o dashboard solicitará que você insira o caminho para a pasta `bin` da sua instalação do R.
    - **Para encontrar o caminho no Windows:**
        - Navegue até `C:\Program Files\R`.
        - Entre na pasta correspondente à sua versão do R (ex: `R-4.4.3`).
        - Dentro dela, entre na pasta `bin`.
        - Copie o caminho completo da barra de endereço do Windows Explorer.

    - **Exemplo de caminho no Windows:**
    ```
    C:\Program Files\R\R-4.4.3\bin
    ```

    - Cole este caminho no campo de texto que apareceu no dashboard e clique em **"Salvar caminho e tentar novamente"**.

4.  **Baixe os Relatórios**
    - Após a execução bem-sucedida do script, os botões **"Baixar Relatório PDF"** e **"Baixar Resumo CSV"** aparecerão na tela, permitindo que você salve os arquivos gerados.

---

## Demonstrações

### Dashboard Principal
*(Insira aqui um print da tela principal do dashboard Streamlit)*
![placeholder](https://via.placeholder.com/800x400.png?text=Print+do+Dashboard+Principal)

### Análise de Machine Learning
*(Insira aqui um print da seção de Machine Learning, mostrando a acurácia e a matriz de confusão)*
![placeholder](https://via.placeholder.com/800x400.png?text=Print+da+Análise+de+Machine+Learning)

### Análise em R
*(Insira aqui um print da seção de Análise R, mostrando os botões de download dos relatórios)*
![placeholder](https://via.placeholder.com/800x400.png?text=Print+da+Análise+em+R)

### Simulação no Wokwi com Display LCD
*(Insira aqui um print da simulação no Wokwi, destacando o display LCD em funcionamento)*
![placeholder](https://via.placeholder.com/800x400.png?text=Print+do+Wokwi+com+Display+LCD)

### Gráfico do Serial Plotter
*(Insira aqui um print do Serial Plotter do Wokwi monitorando a umidade ou outra variável)*
![placeholder](https://via.placeholder.com/800x400.png?text=Print+do+Serial+Plotter)

---

## Vídeo de Demonstração

Assista ao vídeo de apresentação do projeto no YouTube:

**(Insira aqui o link do seu vídeo não listado do YouTube)**

---
