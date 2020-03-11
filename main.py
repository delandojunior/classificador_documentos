from flask import Flask, request, abort
from classificador import classificar, verificarRecebimento
import os
import json
import threading
from queue import Queue
import time
import logging



fila = Queue()
app = Flask(__name__)
global receive, classified


countTeste = 0
countProc = 0

@app.route('/v1/teste', methods=['POST'])
def HelloWorld():
    logging.debug("Recebido uma requisição no endpoint {request.json}.")

    if not request.json:
        logging.debug("Requisição recebida não possui um json valido")
        body = request.data
        print(request)
        response = app.response_class(
        response=json.dumps({"Recebido": 0, "status" : "Recebido mas não é um Json Valido", "req": str(body)}),
        status=400,
        mimetype='application/json'
        )
        return response
    print("AII" + str(request.json))
    #Verificar se o JSON está correto
    #jsonClassificador = classificar(request.json)
    print("verificar recebimento")
    res, code = verificarRecebimento(request.json)
    logging.debug("O JSON FOI VERIFICADO O código de retorno foi: {code} e o status é: {res}")
    print("Código para verificar validade do JSON" + str(code))
    print(f"motivo do erro{res}")
    if(code==200):
        fila.put(request.json)
        logging.debug("Requisição adicionada na fila")
 
    response = app.response_class(
        response=json.dumps(res),
        status=code,
        mimetype='application/json'
    )
    return response

@app.route('/teste/', methods=['GET', 'POST'])
def Home():
    print(countTeste)
    print("Entra?")
    dic = {}
    print("request" + str(request.json))
    dic["data"] = request.data
    dic["header"] = request.headers
    dic["JSON"] = request.json
    # print("recebi requisição data")
    # print(request.data)
    # print("recebi values")
    # print(request.values)
    # print("recebi files")
    # print(request.files)
    # print("recebi form")
    # print(request.form)
    # print("recebi JSON")
    # #print(request.json)
    # print("Header")
    # print(request.headers)
    fila.put(request.json)
    

    response = app.response_class(
        response=json.dumps(str(dic)),
        status=200,
        mimetype='application/text')
    return response
  
    

if __name__ == '__main__':
    #port = int(os.environ.get("PORT",5000))
    app = Flask(__name__)
    #app.run(host='0.0.0.0', port=port)
    