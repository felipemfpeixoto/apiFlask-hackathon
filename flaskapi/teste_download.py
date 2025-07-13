from app.controllers import exemplo_controller, gemini_functions
from firebase_module import inicializar_firebase, salvar_envio_no_firestore
from datetime import datetime
from app.controllers.gemini_functions import extrair_placa

# url = "https://firebasestorage.googleapis.com:443/v0/b/hackatonadapta.firebasestorage.app/o/videos%2Fdemo_user%2F69D41C50-6768-4441-816B-033DC8F326F3.mov?alt=media&token=19501ded-8cc1-4c1a-bc93-5c99dd37f099"
# caminho = exemplo_controller.baixar_video(url)
# if caminho:
#     print("Vídeo baixado com sucesso:", caminho)

#     exemplo_controller.apagar_video(caminho)

# caminho = "flaskapi/videos/videos%2Fdemo_user%2F2AB76BF8-0178-420A-BE49-ED98353938C4.mov"

# final_output = gemini_functions.extrair_placa(video_path=caminho)

# print(final_output)

# print("\n\n*************************** Instanciando e salvando no firebase ***************************\n\n")

# inicializar_firebase()

# instancia = {
#         "userID": "exemplo",
#         "videoURL": "exemplo",
#         "date": datetime.now(),
#         "location": [0.0, 0.0],
#         "infracao": final_output[0]
#     }

# salvar_envio_no_firestore(dados_envio=instancia)

extrair_placa()