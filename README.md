# classificador_documentos
Repositório criado para demostração do classificador de documentos.

#Documentos classificados

* CNH
* CNHXerox
* CPF
* Carteira de Trabalho
* RG Completo
* RG CompletoXerox
* RG frente
* RG verso

json de entrada:

{
    "Documentos" : 
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

Envia a resposta para um webservice,
{
  "Documentos": [
    {
      "Iddocumento": "18",
      "Urldocumento": "https://contractweb.com.br/documents/arquivos/storage/contract/12902/7694/2018_09//15319252_346_C%C3%93PIA%20DO%20RG%20E%20CPF%20OU%20CARTEIRA%20NACIONAL%20DE%20HABILITA%C3%87%C3%83O%20-%20CNH.pdf",
      "Nome": "CARLOS ANTONIO DA SILVA",
      "Cpf": "12362740404",
      "pages": [
        {
          "nomeBateDocumento": true,
          "cpfBateDocumento": true,
          "ClassesDocumento": {
            "class": "RG completo xerox",
            "score": 0.713,
            "trustworthy": false
          },
          "maiorIdade": true,
          "numeroPagina": 1
        }
      ]
    },
    {
      "Iddocumento": "19",
      "Urldocumento": "https://contractweb.com.br/documents/arquivos/storage/contract/14923/10737/2018_11//15745037_346_C%C3%93PIA%20DO%20RG%20E%20CPF%20OU%20CARTEIRA%20NACIONAL%20DE%20HABILITA%C3%87%C3%83O%20-%20CNH.pdf",
      "Nome": "YASMIN NETTO DE OLIVEIRA",
      "Cpf": "189486537",
      "pages": [
        {
          "nomeBateDocumento": true,
          "cpfBateDocumento": true,
          "ClassesDocumento": {
            "class": "RG verso",
            "score": 0.9380000000000001,
            "trustworthy": true
          },
          "maiorIdade": true,
          "numeroPagina": 1
        },
        {
          "nomeBateDocumento": true,
          "cpfBateDocumento": false,
          "ClassesDocumento": {
            "class": "RG Completo",
            "score": 0.629,
            "trustworthy": false
          },
          "maiorIdade": null,
          "numeroPagina": 2
        }
      ]
    }
  ]
}
