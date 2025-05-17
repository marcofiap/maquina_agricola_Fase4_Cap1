import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.graph_objs as go
from dash import dash_table
import json
from datetime import datetime

# Endereço do servidor Flask
FLASK_SERVER_URL = "http://127.0.0.1:8000/get_data"

# Função para buscar os dados do servidor Flask
def get_sensor_data():
    """
    Busca os dados do servidor Flask.
    Retorna os dados brutos em formato JSON.
    Em caso de erro, retorna um dicionário vazio e exibe uma mensagem de erro.
    """
    try:
        response = requests.get(FLASK_SERVER_URL)
        response.raise_for_status()
        data = response.json()
        print("Dados recebidos do servidor:", json.dumps(data, indent=4, ensure_ascii=False))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com o servidor Flask: {e}")
        return {}

# Função para buscar dados meteorológicos de uma API (incluindo previsão de chuva)
def get_weather_data(api_key, cidade):
    """
    Busca dados meteorológicos atuais e previsão de chuva de uma API.
    Retorna um dicionário com os dados ou None em caso de erro.
    """
    url_atual = f"https://api.openweathermap.org/data/2.5/weather?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br"
    url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br&cnt=4"
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

# Configuração da API meteorológica
API_KEY = "9b90edf9b722e841505a711976022ea2"  # Substitua pela sua chave da API OpenWeatherMap
CIDADE = "Sorocaba"  # Substitua pela cidade desejada

# Configuração do aplicativo Dash
app = dash.Dash(__name__)

# Layout do aplicativo
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1(children='FarmTech Solutions - Dashboard de Irrigação', style={'textAlign': 'center', 'color': '#2E8B57'}),
    dash_table.DataTable(
        id='sensor-data-table',
        columns=[],
        data=[],
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': '#555',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#eee'
            }
        ],
        page_size=10,
        style_table={'overflowX': 'auto'},
    ),
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginTop': '20px'}, children=[
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2(children='Umidade do Solo', style={'color': '#333'}),
            dcc.Graph(id='umidade-graph'),
        ]),
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2(children='Temperatura do Solo', style={'color': '#333'}),
            dcc.Graph(id='temperatura-graph'),
        ]),
    ]),
    html.Div(style={'marginBottom': '20px', 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
        html.H2(children='Níveis de Nutrientes', style={'color': '#333'}),
        html.Div(
            id='nutrient-levels',
            style={'display': 'flex', 'justifyContent': 'space-around'},
            children=[
                html.Div(
                    id='fosforo-level',
                    style={
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'color': '#8B4513',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'backgroundColor': '#d2b48c',
                        'textAlign': 'center',
                        'minWidth': '150px',
                    },
                ),
                html.Div(
                    id='potassio-level',
                    style={
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'color': '#191970',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'backgroundColor': '#add8e6',
                        'textAlign': 'center',
                        'minWidth': '150px',
                    },
                ),
            ],
        ),
    ]),
    html.Div(style={'marginBottom': '20px', 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
        html.H2(children='Condições Climáticas', style={'color': '#333'}),
        html.Div(id='clima-info', style={'fontSize': '16px', 'color': '#333'}),
    ]),
    html.Div(style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
        html.H2(children='Previsão de Chuva (Próximas 12 Horas)', style={'color': '#333'}),
        html.Div(id='previsao-chuva', style={'fontSize': '16px', 'color': '#333'}),
    ]),
    html.Div(id='aviso-desligar-bomba', style={'marginTop': '20px', 'fontSize': '18px', 'fontWeight': 'bold', 'textAlign': 'center'}),
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0)
])

# Callback para atualizar a tabela e os gráficos
@app.callback(
    [
        Output('sensor-data-table', 'columns'),
        Output('sensor-data-table', 'data'),
        Output('umidade-graph', 'figure'),
        Output('temperatura-graph', 'figure'),
        Output('fosforo-level', 'children'),
        Output('potassio-level', 'children'),
        Output('clima-info', 'children'),
        Output('previsao-chuva', 'children'),
        Output('aviso-desligar-bomba', 'children')
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    data = get_sensor_data()
    weather_data = get_weather_data(API_KEY, CIDADE)

    if data:
        # Converter para DataFrame para facilitar o manuseio dos dados
        df = pd.DataFrame(data)

        # Converter a coluna 'TIMESTAMP' para o formato datetime, se existir
        if 'TIMESTAMP' in df.columns:
            df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Converter o DataFrame para dicionário (formato esperado pelo DataTable)
        table_data = df.to_dict('records')
        table_columns = [{"name": i, "id": i} for i in df.columns]

        # Criar os gráficos de umidade e temperatura
        umidade_graph = {
            'data': [
                go.Scatter(x=df['TIMESTAMP'], y=df['UMIDADE'], mode='lines', name='Umidade do Solo')
            ],
            'layout': go.Layout(
                title='Umidade do Solo ao Longo do Tempo',
                xaxis={'title': 'Timestamp'},
                yaxis={'title': 'Umidade (%)'}
            )
        }

        temperatura_graph = {
            'data': [
                go.Scatter(x=df['TIMESTAMP'], y=df['TEMPERATURA'], mode='lines', name='Temperatura do Solo')
            ],
            'layout': go.Layout(
                title='Temperatura do Solo ao Longo do Tempo',
                xaxis={'title': 'Timestamp'},
                yaxis={'title': 'Temperatura (°C)'}
            )
        }

        # Obter os níveis de fósforo e potássio
        fosforo_level = f"Fósforo (P): {df['FOSFORO'].iloc[-1]}" if 'FOSFORO' in df.columns else "Fósforo (P): N/A"
        potassio_level = f"Potássio (K): {df['POTASSIO'].iloc[-1]}" if 'POTASSIO' in df.columns else "Potássio (K): N/A"

        # Formatar dados do clima para exibição
        clima_info_children = []
        previsao_chuva_children = []
        aviso_desligar = ""

        if weather_data and weather_data['atual']:
            clima_info_children = [
                html.H4(f"{weather_data['atual']['name']}, {weather_data['atual']['sys']['country']}"),
                html.P(f"Condição: {weather_data['atual']['weather'][0]['description']}"),
                html.P(f"Temperatura: {weather_data['atual']['main']['temp']} °C"),
                html.P(f"Umidade: {weather_data['atual']['main']['humidity']}%"),
                html.P(f"Velocidade do Vento: {weather_data['atual']['wind']['speed']} m/s")
            ]
        else:
            clima_info_children = [html.P("Não foi possível obter dados climáticos atuais.")]

        if weather_data and weather_data['previsao'] and 'list' in weather_data['previsao']:
            previsao_chuva_children.append(html.H4("Próximas Previsões:"))
            for item in weather_data['previsao']['list']:
                timestamp = pd.to_datetime(item['dt'], unit='s').strftime('%H:%M')
                chuva = item.get('rain', {}).get('3h', 0)
                previsao_chuva_children.append(html.P(f"{timestamp}: {chuva} mm"))
                # Verifica se há previsão de chuva
                if chuva > 0:
                    aviso_desligar = html.Div(
                        children="⚠️ AVISO: Previsão de chuva! A bomba de irrigação deve ser DESLIGADA.",
                        style={'color': 'white', 'backgroundColor': '#dc3545', 'padding': '10px', 'borderRadius': '5px'}
                    )
                    break  # Para o loop ao encontrar a primeira previsão de chuva
        else:
            previsao_chuva_children.append(html.P("Não há previsão de chuva disponível."))

        clima_info = html.Div(children=clima_info_children)
        previsao_chuva_output = html.Div(children=previsao_chuva_children)

        return table_columns, table_data, umidade_graph, temperatura_graph, fosforo_level, potassio_level, clima_info, previsao_chuva_output, aviso_desligar
    else:
        return [], [], {}, {}, "Fósforo (P): N/A", "Potássio (K): N/A", html.Div("Nenhum dado recebido"), html.Div("Nenhum dado recebido"), ""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


























# import dash
# from dash import dcc
# from dash import html
# from dash.dependencies import Input, Output
# import pandas as pd
# import requests
# import plotly.graph_objs as go
# from dash import dash_table
# from datetime import datetime

# # Endereço do servidor Flask
# FLASK_SERVER_URL = "http://127.0.0.1:8000/get_data"

# # Função para buscar os dados do servidor Flask
# def get_sensor_data():
#     """
#     Busca os dados do servidor Flask. Retorna um DataFrame.
#     Em caso de erro, retorna um DataFrame vazio e exibe uma mensagem de erro.
#     """
#     try:
#         response = requests.get(FLASK_SERVER_URL)
#         response.raise_for_status()
#         data = response.json()
#         # Ajuste para lidar com a estrutura de dados aninhada
#         if isinstance(data, dict) and "data" in data:
#             # Se os dados estão aninhados, extrai o DataFrame da chave "data"
#             df = pd.DataFrame([data["data"]])
#         elif isinstance(data, list):
#             # Se os dados já estão em uma lista de dicionários, cria o DataFrame diretamente
#             df = pd.DataFrame(data)
#         else:
#             df = pd.DataFrame()  # Retorna um DataFrame vazio em outros casos
#         return df
#     except requests.exceptions.RequestException as e:
#         print(f"Erro ao conectar com o servidor Flask: {e}")
#         return pd.DataFrame()

# # Função para buscar dados meteorológicos de uma API (incluindo previsão de chuva)
# def get_weather_data(api_key, cidade):
#     """
#     Busca dados meteorológicos atuais e previsão de chuva de uma API.
#     Retorna um dicionário com os dados ou None em caso de erro.
#     """
#     url_atual = f"https://api.openweathermap.org/data/2.5/weather?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br"
#     url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br&cnt=4"
#     try:
#         response_atual = requests.get(url_atual)
#         response_atual.raise_for_status()
#         data_atual = response_atual.json()

#         response_previsao = requests.get(url_previsao)
#         response_previsao.raise_for_status()
#         data_previsao = response_previsao.json()

#         return {"atual": data_atual, "previsao": data_previsao}
#     except requests.exceptions.RequestException as e:
#         print(f"Erro ao obter dados meteorológicos: {e}")
#         return None

# # Configuração da API meteorológica
# API_KEY = "9b90edf9b722e841505a711976022ea2"  # Substitua pela sua chave da API OpenWeatherMap
# CIDADE = "Sorocaba"  # Substitua pela cidade desejada

# app = dash.Dash(__name__)

# app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
#     html.H1(children='FarmTech Solutions - Dashboard de Irrigação', style={'textAlign': 'center', 'color': '#2E8B57'}),

#     html.Div(style={'marginBottom': '20px', 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#         html.H2(children='Dados Recebidos em Tempo Real', style={'color': '#333'}),
#         dash_table.DataTable(
#             id='tabela-dados',
#             columns=[{"name": i, "id": i} for i in pd.DataFrame().columns],
#             data=[],
#             style_cell={'textAlign': 'left'},
#             style_header={
#                 'backgroundColor': '#555',
#                 'color': 'white',
#                 'fontWeight': 'bold'
#             },
#             style_data_conditional=[
#                 {
#                     'if': {'row_index': 'odd'},
#                     'backgroundColor': '#eee'
#                 }
#             ],
#             page_size=10,
#             style_table={'overflowX': 'auto'},
#         ),
#     ]),

#     html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
#         html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#             html.H2(children='Umidade do Solo', style={'color': '#333'}),
#             dcc.Graph(id='grafico-umidade'),
#         ]),
#         html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#             html.H2(children='Temperatura', style={'color': '#333'}),
#             dcc.Graph(id='grafico-temperatura'),
#         ]),
#     ]),

#     html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
#         html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#             html.H2(children='pH do Solo', style={'color': '#333'}),
#             html.Div(
#                 id='indicador-ph',
#                 style={
#                     'textAlign': 'center',
#                     'fontSize': '28px',
#                     'fontWeight': 'bold',
#                     'color': '#4682B4',
#                     'padding': '10px',
#                     'backgroundColor': '#e0f2f7',
#                     'borderRadius': '5px'
#                 },
#             ),
#         ]),
#         html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#             html.H2(children='Status da Bomba de Irrigação', style={'color': '#333'}),
#             html.Div(
#                 id='status-rele',
#                 style={
#                     'textAlign': 'center',
#                     'fontSize': '28px',
#                     'fontWeight': 'bold',
#                     'color': '#FF8C00',
#                     'padding': '10px',
#                     'backgroundColor': '#ffe0b2',
#                     'borderRadius': '5px'
#                 },
#             ),
#         ]),
#     ]),

#     html.Div(style={'marginBottom': '20px', 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#         html.H2(children='Níveis de Nutrientes', style={'color': '#333'}),
#         html.Div(
#             id='estado-nutrientes',
#             style={'display': 'flex', 'justifyContent': 'space-around'},
#             children=[
#                 html.Div(
#                     id='fosforo-status',
#                     style={
#                         'fontSize': '18px',
#                         'fontWeight': 'bold',
#                         'color': '#8B4513',
#                         'padding': '10px',
#                         'borderRadius': '5px',
#                         'backgroundColor': '#d2b48c',
#                         'textAlign': 'center',
#                         'minWidth': '150px',
#                     },
#                 ),
#                 html.Div(
#                     id='potassio-status',
#                     style={
#                         'fontSize': '18px',
#                         'fontWeight': 'bold',
#                         'color': '#191970',
#                         'padding': '10px',
#                         'borderRadius': '5px',
#                         'backgroundColor': '#add8e6',
#                         'textAlign': 'center',
#                         'minWidth': '150px',
#                     },
#                 ),
#             ],
#         ),
#     ]),

#     html.Div(style={'marginBottom': '20px', 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#         html.H2(children='Condições Climáticas', style={'color': '#333'}),
#         html.Div(id='clima-info', style={'fontSize': '16px', 'color': '#333'}),
#     ]),

#     html.Div(style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
#         html.H2(children='Previsão de Chuva (Próximas 12 Horas)', style={'color': '#333'}),
#         html.Div(id='previsao-chuva', style={'fontSize': '16px', 'color': '#333'}),
#     ]),

#     html.Div(id='aviso-desligar-bomba', style={'marginTop': '20px', 'fontSize': '18px', 'fontWeight': 'bold', 'textAlign': 'center'}),

#     dcc.Interval(
#         id='interval-component',
#         interval=2000,
#         n_intervals=0
#     )
# ])

# # Callback para atualizar os componentes do dashboard
# @app.callback(
#     [
#         Output('tabela-dados', 'data'),
#         Output('tabela-dados', 'columns'),
#         Output('grafico-umidade', 'figure'),
#         Output('grafico-temperatura', 'figure'),
#         Output('indicador-ph', 'children'),
#         Output('status-rele', 'children'),
#         Output('fosforo-status', 'children'),
#         Output('potassio-status', 'children'),
#         Output('clima-info', 'children'),
#         Output('previsao-chuva', 'children'),
#         Output('aviso-desligar-bomba', 'children')
#     ],
#     [Input('interval-component', 'n_intervals')]
# )
# def update_dashboard(n):
#     df = get_sensor_data()
#     weather_data = get_weather_data(API_KEY, CIDADE)

#     if not df.empty:
#         # Converter 'timestamp' para datetime, se ainda não for
#         if not isinstance(df['timestamp'].iloc[0], datetime):
#             df['timestamp'] = pd.to_datetime(df['timestamp'])

#         # Formatar 'timestamp' para exibição
#         df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

#         data = df.to_dict('records')
#         columns = [{"name": i, "id": i} for i in df.columns]

#         grafico_umidade = {
#             'data': [
#                 go.Scatter(x=df['timestamp'], y=df['umidade'], mode='lines', name='Umidade')
#             ],
#             'layout': go.Layout(title='Umidade do Solo', yaxis={'title': '%'}, xaxis={'title': 'Tempo'})
#         }

#         grafico_temperatura = {
#             'data': [
#                 go.Scatter(x=df['timestamp'], y=df['temperatura'], mode='lines', name='Temperatura')
#             ],
#             'layout': go.Layout(title='Temperatura', yaxis={'title': '°C'}, xaxis={'title': 'Tempo'})
#         }

#         ph_value = f"pH: {df['ph'].iloc[-1]}" if 'ph' in df.columns else "N/A"
#         indicador_ph = html.Div(children=ph_value)

#         # Use 'bomba_dagua' diretamente, assumindo que o nome da coluna está correto
#         rele_status = f"Bomba: {df['bomba_dagua'].iloc[-1].upper()}" if 'bomba_dagua' in df.columns else "N/A"
#         status_rele = html.Div(children=rele_status)

#         fosforo_status = f"Fósforo (P): {df['fosforo'].iloc[-1].upper()}" if 'fosforo' in df.columns else "Fósforo (P): N/A"
#         potassio_status = f"Potássio (K): {df['potassio'].iloc[-1].upper()}" if 'potassio' in df.columns else "Potássio (K): N/A"

#         clima_info_children = []
#         if weather_data and weather_data['atual']:
#             clima_info_children.extend([
#                 html.H4(f"{weather_data['atual']['name']}, {weather_data['atual']['sys']['country']}", style={'marginBottom': '10px'}),
#                 html.P(f"Condição: {weather_data['atual']['weather'][0]['description']}"),
#                 html.P(f"Temperatura: {weather_data['atual']['main']['temp']} °C"),
#                 html.P(f"Umidade: {weather_data['atual']['main']['humidity']}%"),
#                 html.P(f"Velocidade do Vento: {weather_data['atual']['wind']['speed']} m/s")
#             ])
#         else:
#             clima_info_children.append(html.P("Não foi possível obter dados climáticos atuais.", style={'color': 'red'}))
#         clima_info = html.Div(children=clima_info_children)

#         previsao_chuva_children = []
#         if weather_data and weather_data['previsao'] and 'list' in weather_data['previsao']:
#             previsao_chuva_children.append(html.H4("Próximas Previsões:", style={'marginBottom': '10px'}))
#             for item in weather_data['previsao']['list']:
#                 timestamp = pd.to_datetime(item['dt'], unit='s').strftime('%H:%M')
#                 chuva = item.get('rain', {}).get('3h', 0)
#                 previsao_chuva_children.append(html.P(f"{timestamp}: {chuva} mm"))
#         else:
#             previsao_chuva_children.append(html.P("Não há previsão de chuva disponível.", style={'color': 'orange'}))
#         previsao_chuva_output = html.Div(children=previsao_chuva_children)

#         aviso_desligar = ""
#         if weather_data and weather_data['previsao'] and 'list' in weather_data['previsao']:
#             for item in weather_data['previsao']['list']:
#                 if 'rain' in item and item['rain'].get('3h', 0) > 0:
#                     aviso_desligar = html.Div(
#                         children="⚠️ AVISO: Previsão de chuva! A bomba de irrigação deve ser DESLIGADA.",
#                         style={'color': 'white', 'backgroundColor': '#dc3545', 'padding': '10px', 'borderRadius': '5px'}
#                     )
#                     break
#                 elif 'weather' in item:
#                     for condition in item['weather']:
#                         if 'chuva' in condition['description'].lower():
#                             aviso_desligar = html.Div(
#                                 children="⚠️ AVISO: Previsão de chuva! A bomba de irrigação deve ser DESLIGADA.",
#                                 style={'color': 'white', 'backgroundColor': '#dc3545', 'padding': '10px', 'borderRadius': '5px'}
#                             )
#                             break
#                     if aviso_desligar:
#                         break

#         return data, columns, grafico_umidade, grafico_temperatura, indicador_ph, status_rele, fosforo_status, potassio_status, clima_info, previsao_chuva_output, aviso_desligar
#     else:
#         return [], [], {}, {}, html.Div("Nenhum dado recebido"), html.Div("Nenhum dado recebido"), "Fósforo (P): N/A", "Potássio (K): N/A", html.Div("Nenhum dado recebido"), html.Div("Nenhum dado recebido"), ""

# if __name__ == '__main__':
#     app.run(debug=True)

