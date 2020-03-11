# coding: utf-8
from __future__ import print_function
import json
from os.path import abspath
from ibm_watson import VisualRecognitionV3, ApiException
import io
from google.cloud import vision
#convert to json google
from pprint import pprint
from google.protobuf.json_format import MessageToJson
from time import time
from pdf2image import convert_from_path
import urllib.request
from requests.utils import requote_uri
import os
from unidecode import unidecode
import logging
##Import para corrigir erro de bomberror
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import re
import datetime
import main
import enviroments

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = enviroments.googleJson



print("Iniciou")
start = time()

dpi = 300

def compressPhoto(path):
    print("comprimir foto")
    #im1 = Image.open(path)
    with Image.open(path) as im1:
        imSize = im1.size
        #print(imSize)
        #newPath = path
        while(os.path.getsize(path) > 10000000 or imSize[0] > 5300 or imSize[1] > 5300):
            #print("muito grande, comprimindo  -> " + str(os.path.getsize(path)))   
            #path = path
        # print(f"a imagem tem tamanho {im1.size}")
            if (im1.size[0] > 5300 or im1.size[1] > 5300):
                #print("resize")
                im1 = im1.resize((int(imSize[0]/10),int(imSize[1]/10)), Image.ANTIALIAS)
                im1.save(path, "JPEG", quality=40)
                imSize = im1.size
                #print("save")
            else:
                #print("Só comprimirs")
                im1.save(path, "JPEG", quality=40)
            # # write the buffer to a file to make sure it worked
        #print("arquivo ok, comprimindo")
        #print(path)
    return path
# Converter de pdf para imagem
def download_convert(URL, dpi):
    try:
        print('Beginning file download with urllib2... ')
        url_processed = requote_uri(URL)
        filename = str(hash(url_processed)) + '.pdf'
        pathTemp = './temp/pdf/'
        pathFile = pathTemp+filename
        urllib.request.urlretrieve(url_processed, pathFile)
        print("download finished")
        try:
            filesPath = []
            #print(pathFile)
            pages = convert_from_path(pathFile, dpi)
            count = 0
            picTemp = './temp/pictures/'
            
            for page in pages:
                photoName = filename + '-' + str(count) + '.jpg'
                pathPhoto = picTemp + photoName
                page.save(pathPhoto, 'JPEG')
                pathPhoto = compressPhoto(pathPhoto)
               # print(f"filesPath {pathPhoto}")
                filesPath.append(pathPhoto)
                count += 1
                
            return filesPath
        except Exception as error:
            print("Error " + str(error))
            filesPath = ["Erro", error]
            return filesPath
    except Exception as e:
        print("Deu um Erro na url: " + str(e))
        print(e)
        filesPath = ["Erro", e]
        return filesPath
    
    #remover esse comentario
    #os.remove(pathFile)

convertends = time()

##______________Classificar documento OCR Google_______________________##

def detect_document(path):
    """Detects document features in an image."""
    
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)
    
    

    # for page in response.full_text_annotation.pages:
    #     for block in page.blocks:
    #         print('\nBlock confidence: {}\n'.format(block.confidence))

    #         for paragraph in block.paragraphs:
    #             print('Paragraph confidence: {}'.format(paragraph.confidence))

    #             for word in paragraph.words:
    #                 word_text = ''.join([
    #                 symbol.text for symbol in word.symbols
    #                 ])
    #                 print('Word text: {} (confidence: {})'.format(word_text, word.confidence))

    #                 for symbol in word.symbols:
    #                     print('\tSymbol: {} (confidence: {})'.format(
    #                     symbol.text, symbol.confidence))

    

    return response.full_text_annotation.text


endOCR = time()

##_____________________________________##


#______________Consumir API do Watson_______________________##
#If service instance provides IAM API key authentication

def watsonClassifier(path):
        
    print("classificar no watson")
    visual_recognition = VisualRecognitionV3(
        '2018-03-19',
        iam_apikey=enviroments.watsonCredentials['iam_apikey'])
    #print("Certificado watson")
    with open(path, 'rb') as images_file:
        classes = visual_recognition.classify(
            images_file,
            threshold='0.0',
        classifier_ids=enviroments.watsonCredentials['classifier_ids']).get_result()
        print("classificado")
        print(f"Classes do Watson {classes}")
        return classes

endwatson = time()


def validarCPF(cpf, texto):

    textoSemPont = texto.replace(".", "").replace("/", "").replace("-", "").replace(":", "").replace("<", "").replace(">", "").replace('"', "").replace('|', "").replace(" ", "").replace(",", "").replace("'", "")
    cpfSemPont = cpf.replace(".", "").replace("/", "").replace("-", "").replace(":", "").replace("<", "").replace(">", "").replace('"', "").replace('|', "").replace(" ", "").replace(",", "").replace("'", "")
    if cpfSemPont in textoSemPont:
        return True
    else:
        return False
    
def validarNOME(nome, texto):
    textoSemPont = texto.replace(".", "").replace("/", "").replace("-", "").replace(":", "").replace("<", "").replace(">", "").replace('"', "").replace('|', "").replace(" ", "")
    nomeSemPont = nome.replace(".", "").replace("/", "").replace("-", "").replace(":", "").replace("<", "").replace(">", "").replace('"', "").replace('|', "")
    nomeUni = unidecode(nomeSemPont)
    textoUni = unidecode(textoSemPont)
    partesNome = nomeUni.split(" ")
    nomesCertos = 0
    for nome in partesNome:
        if nome in textoUni:
            nomesCertos += 1
    
    score = nomesCertos/len(partesNome)
    if (score >= 0.5):
        return True
    else:
        return False

def validarTipoDocumento(response, texto):
    top = {'class':'negative','score':0, 'trustworthy':False} 
    keywords = {"RG verso": ["lein7116", "de290883", "diretor","registrogeral"], "RG frente": ["dotitular", "carteiradeidentidade", "republicafederativadobrasil","estado"], "CNH": ["carteiranacionaldehabilitacao", "departamentonacionaldetransito", "permissao", "validade", "nregistro"],"CPF": ["ministeriodafazenda", "receitafederal", "comprovantedeinscricao","pessoasfisicas"], "Carteira de Trabalho":["qualificacaocivil", "lein9049", "carteiradetrabalho", "previdenciasocial","18demaiode1995"]}
    textoSemPont = texto.replace(".", "").replace("/", "").replace("-", "").replace(":", "").replace("<", "").replace(">", "").replace('"', "").replace('|', "").replace(" ", "").replace("\n", "").replace("º","").replace("ª","").replace("°","").replace("º","")
    textoUni = unidecode(textoSemPont).lower()
    score = {"RG verso" : 0, "RG frente": 0, "CNH": 0, "CPF": 0, "Carteira de Trabalho": 0}
    try:
        for classe in keywords.keys():
            for word in keywords[classe]:
                if(word in textoUni):
                    print(f"Encontrou a palavra {word} Aumentando o score da {classe}")
                    score[classe] += 0.05
    except Exception as identifier:
        print(identifier)
        print("Eitha deu erro na hora de procurar as palavras")

    #{'class': 'CNH', 'score': 0.001}, {'class': 'CNH xerox', 'score': 0}, {'class': 'CPF', 'score': 0}, 
    # {'class': 'Carteira de Trabalho', 'score': 0.009}, {'class': 'RG Completo', 'score': 0.037}, 
    # {'class': 'RG completo xerox', 'score': 0}, {'class': 'RG frente', 'score': 0.003}, {'class': 'RG verso', 'score': 0.912}]}]    
    print(f"score {score}")
    if(len(response)>0):
        for x in response:
            print(x['class'])
            if(x['class'] == ("RG Completo" or "RG completo xerox")):
                x["score"] += (score["RG verso"] + score["RG frente"])
            if(x['class'] == ("RG verso")):
                x["score"] += score["RG verso"]
            if(x['class'] == ("RG frente")):
                x["score"] += (score['RG frente'])
            if(x['class'] == ("CNH" or "CNH xerox")):
                x["score"] += (score['CNH'])
            if(x['class'] == ("CNH" or "CNH xerox")):
                x["score"] += (score['CNH'])
            if(x['class'] == ("Carteira de Trabalho")):
                x["score"] += (score['Carteira de Trabalho'])
            if(x['class'] == ("CPF")):
                x["score"] += (score['CPF'])

            if(top['score'] < x['score'] and 0.85 < x['score'] ):
                top = x
                top["trustworthy"] = True
            elif(top['score'] < x['score'] ):
                top = x
                top['trustworthy'] = False
            else:
                pass
                #print('pass')
    return top

def validarIdade(texto, cpf):
    print("Validando IDADE")
    #print(texto)
    texto = texto.lower()
    #Tem alguma data que vem separada por hifem?
    #em alguns documentos o cpf vem colado com a data de nascimento gerando uma confusão, por isso foi necessário remover os valores do cpf
    texto = texto.replace("-", "").replace(".","").replace(cpf," ")
    texto = texto.replace("/jan/","/01/").replace("/fev/","/02/").replace("/mar/","/03/").replace("/abr/","/04/").replace("/mat/","/05/").replace("/mai/","/05/").replace("/jun/","/06/").replace("/jul/","/07/").replace("/ago/","/08/").replace("/set/","/09/").replace("/out/","/10/").replace("/nov/","/11/").replace("/dez/","/12/")
    match = re.findall(r'(\d{1,2}[/|\.|\,|\-]\d{1,2}[/|\.|\,|\-]\d{4})',texto)
    #print(texto)
    match = map(convertData, match)
    listaDatas = list(match)
    listaDatas = [x for x in listaDatas if x is not None]
    listaDatas.sort()
    print(f"As data encontradas foram: {listaDatas}")
    #listaDatas = list(datas)
    if (len(listaDatas) >= 1):  
        #0 é o elento mais antigo logo é a data de nascimento se forem encontrada mais de duas datas no documento.
        hoje = datetime.datetime.today()
        dif = hoje - listaDatas[0]
        idade = dif.days/365
        print(f"A idade do agente é: {idade}")
        if (idade>=18):
            return True
        else:
            return False


def convertData(data):
    try:
        data = data.replace(".","/").replace("-","/").replace(",","/")
        data = datetime.datetime.strptime(data, "%d/%m/%Y")
        return data
    except Exception as Erro:
        print(f"Erro data nao reconhecida")
        print(Erro)
        pass

def converterMes(texto):
    texto = texto.lower()
    #Mantendo todas as datas para o formato dd/mm/aaaa
    texto = texto.replace("/jan/","/01/").replace("/fev/","/02/").replace("/mar/","/03/").replace("/abr/","/04/").replace("/mat/","/05/").replace("/jun/","/06/").replace("/jul/","/07/").replace("/ago/","/08/").replace("/set/","/09/").replace("/out/","/10/").replace("/nov/","/11/").replace("/dez/","/12/")
    

def validarDocumento(paginas):
    doc = False
    descricao = u''
    count = 1
    #Checkilist de avaliação dos analistas
    RGVerso = False
    RGFrente = False
    

    listaConfianca = []
    listacpf = []
    listaRGVerso = []
    listaRGFrente = []
    listaNome = []
    listaIdade = []
    isError = False

    for pag in paginas:
        if(pag["ClassesDocumento"]["class"] == "RG verso"):
            RGVerso = True
            #listaRGVerso.append(True)
           # listaRGFrente.append(False)
        elif(pag["ClassesDocumento"]["class"] == "RG frente"):
            RGFrente = True
            #listaRGFrente.append(True)
            #listaRGVerso.append(False)
        elif((pag["ClassesDocumento"]["class"] == "RG Completo" or pag["ClassesDocumento"]["class"] == "RG completo xerox" or pag["ClassesDocumento"]["class"] == "CNH" or pag["ClassesDocumento"]["class"] == "CNH xerox" or pag["ClassesDocumento"]["class"] == "Carteira de Trabalho")):
            RGVerso = True
            RGFrente = True
            #listaRGFrente.append(True)
            #listaRGVerso.append(True)
        else:
            RGVerso = False
            RGFrente = False
            #listaRGFrente.append(False)
            #listaRGVerso.append(False)

        listaConfianca.append(pag["ClassesDocumento"]["trustworthy"])
        listacpf.append(pag["cpfBateDocumento"])
        listaNome.append(pag["nomeBateDocumento"])
        listaRGFrente.append(RGFrente)
        listaRGVerso.append(RGVerso)
        listaIdade.append(pag["maiorIdade"])
        count += 1

    if (True not in listacpf):
        isError = True
        descricao += "o CPF nao foi encontrado; "
    if (True not in listaNome):
        isError = True
        descricao += "o nome nao foi encontrado; "
    if (True not in listaRGVerso):
        isError = True
        descricao += "o verso do RG nao foi encontrado; "
    if (True not in listaRGFrente):
        isError = True
        descricao += "a frente do RG nao foi encontrado ou não foi identificado com o grau de confiança necessária; "
    if (True not in listaConfianca):
        isError = True
        descricao += "nao foi encontrado nenhum documento com um grau de confianca aceitavel; "
    if (True not in listaIdade):
        isError = True
        if(None not in listaIdade):
            descricao += "O colaborador e menor de idade;"
        else:
            descricao += "Nao foi possivel identificar datas no documento;"

    if(isError == False):
        doc = True
        descricao = "O documento esta conforme"
        return doc, descricao
    else:
        doc = False
        descricao = "Documento nao conforme, foram encontrado os seguintes problemas: " + descricao

            

#        descricao = f"""O total de paginas foram: {count-1}
 #       Status CPF por pagina: {listacpf}
  #      Status nome por pagina: {listaNome}       
   #     Status RG Verso por pagina: {listaRGVerso}
    #    Status RG Frente por pagina: {listaRGFrente}
     #   nivel classe e confianca por pagina: {listaConfianca}
      #  """

        descricao = descricao.replace("'",'"')
        return doc, descricao

def validarPagina(nome, cpf, response, texto):
    isnomeAgente = validarNOME(nome.upper(), texto.upper())    
    iscpfAgente = validarCPF(cpf, texto.upper())
    classe = validarTipoDocumento(response, texto)
    maiorIdade = validarIdade(texto, cpf)
    #para uma classe ser considerada valida ela precisa possuir pelo menos o nome ou o cpf do colaborador + uma classe de documento valida com um grau de confiança acima de
    #and classe["trustworthy"] and (classe["class"] != "negative" or classe["class"] != "RG verso" or classe["class"] != "RG frente") and maiorIdade) :
    if (iscpfAgente or isnomeAgente) :
       if (classe["trustworthy"] == True):  
        status = True
        descricao = "Pagina valida"
       else:
        status = False
        descricao = "Documento abaixo da confianca necessaria"
    else:
        if(classe["class"] == "RG frente" and classe["trustworthy"] == True):
            status = True
            descricao = "Frente do RG"
        else:
            status = False
            descricao = "Nao foi encontrado referencia ao colaborador"

    return isnomeAgente, iscpfAgente, classe, status, maiorIdade, descricao


def verificarRecebimento(reqJson):
    main.countTeste += 1
    #print("entra no metodo pela " + main.countTeste + "json para classificação -> " + reqJson)
    print("recebido o arquivo > " + str(main.countTeste))
    #print(reqJson.keys())
    logging.debug(f"Validando JSON para classificar")
    if("Documentos" in reqJson.keys()):
        dic = {'colaboradores' : []}
        code = 200
        print("entrou para verificar")
        for colaborador in reqJson["Documentos"]:
            col = {}
            col["IDdocumento"] = colaborador["Iddocumento"]
            URL = colaborador["Urldocumento"]
            print("Verificar URL -- o json a ser processado é: {reqJson}")
            url_processed = requote_uri(URL)
            
            try:
                res = urllib.request.urlopen(url_processed)
                if(res.code == 200):
                    logging.debug(f"JSON está ok irei adicionar na fila.")
                    #col["code"] = 200
                    col["status"] = 2
                    col["obs"] = 'Recebido com sucesso'
                    dic['colaboradores'].append(col)
                    #Se em algum momento algum doc deu problema ele retornara o erro 400
                    if (code == 200):
                        code = 200
                elif(res.code == 404 or 400 or 405 or 401):
                    logging.debug(f"Falha no download do arquivo do contrato")
                    #print("Devo retornar")
                    #col["code"] = 400
                    col["status"] = 0
                    col["obs"] = "Falha no Download do arquivo " + str(res.reason)
                    dic['colaboradores'].append(col)
                    code = 400
                
            except Exception as erro:
                print (erro)
                col = {}
                #col["code"] = 400
                col["status"] = 0
                col["obs"] = 'Erro -> ' + str(erro)
                code = 400
                dic['colaboradores'].append(col)

        return dic,code              
    else:
        print ("erro")
        #col["code"] = 400
        col["status"] = 0
        col["obs"] = 'Erro -> ' + "Json nao contem o colaborador"
        logging.debug(f"O JSON está no formato incorreto, nao possui colaborador. JSON --> {reqJson}")
        code = 400
        dic['colaboradores'].append(col)
        return dic,code 

## FLuxo de Execução

jsonEntrada ={
    "Documentos":
    [
        {
            "Iddocumento"  : "18",
            "Urldocumento" : "https://contractweb.com.br/documents/arquivos/storage/contract/12902/7694/2018_09//15319252_346_C%C3%93PIA%20DO%20RG%20E%20CPF%20OU%20CARTEIRA%20NACIONAL%20DE%20HABILITA%C3%87%C3%83O%20-%20CNH.pdf", 
            "Nome"         : "CARLOS ANTONIO DA SILVA",
            "Cpf"          : "12362740404"
        },
        {
            "Iddocumento"  : "19",
            "Urldocumento" : "https://contractweb.com.br/documents/arquivos/storage/contract/14923/10737/2018_11//15745037_346_C%C3%93PIA%20DO%20RG%20E%20CPF%20OU%20CARTEIRA%20NACIONAL%20DE%20HABILITA%C3%87%C3%83O%20-%20CNH.pdf", 
            "Nome"         : "YASMIN NETTO DE OLIVEIRA",
            "Cpf"          : "189486537"
        }
        
    ]
}

def deletar_temp(path):
    for photo in path:
        os.remove(photo)
    return "done"

def classificar(jsonEntrada):
    logging.debug(f"Iniciou processo de classificação {jsonEntrada}")
    doc = {}
    response = {}
    doc["colaboradores"] = []
    response["Documentos"] = []

    for colaborador in jsonEntrada["Documentos"]:

        colaborador["pages"] = []
        #Para cada colaborador temos um documento
        documento = {}
        
        file = download_convert(colaborador["Urldocumento"], dpi)

        if(len(file)==0):
            logging.info("Arquivo classificado sem caractere reconhecido")
            continue
        
        #print("Arquivo convertido classificar no watson" + str(file))
        countPag = 1
        for page in file:
            pagina = {}
            watsonResponse = watsonClassifier(page)
            print("Classificar no OCR")
            ocrResponse = detect_document(page)
            print(ocrResponse)
            isnome, iscpf, classe, status, maiorIdade, analisepagina = validarPagina(colaborador["Nome"],colaborador["Cpf"], watsonResponse['images'][0]['classifiers'][0]['classes'], ocrResponse)
            print(classe)
            pagina["nomeBateDocumento"] = isnome
            pagina["cpfBateDocumento"] = iscpf
            pagina["ClassesDocumento"] = classe
            pagina["maiorIdade"] = maiorIdade
            #pagina["statusPaginaValida"] = status
            #pagina["analisepagina"] = analisepagina
            pagina["numeroPagina"] = countPag
                        
            #print(json.dumps(watsonResponse['images'][0]['classifiers'][0]['classes'], indent=2))
            #print(f"O nome está ok {isnome} e o cpf é {iscpf}")
            
            #verificar se é melhor ter esse if que valide as páginas que possuem um minimo de confinça para a classificação
            colaborador["pages"].append(pagina)
            countPag += 1

        qtdPag = len(list(colaborador["pages"]))

        #if(qtdPag > 0):
            #doc["statusDocumentoValido"], descricao = validarDocumento(colaborador["pages"])
        #else:
         #   doc["statusDocumentoValido"] = False
         #   descricao = "Documento nao conforme, " + analisepagina# nao foi encontrada nenhuma referencia do colaborador"
        
       
        doc["colaboradores"].append(colaborador)


        documento["iddocumento"] = colaborador["Iddocumento"]
        #print(documento["statusdocumento"])
        #response["Documentos"].append(documento)

    #deletar_temp(file)
    #print(json.dumps(response, indent=2))

    response['Documentos'] = doc['colaboradores']
    return response

#print(classificar(jsonEntrada))






