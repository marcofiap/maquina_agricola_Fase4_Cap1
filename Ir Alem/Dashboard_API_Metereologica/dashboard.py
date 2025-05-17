import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
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

# Função para buscar dados meteorológicos de uma API (incluindo previsão de chuva)
def get_weather_data(api_key, cidade):
    """
    Busca dados meteorológicos atuais e previsão de chuva de uma API.
    Retorna um dicionário com os dados ou None em caso de erro.
    """
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

# Configuração da API meteorológica
API_KEY = "9b90edf9b722e841505a711976022ea2" # Substitua pela sua chave da API OpenWeatherMap
CIDADE = "Presidente Figueiredo" # Substitua pela cidade desejada

app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1(children='FarmTech Solutions - Dashboard de Irrigação', style={'textAlign': 'center', 'color': '#2E8B57'}),

    html.Div(style={'marginBottom': '20px', 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
        html.H2(children='Dados Recebidos em Tempo Real', style={'color': '#333'}),
        dash_table.DataTable(
            id='tabela-dados',
            columns=[{"name": i, "id": i} for i in pd.DataFrame().columns],
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
    ]),

    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2(children='Umidade do Solo', style={'color': '#333'}),
            dcc.Graph(id='grafico-umidade'),
        ]),
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2(children='Temperatura', style={'color': '#333'}),
            dcc.Graph(id='grafico-temperatura'),
        ]),
    ]),

    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2(children='pH do Solo', style={'color': '#333'}),
            html.Div(
                id='indicador-ph',
                style={
                    'textAlign': 'center',
                    'fontSize': '28px',
                    'fontWeight': 'bold',
                    'color': '#4682B4',
                    'padding': '10px',
                    'backgroundColor': '#e0f2f7',
                    'borderRadius': '5px'
                },
            ),
        ]),
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2(children='Status da Bomba de Irrigação', style={'color': '#333'}),
            html.Div(
                id='status-rele',
                style={
                    'textAlign': 'center',
                    'fontSize': '28px',
                    'fontWeight': 'bold',
                    'color': '#FF8C00',
                    'padding': '10px',
                    'backgroundColor': '#ffe0b2',
                    'borderRadius': '5px'
                },
            ),
        ]),
    ]),

    html.Div(style={'marginBottom': '20px', 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
        html.H2(children='Níveis de Nutrientes', style={'color': '#333'}),
        html.Div(
            id='estado-nutrientes',
            style={'display': 'flex', 'justifyContent': 'space-around'},
            children=[
                html.Div(
                    id='fosforo-status',
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
                    id='potassio-status',
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
        Output('previsao-chuva', 'children'), # Novo output para previsão de chuva
        Output('aviso-desligar-bomba', 'children') # Novo output para o aviso de desligar a bomba
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
                go.Scatter(x=df['data hora'], y=df['umidade'], mode='lines', name='Umidade')
            ],
            'layout': go.Layout(title='Umidade do Solo', yaxis={'title': '%'})
        }

        grafico_temperatura = {
            'data': [
                go.Scatter(x=df['data hora'], y=df['temperatura'], mode='lines', name='Temperatura')
            ],
            'layout': go.Layout(title='Temperatura', yaxis={'title': '°C'})
        }

        ph_value = f"pH: {df['ph'].iloc[-1]}" if 'ph' in df.columns else "N/A"
        indicador_ph = html.Div(children=ph_value)

        rele_status = f"Bomba: {df['bomba dagua'].iloc[-1].upper()}" if 'bomba dagua' in df.columns else "N/A"
        status_rele = html.Div(children=rele_status)

        fosforo_status = f"Fósforo (P): {df['fosforo'].iloc[-1].upper()}" if 'fosforo' in df.columns else "Fósforo (P): N/A"
        potassio_status = f"Potássio (K): {df['potassio'].iloc[-1].upper()}" if 'potassio' in df.columns else "Potássio (K): N/A"

        # Formata dados do clima atual para exibição
        clima_info_children = []
        if weather_data and weather_data['atual']:
            clima_info_children.extend([
                html.H4(f"{weather_data['atual']['name']}, {weather_data['atual']['sys']['country']}", style={'marginBottom': '10px'}), # Adicionando nome da cidade e país
                html.P(f"Condição: {weather_data['atual']['weather'][0]['description']}"),
                html.P(f"Temperatura: {weather_data['atual']['main']['temp']} °C"),
                html.P(f"Umidade: {weather_data['atual']['main']['humidity']}%"),
                html.P(f"Velocidade do Vento: {weather_data['atual']['wind']['speed']} m/s")
            ])
        else:
            clima_info_children.append(html.P("Não foi possível obter dados climáticos atuais.", style={'color': 'red'}))
        clima_info = html.Div(children=clima_info_children)

        # Formata dados da previsão de chuva para exibição
        previsao_chuva_children = []
        if weather_data and weather_data['previsao'] and 'list' in weather_data['previsao']:
            previsao_chuva_children.append(html.H4("Próximas Previsões:", style={'marginBottom': '10px'}))
            for item in weather_data['previsao']['list']:
                timestamp = pd.to_datetime(item['dt'], unit='s').strftime('%H:%M')
                chuva = item.get('rain', {}).get('3h', 0)
                previsao_chuva_children.append(html.P(f"{timestamp}: {chuva} mm"))
        else:
            previsao_chuva_children.append(html.P("Não há previsão de chuva disponível.", style={'color': 'orange'}))
        previsao_chuva_output = html.Div(children=previsao_chuva_children)

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

        return data, columns, grafico_umidade, grafico_temperatura, indicador_ph, status_rele, fosforo_status, potassio_status, clima_info, previsao_chuva_output, aviso_desligar
    else:
        return [], [], {}, {}, html.Div("Nenhum dado recebido"), html.Div("Nenhum dado recebido"), "Fósforo (P): N/A", "Potássio (K): N/A", html.Div("Nenhum dado recebido"), html.Div("Nenhum dado recebido"), ""

if __name__ == '__main__':
    app.run(debug=True)


#     import dash
# from dash import dcc
# from dash import html
# from dash.dependencies import Input, Output
# import pandas as pd
# import requests
# import plotly.graph_objs as go
# from dash import dash_table

# # Endereço do servidor Flask
# FLASK_SERVER_URL = "http://127.0.0.1:8000/data"

# # Função para buscar os dados do servidor Flask
# def get_sensor_data():
#     """
#     Busca os dados do servidor Flask. Retorna um DataFrame.
#     Em caso de erro, retorna um DataFrame vazio e exibe uma mensagem de erro.
#     """
#     try:
#         response = requests.get(FLASK_SERVER_URL.replace('/data', '/get_data'))
#         response.raise_for_status()
#         data = response.json()
#         df = pd.DataFrame(data) if data else pd.DataFrame()
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
#     url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade},BR&appid={api_key}&units=metric&lang=pt_br&cnt=4" # Previsão para 3 em 3 horas (próximas 12 horas)
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
# API_KEY = "9b90edf9b722e841505a711976022ea2" # Substitua pela sua chave da API OpenWeatherMap
# CIDADE = "Porto Alegre" # Substitua pela cidade desejada

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
#         Output('clima-info', 'children'), #Adicionado output para informações climaticas
#         Output('previsao-chuva', 'children') # Novo output para previsão de chuva
#     ],
#     [Input('interval-component', 'n_intervals')]
# )
# def update_dashboard(n):
#     df = get_sensor_data()
#     weather_data = get_weather_data(API_KEY, CIDADE) # Busca dados do clima (atual e previsão)

#     if not df.empty:
#         data = df.to_dict('records')
#         columns = [{"name": i, "id": i} for i in df.columns]

#         grafico_umidade = {
#             'data': [
#                 go.Scatter(x=df['data hora'], y=df['umidade'], mode='lines', name='Umidade')
#             ],
#             'layout': go.Layout(title='Umidade do Solo', yaxis={'title': '%'})
#         }

#         grafico_temperatura = {
#             'data': [
#                 go.Scatter(x=df['data hora'], y=df['temperatura'], mode='lines', name='Temperatura')
#             ],
#             'layout': go.Layout(title='Temperatura', yaxis={'title': '°C'})
#         }

#         ph_value = f"pH: {df['ph'].iloc[-1]}" if 'ph' in df.columns else "N/A"
#         indicador_ph = html.Div(children=ph_value)

#         rele_status = f"Bomba: {df['bomba dagua'].iloc[-1].upper()}" if 'bomba dagua' in df.columns else "N/A"
#         status_rele = html.Div(children=rele_status)

#         fosforo_status = f"Fósforo (P): {df['fosforo'].iloc[-1].upper()}" if 'fosforo' in df.columns else "Fósforo (P): N/A"
#         potassio_status = f"Potássio (K): {df['potassio'].iloc[-1].upper()}" if 'potassio' in df.columns else "Potássio (K): N/A"

#         # Formata dados do clima atual para exibição
#         clima_info_children = []
#         if weather_data and weather_data['atual']:
#             clima_info_children.extend([
#                 html.H4(f"{weather_data['atual']['name']}, {weather_data['atual']['sys']['country']}", style={'marginBottom': '10px'}), # Adicionando nome da cidade e país
#                 html.P(f"Condição: {weather_data['atual']['weather'][0]['description']}"),
#                 html.P(f"Temperatura: {weather_data['atual']['main']['temp']} °C"),
#                 html.P(f"Umidade: {weather_data['atual']['main']['humidity']}%"),
#                 html.P(f"Velocidade do Vento: {weather_data['atual']['wind']['speed']} m/s")
#             ])
#         else:
#             clima_info_children.append(html.P("Não foi possível obter dados climáticos atuais.", style={'color': 'red'}))
#         clima_info = html.Div(children=clima_info_children)

#         # Formata dados da previsão de chuva para exibição
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

#         return data, columns, grafico_umidade, grafico_temperatura, indicador_ph, status_rele, fosforo_status, potassio_status, clima_info, previsao_chuva_output
#     else:
#         return [], [], {}, {}, html.Div("Nenhum dado recebido"), html.Div("Nenhum dado recebido"), "Fósforo (P): N/A", "Potássio (K): N/A", html.Div("Nenhum dado recebido"), html.Div("Nenhum dado recebido")

# if __name__ == '__main__':
#     app.run(debug=True)