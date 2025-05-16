from flask import Flask, request
import datetime
from flask import jsonify

app = Flask(__name__)

# Dicionário para armazenar os dados recebidos
sensor_data = []

@app.route('/get_data', methods=['GET'])
def get_all_data():
    return jsonify(sensor_data)

@app.route('/data', methods=['GET'])
def receive_data():
    if request.method == 'GET':
        umidade = request.args.get('umidade')
        temperatura = request.args.get('temperatura')
        ph = request.args.get('ph')
        fosforo = request.args.get('fosforo')
        potassio = request.args.get('potassio')
        rele = request.args.get('rele')
        datahora = datetime.datetime.now().isoformat()

        data = {
            'data hora': datahora,
            'umidade': umidade,
            'temperatura': temperatura,
            'ph': ph,
            'fosforo': fosforo,
            'potassio': potassio,
            'bomba dagua': rele
        }
        sensor_data.append(data)
        print(f"Dados recebidos: {data}")
        return "Dados recebidos com sucesso!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    print("Servidor Flask rodando na porta 8000...")