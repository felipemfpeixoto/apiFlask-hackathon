from flask import jsonify

def exemplo():
    return jsonify({"mensagem": "Rota de exemplo funcionando!"})
