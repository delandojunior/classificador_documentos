# coding: utf-8

from waitress import serve
import main
import threading
from queue import Queue
import time
from classificador import classificar, verificarRecebimento
import json
import urllib.request
import logging



def process():
    
    print("Parooou será? " + str(main.countProc))
    while True:
        print("Li a FILA " + str())
        jsonC = main.fila.get()
        logging.debug(f"Lido elemento da fila -> json: {jsonC}")
        with open("json_requisicoes.txt", "a") as myfile:
            myfile.write(str(jsonC)+'\n')
        print("Rodar o Classificador")
        try:
            jsonClassificador = classificar(jsonC)
            main.countProc+=1
        except Exception as identifier:
            print("--------------ERROOOOOOR--------------")
            print("/n/n")
            print(jsonC)
            print("\n----------------------------------------------\n")
            print(identifier)
            logging.error("Ocorreu um erro durante a classificação do arquivo")
            jsonClassificador = {"documento": [{"iddocumento": jsonC["Colaborador"][0]["Iddocumento"], "statusdocumento": "0", "descricaodocumento": "Nao foi possivel classificar o documento."}]}
            #jsonClassificador = {"status": "0", "obs":"não foi possível classificar"}
            
        logging.debug(f"ELEMENTO CLASSIFICADO resposta -> {jsonClassificador}")
        print(jsonClassificador)
        try:    
                myurl = "https://webhook.site/11a86c5c-f334-4de8-b20d-2452a08fa4a5"
                req = urllib.request.Request(myurl)
                req.add_header('Content-Type', 'application/json; charset=utf-8')
                jsondata = json.dumps(jsonClassificador)
                jsondata.replace("'",'"')
                jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
                req.add_header('Content-Length', len(jsondataasbytes))
                print("VOU ENVIIIAR")
                response = urllib.request.urlopen(req, jsondataasbytes)
                print(f"response {response}")
                print("enviei para o server esse json")
                logging.debug(f"Enviado para o webserver do contract aguardando retorno.")
                print(jsondataasbytes)
                #tratar o retorno do webserver
                raw_data = response.read()
                encoding = response.info().get_content_charset('utf8')  # JSON default
                #data = json.loads(raw_data.decode(encoding))
                logging.debug(f"Envio da classificação para o contract json enviado -> {jsondataasbytes}")
                logging.debug(f"Retorono do contract web -> {data}")
                #main.classified += 1
        except urllib.error.HTTPError as e:
                body = e.read().decode()  
                print(body)
                print("Erro no envio para o server")
                logging.warning("Erro de envio da resposta do classificador para o contract. Excessão -> {body}")
                #main.fila.put(jsonC)
                pass
        print("Thread de classificação numero > " + str(main.countProc))
        print(data)

#server = threading.Thread(target=start, args=(main.fila,))
consumer = threading.Thread(target=process)
consumer1 = threading.Thread(target=process)
consumer2 = threading.Thread(target=process)
consumer.start()
consumer1.start()
consumer2.start()

serve(main.app, host='0.0.0.0', port=5000)
