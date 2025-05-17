## Ir Além 1: Dashboard em Python para Visualização dos Dados

### Objetivo

Desenvolvimento de um dashboard interativo em Python para apresentar de forma clara e compreensível os dados coletados do sistema de irrigação simulado e dos sensores. O dashboard visa facilitar o entendimento do funcionamento do sistema, exibindo informações cruciais como níveis de umidade, estado da bomba, pH e nutrientes (P e K) através de visualizações intuitivas.

### Bibliotecas Utilizadas

Para a criação do dashboard, utilizamos a biblioteca [Nome da Biblioteca Utilizada, ex: Dash] em Python. [Opcional: Explique brevemente o motivo da escolha da biblioteca, ex: Dash foi escolhido por sua capacidade de criar aplicativos web interativos com componentes visuais.]

### Funcionalidades do Dashboard

O dashboard implementado apresenta as seguintes visualizações:
* **Gráfico de Umidade do Solo:** Exibe a variação da umidade do solo ao longo do tempo, permitindo identificar padrões e necessidades de irrigação.
* **Gráfico de Estado do Relé (Bomba):** Indica os momentos em que a bomba de irrigação foi ativada (ON) e desativada (OFF), correlacionando com outros dados.
* **Gráfico de pH:** Mostra a simulação das leituras de pH ao longo do tempo.
* **Gráfico de Nutrientes (P e K):** Apresenta o estado (presença/ausência simulada) dos nutrientes Fósforo e Potássio. [Opcional: Se você representou isso de alguma forma visual no gráfico, explique.]
* **Tabela de Dados em Tempo Real:** Exibe os valores mais recentes de todos os sensores em formato tabular para uma visão detalhada.
* **Condições Climáticas Atuais:** [Se implementado] Mostra as condições climáticas atuais (temperatura, umidade, vento, etc.) obtidas através de uma API.
* **Previsão de Chuva:** [Se implementado] Exibe a previsão de chuva para as próximas horas, auxiliando na decisão de irrigar ou não.
* **Aviso de Desligamento da Bomba:** [Se implementado] Apresenta um alerta visual quando há previsão de chuva, indicando que a bomba deve ser desligada.

### Integração com Dados

Os dados exibidos no dashboard são integrados [Como os dados são integrados? Ex: diretamente do monitor serial (para simulação), de um arquivo CSV simulado, ou (se já implementado) de um banco de dados SQL]. [Se você simulou dados, explique brevemente como essa simulação foi feita.]

### Atualizações e Simulações

[Explique como o dashboard é atualizado. Ex: Os dados são atualizados automaticamente a cada X segundos, ou é necessário recarregar a página? Se você implementou alguma forma de simulação (ex: permitir alterar valores de sensores), explique aqui.]

### Capturas de Tela do Dashboard
![DashBoardCompletoeFuncionando](https://github.com/user-attachments/assets/59284969-1e00-42cb-8b19-92bf3b870ade)

As capturas de tela acima ilustram a interface e as visualizações implementadas no dashboard.

### Considerações Finais
O dashboard desenvolvido em Python oferece uma maneira intuitiva de monitorar e analisar os dados do sistema de irrigação simulado, facilitando a compreensão do seu funcionamento e auxiliando em futuras decisões sobre o manejo da água.
