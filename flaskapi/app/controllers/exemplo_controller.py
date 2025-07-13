from flask import request, jsonify
import os
import requests
from urllib.parse import urlparse
from .gemini_functions import extrair_placa

def raiz_requisicao():
    print("\n\n****************** CHAMOU EXEMPLO ******************\n\n")

    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem JSON válido"}), 400

    user_id = data.get("userID")
    video_url = data.get("videoURL")
    date = data.get("date")
    location = data.get("location", {})  # dicionário com latitude e longitude

    print(f"userID: {user_id}")
    print(f"videoURL: {video_url}")
    print(f"date: {date}")
    print(f"location: {location}")

    caminho_arquivo = baixar_video(video_url)

    extrair_placa(mocked=False, video_path=caminho_arquivo)

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