import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# URL do seu servidor Flask local
FLASK_SERVER_URL = "http://127.0.0.1:8000/get_data"

# --- Função para consultar a API do tempo ---
def get_clima_atual():
    API_KEY = "SUA_SENHA"  # <-- chave da OpenWeatherMap
    CIDADE = "Camopi"
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={CIDADE}&appid={API_KEY}&units=metric&lang=pt_br"

    try:
        response = requests.get(URL)
        response.raise_for_status()
        dados = response.json()

        clima = {
            'cidade': dados.get("name", "Desconhecida"),
            'temperatura': dados.get("main", {}).get("temp", "N/A"),
            'umidade': dados.get("main", {}).get("humidity", "N/A"),
            'condicao': dados.get("weather", [{}])[0].get("description", "N/A").capitalize(),
            'vento': dados.get("wind", {}).get("speed", "N/A"),
            'chuva': dados.get("rain", {}).get("1h", 0.0)
        }

        clima['vai_chover'] = clima['chuva'] > 0
        return clima

    except Exception as e:
        print("Erro ao consultar clima:", e)
        return {
            'cidade': 'Erro',
            'temperatura': 'N/A',
            'umidade': 'N/A',
            'condicao': 'Erro ao consultar clima',
            'vento': 'N/A',
            'chuva': 'N/A',
            'vai_chover': False
        }

# --- Função para obter os dados do Flask ---
def get_sensor_data():
    try:
        response = requests.get(FLASK_SERVER_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com o servidor Flask: {e}")
        return []

# --- Layout do app ---
app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1('Dashboard FarmTech Solutions', style={'textAlign': 'center', 'color': '#2E8B57'}),

    dash_table.DataTable(
        id='sensor-data-table',
        columns=[],
        data=[],
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': '#555', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#eee'}],
        page_size=10,
        style_table={'overflowX': 'auto'},
    ),

    html.Div(style={'display': 'flex', 'gap': '20px', 'marginTop': '20px'}, children=[
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2('Umidade do Solo'),
            dcc.Graph(id='umidade-graph'),
        ]),
        html.Div(style={'flex': 1, 'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}, children=[
            html.H2('Temperatura do Solo'),
            dcc.Graph(id='temperatura-graph'),
        ]),
    ]),

    html.Div(id='nutrient-levels', style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}, children=[
        html.Div(id='fosforo-level'),
        html.Div(id='potassio-level'),
        html.Div(id='bomba-status'),
    ]),
 
    html.Div(id='alerta-chuva', style={
        'marginTop': '10px',
        'fontWeight': 'bold',
        'fontSize': '18px',
        'textAlign': 'center',
        'padding': '10px',
        'borderRadius': '8px'
    }),

    html.Br(),

    html.Div(id='painel-clima', style={
        'marginTop': '10px',
        'padding': '15px',
        'border': '2px solid #ccc',
        'borderRadius': '10px',
        'backgroundColor': '#f5f5f5',
        'fontSize': '16px',
        'lineHeight': '1.6',
        'color': '#333' 
    }),

    dcc.Interval(id='interval-component', interval=3000, n_intervals=0)
])

@app.callback(
    [
        Output('sensor-data-table', 'columns'),
        Output('sensor-data-table', 'data'),
        Output('umidade-graph', 'figure'),
        Output('temperatura-graph', 'figure'),
        Output('fosforo-level', 'children'),
        Output('fosforo-level', 'style'),
        Output('potassio-level', 'children'),
        Output('potassio-level', 'style'),
        Output('bomba-status', 'children'),
        Output('bomba-status', 'style'),
        Output('alerta-chuva', 'children'),
        Output('alerta-chuva', 'style'),
        Output('painel-clima', 'children'),
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    data = get_sensor_data()
    if data:
        df = pd.DataFrame(data)
        df.columns = df.columns.str.upper()

        if 'TIMESTAMP' in df.columns:
            df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])                       
            df.sort_values(by="TIMESTAMP", inplace=True)

        table_data = df.to_dict('records')
        table_columns = [{"name": i, "id": i} for i in df.columns]

        umidade_graph = {
            'data': [go.Scatter(x=df['TIMESTAMP'], y=df['UMIDADE'], mode='lines', name='Umidade')],
            'layout': go.Layout(title='Umidade do Solo ao Longo do Tempo', xaxis={'title': 'Timestamp'}, yaxis={'title': 'Umidade (%)'})
        }

        temperatura_graph = {
            'data': [go.Scatter(x=df['TIMESTAMP'], y=df['TEMPERATURA'], mode='lines', name='Temperatura')],
            'layout': go.Layout(title='Temperatura do Solo ao Longo do Tempo', xaxis={'title': 'Timestamp'}, yaxis={'title': 'Temperatura (°C)'})
        }

        fosforo_msg = "Fósforo (P): N/A"
        fosforo_style = {}
        if 'FOSFORO' in df.columns and not df['FOSFORO'].isna().all():
            val = df['FOSFORO'].iloc[-1].strip().lower()
            fosforo_msg = 'Fósforo (P): Presente ✅' if val == 'presente' else 'Fósforo (P): Ausente ❌'
            fosforo_style = {'color': 'green' if val == 'presente' else 'red',
                             'backgroundColor': '#d0f0c0' if val == 'presente' else '#f9d6d5',
                             'fontWeight': 'bold', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '5px'}

        potassio_msg = "Potássio (K): N/A"
        potassio_style = {}
        if 'POTASSIO' in df.columns and not df['POTASSIO'].isna().all():
            val = df['POTASSIO'].iloc[-1].strip().lower()
            potassio_msg = 'Potássio (K): Presente ✅' if val == 'presente' else 'Potássio (K): Ausente ❌'
            potassio_style = {'color': 'green' if val == 'presente' else 'red',
                              'backgroundColor': '#d0f0c0' if val == 'presente' else '#f9d6d5',
                              'fontWeight': 'bold', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '5px'}

        bomba_msg = "Bomba: status desconhecido"
        bomba_style = {'color': 'gray', 'backgroundColor': '#eeeeee', 'fontWeight': 'bold', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '5px'}
        if 'BOMBA_DAGUA' in df.columns and not df['BOMBA_DAGUA'].isna().all():
            val = df['BOMBA_DAGUA'].iloc[-1].strip().lower()
            if val == 'on':
                bomba_msg = 'Bomba de Irrigação: Ligada ✅'
                bomba_style['color'] = 'green'
                bomba_style['backgroundColor'] = '#d0f0c0'
            elif val == 'off':
                bomba_msg = 'Bomba de Irrigação: Desligada ❌'
                bomba_style['color'] = 'red'
                bomba_style['backgroundColor'] = '#f9d6d5'

        clima = get_clima_atual()
        alerta_msg = f"🌧️ Alerta: Previsão de {clima['chuva']} mm de chuva!Manter Desligado a Bomba d'água!!!" if clima['vai_chover'] else "☀️ Sem previsão de chuva nas próximas horas."
        alerta_style = {'textAlign': 'center', 'marginTop': '30px', 'backgroundColor': '#ffe4e1' if clima['vai_chover'] else '#e0f7fa', 'color': 'red' if clima['vai_chover'] else 'green'}

        painel_clima = html.Div([
            html.Div(style={'display': 'flex', 'justifyContent': 'space-around'}, children=[
                html.Div(f"📍 Cidade: {clima['cidade']}"),
                html.Div(f"🌡️ Temperatura: {clima['temperatura']}°C"),
                html.Div(f"💧 Umidade: {clima['umidade']}%"),
            ]),
            html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '10px'}, children=[
                html.Div(f"☁️ Condição: {clima['condicao']}"),
                html.Div(f"🌬️ Vento: {clima['vento']} m/s"),
                html.Div(f"🌧️ Chuva (última hora): {clima['chuva']} mm"),
            ])
        ])

        return table_columns, table_data, umidade_graph, temperatura_graph, \
               fosforo_msg, fosforo_style, potassio_msg, potassio_style, \
               bomba_msg, bomba_style, alerta_msg, alerta_style, painel_clima

    else:
        painel_clima = html.Div([
            html.Div("❌ Erro ao obter dados climáticos.", style={'textAlign': 'center'})
        ])
        return [], [], {}, {}, "Fósforo (P): N/A", {}, "Potássio (K): N/A", {}, \
               "Bomba: N/A", {}, "Sem dados climáticos", {}, painel_clima

if __name__ == '__main__':
    app.run(debug=True)







