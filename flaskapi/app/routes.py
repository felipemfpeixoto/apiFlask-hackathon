from flask import jsonify
from .controllers import exemplo_controller, gemini_functions

def init_routes(app):
    @app.route('/')
    def home():
        return jsonify({"mensagem": "API Flask rodando!"})

    app.route('/exemplo', methods=['GET'])(exemplo_controller.exemplo)
    app.route('/extrair_placa', methods=['GET'])(gemini_functions.extrair_placa)
