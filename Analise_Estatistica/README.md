# Análise Estatística e Preditiva – FarmTech Solutions

Esta pasta contém a análise estatística e preditiva realizada com R, usando os dados coletados pelo sistema de sensores e armazenados no banco Oracle. A proposta é extrair insights sobre umidade, temperatura, pH e o impacto da bomba de irrigação, além de prever o comportamento futuro da umidade com base em modelos de séries temporais.

---

## Arquivos principais:

- `analise_sensores_farmtech.R`: Script de análise estatística e previsão com ARIMA
- `analise_farmtech.Rmd`: Relatório RMarkdown para knit em HTML ou PDF
- `leituras_sensores.csv`: Base de dados exportada do Oracle
- `resumo_estatistico.csv`: Export gerado com as estatísticas descritivas

---

## Técnicas aplicadas:

- Estatística descritiva (média, desvio padrão, boxplots)
- Visualização de dados com `ggplot2`
- Modelagem de séries temporais (`ts`, `auto.arima`)
- Previsão de umidade para as próximas 24 leituras

---

## Objetivo:

Demonstrar como a estatística pode enriquecer sistemas de agricultura digital, gerando decisões mais inteligentes sobre irrigação. Com base em dados históricos e sensoriais, é possível:

- Detectar padrões de comportamento do solo
- Antecipar o momento ideal de irrigação
- Avaliar o efeito de variáveis como chuva ou temperatura

---

## Requisitos (R):

Instale os pacotes antes de executar:

```r
install.packages(c("readr", "dplyr", "ggplot2", "lubridate", "forecast"))
```

---

## Execução sugerida:

1. Exporte os dados com `exporta_oracle_para_csv.py`
2. Abra `analise_farmtech.Rmd` no RStudio
3. Clique em **Knit → HTML**
4. Veja os gráficos e insights automaticamente

---

Grupo 58 – FIAP  
Projeto Integrador Fase 3 | Inteligência Artificial

