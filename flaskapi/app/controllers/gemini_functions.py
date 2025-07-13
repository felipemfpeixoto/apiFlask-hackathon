import os
import time
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
from rag_functions.pinecone_functions import query_db
import os
import json
from app.controllers._utils import get_json_from_string
# without os.path.join
# with open("app\data\law_descriptions_bonitinho.json", "r") as file:
# with os.path.join
with open(os.path.join("app", "data", "law_descriptions_bonitinho.json"), "r", encoding="utf8") as file:
    law_descriptions = json.load(file)

load_dotenv()


def extrair_placa(mocked: bool = True, video_path: str = None):
    # Google Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não definida no .env")

    # OpenAI API Key
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # if not client.api_key:
    #     raise ValueError("OPENAI_API_KEY não definida no .env")

    # Inicializa cliente Gemini
    if not mocked:
        client = genai.Client(api_key=api_key)

        # video_path = "/Users/infra/Documents/Adapta Challenge/projeto/apiFlask/flaskapi/app/data/ultrapassagens16s.mp4"

        # Upload do vídeo
        video_file = client.files.upload(file=video_path)
        file_name = video_file.name

        # Aguarda processamento
        while video_file.state.name == "PROCESSING":
            print("Aguardando processamento do vídeo...")
            time.sleep(2)
            video_file = client.files.get(name=file_name)

        # Análise com Gemini
        gemini_prompt = (
            "Gere uma descrição do que aconteceu no vídeo. Leve em conta os detalhes, como de que forma "
            "a ultrapassagem foi feita, se era permitida naquele local (segundo sinalização no piso, como faixa dupla contínua ou placa), "
            "e outros detalhes que possam ser importantes. Me dê também a placa e modelo dos veículos identificados."
        )
        gemini_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[gemini_prompt, video_file]
        )
        gemini_text = gemini_response.text
    else:
        print("\n\n****** ENTROU NO MOCKED *********\n\n")
        gemini_text = get_gemini_response_mock()

    
    print("🔍 Resposta do Gemini:\n", gemini_text)

    print("\n\n***************************************************************\n\n")

    structured_output = interpretar_com_gpt(gemini_text=gemini_text, mock=False)
    
    final_output = add_law_references(structured_output)

    print("📋 Análise estruturada para infrações:\n", final_output)

    print("\n\n***************************************************************\n\n")

    return final_output

def get_gemini_response_mock():
    return """"
    Com base no vídeo, segue a descrição detalhada do ocorrido:

**Descrição do Ocorrido:**

O vídeo é gravado de uma câmera posicionada no topo da cabine de um caminhão (aparentemente uma carreta), mostrando a perspectiva para frente. A pista está molhada, indicando que está chovendo ou choveu recentemente, e há spray de água sendo levantado pelos veículos.

A rodovia é de pista simples, com uma faixa em cada sentido. A sinalização horizontal no asfalto é de **faixa dupla contínua amarela**, indicando que a ultrapassagem é proibida para ambos os sentidos de tráfego naquele trecho. Além disso, a manobra ocorre em uma **curva**, o que agrava a situação de perigo e é outro fator que, por si só, proíbe a ultrapassagem segundo o Código de Trânsito Brasileiro (CTB).

Um veículo branco, um sedan, tenta realizar uma ultrapassagem arriscada. Ele sai de trás de outro caminhão (um caminhão-tanque de cor escura, que está à frente do caminhão que filma) e avança para a contramão para tentar ultrapassar ambos os caminhões.

No momento em que o veículo branco está na contramão, se aproximando da lateral do caminhão que filma e já tendo ultrapassado o caminhão-tanque, um **veículo vindo em sentido contrário** (um carro de cor clara, possivelmente um SUV ou hatch) aparece na pista.

Sem espaço para completar a ultrapassagem e com o veículo vindo na direção oposta, o carro branco é forçado a "cortar" bruscamente e se espremer entre o caminhão que filma e o caminhão-tanque que ele havia acabado de ultrapassar. A manobra é extremamente perigosa, com o carro branco ficando a centímetros de colidir com a lateral do caminhão que filma e o veículo que vinha na contramão. Ele consegue se encaixar na faixa de rolamento por pouco, evitando uma colisão frontal com o veículo que se aproximava e uma possível colisão lateral com o caminhão que o filmava.

**Legalidade da Manobra:**

A ultrapassagem realizada pelo veículo branco foi **flagrantemente ilegal e extremamente perigosa** por vários motivos:
1.  **Faixa Dupla Contínua Amarela:** Proíbe expressamente a ultrapassagem para ambos os sentidos de tráfego.
2.  **Curva:** Ultrapassagens em curvas são proibidas devido à visibilidade reduzida e ao alto risco de colisão frontal.
3.  **Presença de Veículo em Sentido Contário:** O condutor não avaliou a presença de tráfego no sentido oposto antes de iniciar a manobra, colocando-se e a terceiros em risco iminente.
4.  **Condições Climáticas/Visibilidade:** A pista molhada e a provável chuva reduzem a aderência dos pneus e a visibilidade, tornando manobras arriscadas ainda mais perigosas.

**Veículos Identificados:**

*   **Veículo que realiza a ultrapassagem (sedan branco):**
    *   **Placa:** PCF 9041
    *   **Modelo:** Toyota Corolla (geração que circulou aproximadamente entre 2008 e 2014, conhecido como "Brad Pitt" no Brasil, ou a geração imediatamente anterior ao modelo que começou a ter LEDs nos faróis traseiros)

*   **Caminhão que grava o vídeo:**
    *   **Placa:** Não visível (somente a parte superior do baú/carroceria).
    *   **Modelo:** Não é possível determinar o modelo exato do caminhão, mas o baú/carroceria traseira possui uma marcação com o site **"www.igr.com.br"**, sugerindo ser um veículo da empresa IGR Transportes.

*   **Caminhão-tanque sendo ultrapassado:**
    *   **Placa:** Não visível.
    *   **Modelo:** Não é possível determinar o modelo ou marca, apenas que é um caminhão-tanque de cor escura.
    """

def interpretar_com_gpt(gemini_text: str, mock: bool = True) -> str:
    if not mock:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = (
            "A seguir está uma descrição textual de uma cena de trânsito analisada por IA:\n\n"
            f"{gemini_text}\n\n"
            "Com base nessa descrição, extraia apenas informações relacionadas a veículos identificáveis, estruturando da seguinte forma em um json que possua várias possíveis infrações (uma lista):\n\n"
            "- Placa:\n"
            "- Modelo:\n"
            "- Cor:\n"
            "- Comportamento observado:\n"
            "- Possível infração: (sim/não)\n\n"
            "Se houver múltiplos veículos, repita essa estrutura apenas para veículos que possuem possíveis infrações."
            "Me retorne APENAS o a lista com os elementos json dentro, SEM os caracteres de markdown, e com as chaves dos itens EXATAMENTE como estao escritas acima, pois estou integrando a saída diretamente em minha API!!!"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente que identifica possíveis infrações de trânsito a partir de descrições de vídeos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        json_response = get_json_from_string(response.choices[0].message.content.strip())
    
    else:
        print("Entrou no mock")
        resposta_mock = """"
            [ { "Placa": "PCF 9041", "Modelo": "Toyota Corolla (geração 2014-2019)", "Cor": "Prata", "Comportamento observado": "Tentativa de ultrapassagem em local proibido com faixa dupla contínua, invadindo a faixa de sentido contrário e realizando manobra evasiva perigosa.", "Possível infração": "sim" } ]
        """

        json_response = get_json_from_string(resposta_mock)

    print("****************************************")
    print("Resposta do GPT: \n")
    print(json_response)
    print("****************************************")

    return json_response

def add_law_references(structured_output: list) -> list:
    """Add law references to the structured output based on the infractions detected via RAG."""
    
    for idx, item in enumerate(structured_output):
        if item['Possível infração'] == "sim":
            nodes = query_db(
                query=item['Comportamento observado'],
                index_name="codigo-transito-brasileiro",
                k=5
            )

            # list comprehension style
            # law_references = [{'law_reference': node['path'],
            #                    'ticket': law_descriptions[node['path']],
            #                    'score': node['score']} for node in nodes if node['score'] > 0.1]
            
            # non list comprehension style
            law_references = []
            for node in nodes:
                if node['score'] > 0.6:
                    law_reference = {
                        'law_reference': node['path'],
                        'ticket': law_descriptions[node['path']],
                        'score': node['score']
                    }
                    law_references.append(law_reference)
            
            structured_output[idx]['law_references'] = law_references
                        
        else:
            structured_output[idx]['law_references'] = None

    return structured_output