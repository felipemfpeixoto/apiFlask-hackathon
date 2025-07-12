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
GEMINI_API_KEY=sua_api_key_aqui
```

> Substitua `sua_api_key_aqui` pela sua chave de API Gemini.

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

### 4. Rode a API

```bash
python3 main.py
```

A API estará disponível em: [http://localhost:5000](http://localhost:5000)

---

## 📝 Observações

- O vídeo de entrada deve estar no diretório `app/data/` ou ser enviado conforme implementação.

---

## 📫 Contato

Em caso de dúvidas, sugestões ou bugs, entre em contato via [seuemail@exemplo.com] ou abra uma issue neste repositório.
