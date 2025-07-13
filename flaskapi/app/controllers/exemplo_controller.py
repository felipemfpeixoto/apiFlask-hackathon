from flask import request, jsonify
import os
import requests
from urllib.parse import urlparse
from .gemini_functions import extrair_placa
from firebase_module import inicializar_firebase, salvar_envio_no_firestore
from datetime import datetime

def raiz_requisicao():
    print("\n\n****************** CHAMOU EXEMPLO ******************\n\n")

    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem JSON válido"}), 400
    
    inicializar_firebase()

    user_id = data.get("userID")
    video_url = data.get("videoURL")
    date = data.get("date")
    location = data.get("location", {})  # dicionário com latitude e longitude

    print(f"userID: {user_id}")
    print(f"videoURL: {video_url}")
    print(f"date: {date}")
    print(f"location: {location}")

    # MARK: Aqui, retornar para o usuário e continuar a execução das APIs

    caminho_arquivo = baixar_video(video_url)

    final_output = extrair_placa(mocked=False, video_path=caminho_arquivo)

    """"
    [
        {
            'Placa': 'PCF 9041', 
            'Modelo': 'Toyota Corolla (geração 2014-2019)', 
            'Cor': 'Prata', 
            'Comportamento observado': 'Tentativa de ultrapassagem em local proibido com faixa dupla contínua, invadindo a faixa de sentido contrário e realizando manobra evasiva perigosa.', 
            'Possível infração': 'sim', 
            'law_references': [
                {
                    'law_reference': 'CAPÍTULO XV - Art. 203 - V', 
                    'ticket': 'Ultrapassar pela contramão onde houver linha dupla contínua ou simples contínua amarela.', 
                    'score': 0.650156438
                }, 
                {
                    'law_reference': 'CAPÍTULO XV - Art. 191 - Parágrafo único', 
                    'ticket': 'Forçar passagem entre veículos que, em sentidos opostos, estão próximos na ultrapassagem, com reincidência em 12 meses (multa em dobro).', 
                    'score': 0.645095587
                }, 
                {
                    'law_reference': 'CAPÍTULO XV - Art. 203 - I', 
                    'ticket': 'Ultrapassar pela contramão em curvas, aclives e declives sem visibilidade.', 
                    'score': 0.622634828    
                }, 
                {
                    'law_reference': 'CAPÍTULO XV - Art. 203 - IV', 
                    'ticket': 'Ultrapassar pela contramão veículo parado em fila (sinais, porteiras, cruzamentos, impedimentos).', 
                    'score': 0.616180301
                }, 
                {
                    'law_reference': 'CAPÍTULO XV - Art. 186 - II', 
                    'ticket': 'Transitar pela contramão em vias de sentido único de circulação.', 
                    'score': 0.615073442
                }
            ]
        }
    ]
    """

    intancia_banco = {
        "userID": user_id,
        "videoURL": video_url,
        "date": datetime.now(), # MARK: Não sei se ta funcionando
        "location": location,
        "infracao": final_output[0],
        "status": "pendente"
    }

    salvar_envio_no_firestore(dados_envio=intancia_banco)

    apagar_video(caminho_arquivo)

    return jsonify({
        "mensagem": "Dados recebidos com sucesso!",
        "userID": user_id,
        "videoURL": video_url,
        "date": date,
        "location": location
    })

def baixar_video(url, pasta_destino="videos"):
    # Criar pasta local para salvar o vídeo, se necessário
    os.makedirs(pasta_destino, exist_ok=True)

    try:
        # Extrair o nome do arquivo da URL
        nome_arquivo = os.path.basename(urlparse(url).path)
        if not nome_arquivo:
            nome_arquivo = "video_baixado.mp4"

        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

        # Baixar o vídeo
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(caminho_arquivo, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Vídeo salvo em: {caminho_arquivo}")
        return caminho_arquivo

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return None
    
def apagar_video(caminho_arquivo):
    try:
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            print(f"Arquivo removido: {caminho_arquivo}")
            return True
        else:
            print(f"Arquivo não encontrado: {caminho_arquivo}")
            return False
    except Exception as e:
        print(f"Erro ao tentar remover o arquivo: {e}")
        return False