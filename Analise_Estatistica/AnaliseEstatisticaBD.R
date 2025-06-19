# Análise Estatística de Dados de Sensores - FarmTech Solutions

# Função para instalar e carregar pacotes
install_and_load <- function(package) {
  if (!require(package, character.only = TRUE)) {
    cat("Instalando pacote:", package, "\n")
    install.packages(package, repos = "https://cran.rstudio.com/")
    library(package, character.only = TRUE)
  }
}

# Pacotes necessários
cat("=== VERIFICANDO E INSTALANDO PACOTES ===\n")
required_packages <- c("dplyr", "ggplot2", "readr", "lubridate", "forecast")

for (pkg in required_packages) {
  install_and_load(pkg)
}

cat("✅ Todos os pacotes carregados com sucesso!\n\n")

# Carregar os dados exportados do banco PostgreSQL
df <- read_csv("leituras_sensores.csv")

# Transformar coluna de timestamp em formato de data/hora
# Verifica se a coluna é 'timestamp' ou 'data_hora_leitura'
if("timestamp" %in% colnames(df)) {
  df$timestamp <- ymd_hms(df$timestamp)
} else {
  # Converte data_hora_leitura para timestamp se necessário
  df$timestamp <- ymd_hms(df$data_hora_leitura)
}

# Converter variáveis booleanas para numéricas se necessário
if("bomba_dagua" %in% colnames(df)) {
  if(is.character(df$bomba_dagua) || is.logical(df$bomba_dagua)) {
    df$bomba_dagua <- ifelse(df$bomba_dagua == TRUE | df$bomba_dagua == "true" | df$bomba_dagua == "True", 1, 0)
  }
}

if("fosforo" %in% colnames(df)) {
  if(is.character(df$fosforo) || is.logical(df$fosforo)) {
    df$fosforo <- ifelse(df$fosforo == TRUE | df$fosforo == "true" | df$fosforo == "True", 1, 0)
  }
}

if("potassio" %in% colnames(df)) {
  if(is.character(df$potassio) || is.logical(df$potassio)) {
    df$potassio <- ifelse(df$potassio == TRUE | df$potassio == "true" | df$potassio == "True", 1, 0)
  }
}

# Resumo estatístico das variáveis
cat("=== RESUMO ESTATÍSTICO DOS DADOS ===\n")
print(summary(df))

# Correlação entre variáveis numéricas
cat("\n=== CORRELAÇÕES ===\n")
cat("Correlação Umidade vs pH:", cor(df$umidade, df$ph, use = "complete.obs"), "\n")
cat("Correlação Umidade vs Temperatura:", cor(df$umidade, df$temperatura, use = "complete.obs"), "\n")

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

# Informações sobre o modelo
cat("\n=== MODELO DE PREVISÃO ===\n")
print(modelo)

cat("\n=== PREVISÕES PARA AS PRÓXIMAS 24 LEITURAS ===\n")
print(previsao)

# Exportar resumo
write.csv(summary(df), "resumo_estatistico.csv")

cat("\n=== ARQUIVOS GERADOS ===\n")
cat("✅ resumo_estatistico.csv - Resumo estatístico salvo\n")
cat("📊 Gráficos gerados: Histograma, Boxplot, Previsão\n")

cat("\n=== ANÁLISE CONCLUÍDA COM SUCESSO ===\n")
cat("Total de registros analisados:", nrow(df), "\n")
cat("Período dos dados:", min(df$timestamp, na.rm=TRUE), "a", max(df$timestamp, na.rm=TRUE), "\n")
