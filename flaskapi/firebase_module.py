import firebase_admin
from firebase_admin import credentials, firestore

# Inicialização (faça isso uma única vez no seu app)
def inicializar_firebase(caminho_credencial_json="/Users/infra/Documents/Adapta Challenge/projeto/apiFlask/firebaseCredentials.json"):
    if not firebase_admin._apps:
        cred = credentials.Certificate(caminho_credencial_json)
        firebase_admin.initialize_app(cred)
    print("Firebase inicializado")

# Função para salvar no Firestore
def salvar_envio_no_firestore(dados_envio: dict):
    try:
        # Inicializa Firebase se necessário
        # inicializar_firebase()

        # Conecta ao Firestore
        db = firestore.client()

        # Adiciona o dicionário à coleção 'envios'
        doc_ref = db.collection("Envios").add(dados_envio)

        print(f"Documento criado com ID: {doc_ref[1].id}")
        return doc_ref[1].id

    except Exception as e:
        print(f"Erro ao salvar no Firestore: {e}")
        return None
