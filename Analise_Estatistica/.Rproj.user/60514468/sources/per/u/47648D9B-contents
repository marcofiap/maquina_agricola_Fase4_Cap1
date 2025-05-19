# Análise Estatística de Dados de Sensores - FarmTech Solutions

# Pacotes necessários
library(dplyr)
library(ggplot2)
library(readr)
library(lubridate)
library(forecast)

# Carregar os dados exportados do banco Oracle (CSV simulado)
df <- read_csv("leituras_sensores.csv")

# Transformar coluna de timestamp em formato de data/hora
df$timestamp <- ymd_hms(df$timestamp)

# Resumo estatístico das variáveis
summary(df)

# Correlação entre variáveis
cor(df$umidade, df$ph, use = "complete.obs")

# Histograma da umidade
ggplot(df, aes(x = umidade)) +
  geom_histogram(binwidth = 2, fill = "skyblue", color = "black") +
  labs(title = "Distribuição da Umidade do Solo", x = "Umidade (%)", y = "Frequência")

# Boxplot de temperatura por status da bomba
ggplot(df, aes(x = bomba_dagua, y = temperatura, fill = bomba_dagua)) +
  geom_boxplot() +
  labs(title = "Temperatura vs Estado da Bomba", x = "Bomba", y = "Temperatura (°C)")

# Série temporal da umidade
df_ts <- df %>%
  arrange(timestamp) %>%
  select(timestamp, umidade)

serie_umidade <- ts(df_ts$umidade, frequency = 24)

# Modelo de previsão automática
modelo <- auto.arima(serie_umidade)
previsao <- forecast(modelo, h = 24)

# Plot da previsão
plot(previsao, main = "Previsão de Umidade para as Próximas 24 Leituras")

# Exportar resumo
write.csv(summary(df), "resumo_estatistico.csv")

# Fim da análise
