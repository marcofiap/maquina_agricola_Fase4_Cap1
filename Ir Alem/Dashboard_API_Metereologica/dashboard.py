import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import time
import requests
import plotly.graph_objs as go
from dash import dash_table

# Endereço do servidor Flask
FLASK_SERVER_URL = "http://127.0.0.1:8000/data"

# Função para buscar os dados do servidor Flask
def get_sensor_data():
    """
    Busca os dados do servidor Flask. Retorna um DataFrame.
    Em caso de erro, retorna um DataFrame vazio e exibe uma mensagem de erro.
    """
    try:
        response = requests.get(FLASK_SERVER_URL.replace('/data', '/get_data'))       
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com o servidor Flask: {e}")
        return pd.DataFrame()

# Função para buscar dados meteorológicos de uma API
def get_weather_data(api_key, cidade):
    """
    Busca dados meteorológicos de uma API.
    Retorna um dicionário com os dados ou None em caso de erro.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"  # Adaptado para português
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados meteorológicos: {e}")
        return None

# Configuração da API meteorológica
API_KEY = "9b90edf9b722e841505a711976022ea2"  # Substitua pela sua chave da API OpenWeatherMap
CIDADE = "Sorocaba"  # Substitua pela cidade desejada

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='FarmTech Solutions - Dashboard de Irrigação'),

    html.Div(children=[
        html.H2(children='Dados Recebidos em Tempo Real'),
        dash_table.DataTable(
            id='tabela-dados',
            columns=[{"name": i, "id": i} for i in pd.DataFrame().columns],
            data=[],
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(220, 220, 220)',
                    'color': 'black'
                }
            ],
            page_size=10,
            style_table={
                'height': '300px',
                'overflowY': 'auto',
                'overflowX': 'auto',
            },
        ),
    ]),

    html.Div(children=[
        html.H2(children='Umidade do Solo'),
        dcc.Graph(id='grafico-umidade'),
    ]),

    html.Div(children=[
        html.H2(children='Temperatura'),
        dcc.Graph(id='grafico-temperatura'),
    ]),

    html.Div(children=[
        html.H2(children='pH do Solo'),
        html.Div(
            id='indicador-ph',
            style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'fontSize': '24px',
                'fontWeight': 'bold',
                'color': '#333',
                'marginTop': '20px',
            },
        ),
    ]),

    html.Div(children=[
        html.H2(children='Status da Bomba de Irrigação'),
        html.Div(
            id='status-rele',
            style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'fontSize': '24px',
                'fontWeight': 'bold',
                'marginTop': '20px',
            },
        ),
    ]),

    html.Div(
        children=[
            html.H2(children='Níveis de Nutrientes'),
            html.Div(
                id='estado-nutrientes',
                style={
                    'display': 'flex',
                    'justifyContent': 'space-around',
                    'alignItems': 'center',
                    'marginTop': '20px',
                    'width': '100%',
                },
                children=[
                    html.Div(
                        id='fosforo-status',
                        style={
                            'fontSize': '18px',
                            'fontWeight': 'bold',
                            'color': '#333',
                            'padding': '10px',
                            'borderRadius': '5px',
                            'backgroundColor': '#e0e0e0',
                            'textAlign': 'center',
                            'minWidth': '150px',
                        },
                    ),
                    html.Div(
                        id='potassio-status',
                        style={
                            'fontSize': '18px',
                            'fontWeight': 'bold',
                            'color': '#333',
                            'padding': '10px',
                            'borderRadius': '5px',
                            'backgroundColor': '#e0e0e0',
                            'textAlign': 'center',
                            'minWidth': '150px',
                        },
                    ),
                ],
            ),
        ],
    ),
    html.Div(children=[ #Div para clima
        html.H2(children='Condições Climáticas'),
        html.Div(id='clima-info')
    ]),

    dcc.Interval(
        id='interval-component',
        interval=2000,
        n_intervals=0
    )
])


# Callback para atualizar os componentes do dashboard
@app.callback(
    [
        Output('tabela-dados', 'data'),
        Output('tabela-dados', 'columns'),
        Output('grafico-umidade', 'figure'),
        Output('grafico-temperatura', 'figure'),
        Output('indicador-ph', 'children'),
        Output('status-rele', 'children'),
        Output('fosforo-status', 'children'),
        Output('potassio-status', 'children'),
        Output('clima-info', 'children'), #Adicionado output para informações climaticas
        Output('previsao-chuva', 'children') # Novo output para previsão de chuva
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = get_sensor_data()
    weather_data = get_weather_data(API_KEY, CIDADE) # Busca dados do clima (atual e previsão)

    if not df.empty:
        data = df.to_dict('records')
        columns = [{"name": i, "id": i} for i in df.columns]

        grafico_umidade = {
            'data': [
                go.Scatter(x=df['data hora'], y=df['umidade'], mode='lines')
            ],
            'layout': go.Layout(title='Umidade do Solo')
        }

        grafico_temperatura = {
            'data': [
                go.Scatter(x=df['data hora'], y=df['temperatura'], mode='lines')
            ],
            'layout': go.Layout(title='Temperatura')
        }

        ph_value = f"pH: {df['ph'].iloc[-1]}" if 'ph' in df.columns else "Dados de pH insuficientes"
        indicador_ph = html.P(
            children=ph_value,
            style={
                'fontSize': '24px',
                'fontWeight': 'bold',
                'color': '#333',
            }
        )

        rele_status = f"Bomba: {df['bomba dagua'].iloc[-1].upper()}" if 'bomba dagua' in df.columns else "Dados do relé insuficientes"
        status_rele = html.P(
            children=rele_status,
            style={
                'fontSize': '24px',
                'fontWeight': 'bold',
                'color': '#333',
            }
        )

        fosforo_status = f"Fósforo (P): {df['fosforo'].iloc[-1].upper()}" if 'fosforo' in df.columns else "Fósforo (P): N/A"
        potassio_status = f"Potássio (K): {df['potassio'].iloc[-1].upper()}" if 'potassio' in df.columns else "Potássio (K): N/A"

        # Formata dados do clima atual para exibição
        if weather_data and weather_data['atual']:
            clima_info = html.Div(children=[
                html.P(f"Condição: {weather_data['atual']['weather'][0]['description']}"),
                html.P(f"Temperatura: {weather_data['atual']['main']['temp']} °C"),
                html.P(f"Umidade: {weather_data['atual']['main']['humidity']}%"),
                html.P(f"Velocidade do Vento: {weather_data['atual']['wind']['speed']} m/s")
            ], style = {
                'fontSize': '18px',
                'color': '#333'
            })
        else:
            clima_info = html.P("Não foi possível obter dados climáticos atuais.", style={'color': 'red'})

        # Formata dados da previsão de chuva para exibição
        previsao_chuva_info = []
        if weather_data and weather_data['previsao'] and 'list' in weather_data['previsao']:
            for item in weather_data['previsao']['list']:
                timestamp = pd.to_datetime(item['dt'], unit='s').strftime('%H:%M')
                chuva = item.get('rain', {}).get('3h', 0) # Obtém a quantidade de chuva nas próximas 3 horas
                previsao_chuva_info.append(html.P(f"{timestamp}: {chuva} mm"))
            previsao_chuva_output = html.Div(children=previsao_chuva_info, style={'fontSize': '16px', 'color': '#333'})
        else:
            previsao_chuva_output = html.P("Não há previsão de chuva disponível.", style={'color': 'orange'})

        return data, columns, grafico_umidade, grafico_temperatura, indicador_ph, status_rele, fosforo_status, potassio_status, clima_info, previsao_chuva_output
    else:
        return [], [], {}, {}, html.P("Nenhum dado recebido do servidor Flask."), html.P("Nenhum dado recebido"), "Fósforo (P): N/A", "Potássio (K): N/A", html.P("Nenhum dado recebido"), html.P("Nenhum dado recebido")

if __name__ == '__main__':
    app.run(debug=True)






# import streamlit as st
# import pandas as pd
# import time
# import requests

# # Endereço do servidor Flask
# FLASK_SERVER_URL = "http://127.0.0.1:8000/data"  # Por enquanto, vamos buscar os dados do servidor

# # Função para buscar os dados do servidor Flask
# def get_sensor_data():
#     """
#     Busca os dados do servidor Flask.  Retorna um DataFrame.
#     Em caso de erro, retorna um DataFrame vazio e exibe uma mensagem de erro no Streamlit.
#     """
#     try:
#         response = requests.get(FLASK_SERVER_URL.replace('/data', '/get_data'))  # Usamos a nova rota
#         response.raise_for_status()  # Lança uma exceção para erros HTTP (4xx ou 5xx)
#         data = response.json()
#         # Garante que a conversão para DataFrame ocorra mesmo se 'data' for uma lista vazia
#         df = pd.DataFrame(data) if data else pd.DataFrame()
#         return df
#     except requests.exceptions.RequestException as e:
#         st.error(f"Erro ao conectar com o servidor Flask: {e}")
#         return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

# st.title("FarmTech Solutions - Dashboard de Irrigação")

# # Exibir os dados brutos
# st.subheader("Dados Recebidos em Tempo Real")
# df = get_sensor_data() # Obtem os dados

# # Verifica se o DataFrame está vazio antes de tentar exibir ou plotar
# if not df.empty:
#     st.dataframe(df)  # Exibe o DataFrame se não estiver vazio

#     # Gráfico de Umidade
#     st.subheader("Umidade do Solo")
#     if 'data hora' in df.columns and 'umidade' in df.columns: #alterado de timestamp para data hora
#         st.line_chart(df[['data hora', 'umidade']].set_index('data hora')) #alterado de timestamp para data hora
#     else:
#         st.warning("Dados de umidade insuficientes para exibir o gráfico.")

#     # Gráfico de Temperatura
#     st.subheader("Temperatura")
#     if 'data hora' in df.columns and 'temperatura' in df.columns: #alterado de timestamp para data hora
#         st.line_chart(df[['data hora', 'temperatura']].set_index('data hora')) #alterado de timestamp para data hora
#     else:
#         st.warning("Dados de temperatura insuficientes para exibir o gráfico.")

#     # Indicador de pH
#     st.subheader("pH do Solo")
#     if 'ph' in df.columns:
#         st.metric(label="pH", value=df['ph'].iloc[-1])
#     else:
#         st.warning("Dados de pH insuficientes para exibir o indicador.")

#     # Status do Relé
#     st.subheader("Status da Bomba de Irrigação")
#     if 'bomba dagua' in df.columns: #alterado de rele para bomba dagua
#         st.metric(label="Rele", value=df['bomba dagua'].iloc[-1].upper()) #alterado de rele para bomba dagua
#     else:
#         st.warning("Dados do relé insuficientes para exibir o status.")

#     # Estado dos Nutrientes
#     st.subheader("Níveis de Nutrientes")
#     col1, col2 = st.columns(2)
#     if 'fosforo' in df.columns:
#         col1.metric("Fósforo (P)", df['fosforo'].iloc[-1].upper())
#     else:
#         col1.warning("Dados de fósforo insuficientes.")
#     if 'potassio' in df.columns:
#         col2.metric("Potássio (K)", df['potassio'].iloc[-1].upper())
#     else:
#         col2.warning("Dados de potássio insuficientes.")
# else:
#     st.warning("Nenhum dado recebido do servidor Flask.")
#     st.info("Aguardando dados dos sensores... Certifique-se de que o servidor Flask está em execução e enviando dados.")





