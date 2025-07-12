import time
from google import genai
from dotenv import load_dotenv
from rag_functions.pinecone_functions import query_db
import os
import json

with open("app\data\law_descriptions_bonitinho.json", "r") as file:
    law_descriptions = json.load(file)

load_dotenv()

def extrair_placa():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY não definida no .env")

    client = genai.Client(api_key=api_key)

    video_file = client.files.upload(
        # TODO: change this path to make a donload according to the url
        file="/Users/infra/Documents/Adapta Challenge/projeto/apiFlask/flaskapi/app/data/ultrapassagens16s.mp4" # TODO: Isso aqui ta hardcoded. Mudar de acordo com o vídeo enviado para a API
    )

    file_name = video_file.name

    while video_file.state.name == "PROCESSING":
        time.sleep(2)
        print("status:", video_file.state.name)
        video_file = client.files.get(name=file_name)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["Gere uma descrição do que aconteceu no vídeo. Leve em conta os detalhes, como de que forma a ultrapassagem foi feita, se era permitida naquele local (segundo sinalização no piso, como faixa dupla contínua ou placa), e outros detalhes que possam ser importantes. Me de também a placa e modelo dos veículos identificados", video_file]
    )
    
    nodes = query_db(
        query=response.text,
        index_name="codigo-transito-brasileiro",
        top_k=1
    )

    referencia_juridica = nodes[0].metadata['path']
    
    ticket = law_descriptions[referencia_juridica]
    

    return response.text