# Flask API - Análise de Vídeo com Gemini

Esta API Flask realiza a análise de vídeos com uso da API Gemini da Google, retornando descrições detalhadas de eventos registrados, como ultrapassagens proibidas e identificação de placas.

---

## 🚀 Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/felipemfpeixoto/flaskapi-hackathon.git
cd flaskapi-hackathon
```

---

### 2. Crie o arquivo `.env`

Crie um arquivo chamado `.env` na raiz do projeto com o seguinte conteúdo:

```env
PINECONE_API_KEY=SUA_CHAVE_PINECONE
GEMINI_API_KEY=SUA_CHAVE_GEMINI
HUGGINGFACE_HUB_TOKEN=SEU_TOKEN_HUGGINGFACE_HUB
OPENAI_API_KEY=SUA_CHAVE_OPENAI
HOST_IP=SEU_HOST_IP
```

> Substitua os campos acima por suas credenciais para os respectivos serviços

---

### 3. Instale as dependências

Se estiver usando um ambiente virtual, ative-o primeiro:

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

Depois, instale as dependências:

```bash
pip install -r requirements.txt
```
---


### 4. Configure o acessso ao firebase

Gere um ambiente firebase e conecte-o exportando o json de credenciais e posicionando na raíz do projeto como `firebaseCredentials.json`

---

### 5. Rode a API

```bash
python3 main.py
```

---

## 📫 Contato

Em caso de dúvidas, sugestões ou bugs, abra uma issue neste repositório.
