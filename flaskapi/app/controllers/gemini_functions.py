import os
import time
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
from rag_functions.pinecone_functions import query_db
import os
import json

with open("app\data\law_descriptions_bonitinho.json", "r") as file:
    law_descriptions = json.load(file)

load_dotenv()


def extrair_placa(mocked: bool = True):
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

        video_path = "/Users/infra/Documents/Adapta Challenge/projeto/apiFlask/flaskapi/app/data/ultrapassagens16s.mp4"

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

    final_output = interpretar_com_gpt(gemini_text=gemini_text)

    print("📋 Análise estruturada para infrações:\n", final_output)

    print("\n\n***************************************************************\n\n")

    return final_output

def get_gemini_response_mock():
    return """"
    O vídeo, filmado em um dia chuvoso com pista molhada, mostra uma sequência de veículos em uma rodovia de mão dupla, com uma faixa contínua dupla amarela no centro, indicando **proibição de ultrapassagem** para ambos os sentidos.

**Descrição do que aconteceu:**

1.  **Cenário Inicial:** O vídeo começa com a visão da perspectiva de um veículo (aparentemente um carro, filmando sobre outro carro que está à frente), que está seguindo um comboio na rodovia. À frente do veículo que está sendo filmado (um Toyota Corolla prata), há um caminhão-baú grande de cor branca, e à frente deste, mais dois veículos (uma caminhonete escura e outra mais clara). A pista está visivelmente molhada e há pouca visibilidade devido à chuva e neblina.
2.  **Tentativa de Ultrapassagem:** Por volta de 0:05, o Toyota Corolla prata, que está logo à frente do veículo do cinegrafista, inicia uma manobra de ultrapassagem sobre o caminhão-baú. Ele se desloca para a faixa de sentido contrário, invadindo-a completamente.
3.  **Situação de Perigo:** Enquanto o Corolla está na contramão ao lado do caminhão, um veículo (um carro de cor clara) surge na pista no sentido contrário.
4.  **Manobra de Abortagem:** O motorista do Corolla, percebendo a aproximação perigosa do veículo na contramão, é forçado a abortar bruscamente a ultrapassagem. Ele freia e esterça violentamente para a direita, retornando à sua faixa original e evitando por pouco uma colisão tanto com o caminhão-baú (que ele quase atinge na traseira) quanto com o veículo que vinha no sentido contrário.
5.  **Continuação:** Após a manobra arriscada, o Corolla se alinha novamente atrás do caminhão, e o comboio continua na estrada molhada. Outro veículo se aproxima no sentido contrário logo em seguida.

**Detalhes Importantes:**

*   **Forma da Ultrapassagem:** A ultrapassagem foi feita pela esquerda, invadindo a faixa de rolamento do sentido contrário.
*   **Permissão no Local:** A ultrapassagem **não era permitida** no local. A sinalização de solo, uma **faixa dupla contínua amarela**, indica claramente a proibição de ultrapassagem para ambos os sentidos, conforme o Código de Trânsito Brasileiro. Além disso, as condições climáticas (chuva, pista molhada, baixa visibilidade) tornavam a manobra ainda mais perigosa, independentemente da sinalização.
*   **Consequências Imediatas:** A imprudência resultou em uma situação de alto risco, com a necessidade de uma manobra evasiva perigosa para evitar uma colisão múltipla.

---

**Identificação de Veículos:**

*   **Veículo que realiza a ultrapassagem (Sedan Prata):**
    *   **Modelo:** Toyota Corolla (geração 2014-2019, conhecida como modelo "Altis" ou "GLi" no Brasil).
    *   **Placa:** PCF 9041
*   **Caminhão-Baú (Grande, Branco):**
    *   **Modelo:** Não é possível identificar o modelo exato da cabine, mas o baú é da empresa **"TRLog"** (com o site "www.tfr.com.br" visível) e possui a marca **"RANDON"** (fabricante de implementos rodoviários) visível no para-lama traseiro.
    *   **Placa:** Partes da placa são visíveis (ex: "012-0436" por volta de 0:04), mas não é possível ler a placa completa com clareza para identificação.
*   **Veículo do Cinegrafista:** Não é possível identificar o modelo ou a placa do veículo de onde o vídeo foi filmado, mas a perspectiva sugere que é um carro, provavelmente um sedan, que segue de perto o Toyota Corolla.
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
            "- Possível infração (sim/não):\n\n"
            "Se houver múltiplos veículos, repita essa estrutura apenas para veículos que possuem possíveis infrações."
            "Me retorne APENAS o json sem os caracteres de markdown, pois estou integrando a saída diretamente em minha API!!!"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente que identifica possíveis infrações de trânsito a partir de descrições de vídeos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Gere uma descrição do que aconteceu no vídeo. Leve em conta os detalhes, como de que forma a ultrapassagem foi feita, se era permitida naquele local (segundo sinalização no piso, como faixa dupla contínua ou placa), e outros detalhes que possam ser importantes. Me de também a placa e modelo dos veículos identificados", video_file]
        )

        nodes = query_db(
            query=response.choices[0].message.content,
            index_name="codigo-transito-brasileiro",
            top_k=1
        )

        law_reference = nodes[0].metadata['path']

        ticket = law_descriptions[law_reference]

        return {"analysis": response.choices[0].message.content, "ticket": ticket, "law-reference": law_reference}
    else:
        print("Entrou no mock")
        resposta_mock = """"
            [ { "Placa": "PCF 9041", "Modelo": "Toyota Corolla (geração 2014-2019)", "Cor": "Prata", "Comportamento observado": "Tentativa de ultrapassagem em local proibido, invadindo a faixa de sentido contrário e realizando manobra evasiva perigosa.", "Possível infração": "sim" } ]
        """
        return {resposta_mock, "ticket": None, "law-reference": law_reference}