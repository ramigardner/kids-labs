import os
import json
import threading
import time
import random
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from garden_state import GardenState
from hash_chain import MiniBlockchain
from challenges import ChallengeManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aspr-kids-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar componentes del jardín
garden = GardenState()
blockchain = MiniBlockchain()
challenge_mgr = ChallengeManager()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# API estilo ASPR (endpoints educativos)
@app.route('/verify')
def verify():
    """Simula el endpoint /verify del nodo ASPR"""
    target = request.args.get('animal', 'all')
    if target == 'all':
        data = garden.get_all_karma()
    else:
        data = garden.get_animal_karma(target)
    return jsonify({
        "verified_by": "ASPR Kids Node v1.0",
        "found": True,
        "data": data,
        "chain_tip": blockchain.get_latest_hash()[:8]
    })

@app.route('/chain/latest')
def chain_latest():
    """Último bloque de la cadena visual"""
    return jsonify(blockchain.get_latest_block())

@app.route('/chain/all')
def chain_all():
    """Todos los bloques para visualización"""
    return jsonify(blockchain.get_all_blocks())

# SocketIO: eventos para actualizaciones en tiempo real
@socketio.on('connect')
def handle_connect():
    print("Cliente conectado")
    emit('garden_update', garden.get_full_state())

@socketio.on('request_update')
def handle_update_request():
    """El cliente pide el estado actual"""
    emit('garden_update', garden.get_full_state())
    emit('chain_update', blockchain.get_all_blocks())

@socketio.on('run_challenge')
def handle_run_challenge(data):
    """Ejecuta el código modificado por el niño para un desafío"""
    animal = data.get('animal')
    code = data.get('code')
    challenge_id = data.get('challenge_id')

    try:
        result = challenge_mgr.run_challenge(animal, code, challenge_id)
        # Actualizar el jardín con el nuevo comportamiento (simulación)
        garden.update_animal_logic(animal, result.get('new_karma', 0.5))
        # Añadir bloque con la acción realizada
        blockchain.add_block({
            "event": "challenge_run",
            "animal": animal,
            "result": result.get('message', '')
        })
        emit('challenge_result', result)
        emit('garden_update', garden.get_full_state())
        emit('chain_update', blockchain.get_all_blocks())
    except Exception as e:
        emit('challenge_result', {"success": False, "message": f"Error: {str(e)}"})

@socketio.on('simulate_round')
def handle_simulate_round():
    """Avanza una ronda de simulación (reportes de animales)"""
    garden.simulate_round()
    blockchain.add_block({
        "event": "round_completed",
        "karma_snapshot": garden.get_all_karma()
    })
    emit('garden_update', garden.get_full_state())
    emit('chain_update', blockchain.get_all_blocks())

# Hilo de fondo para simular actividad automática
def background_simulation():
    while True:
        time.sleep(15)  # cada 15 segundos una ronda automática
        garden.simulate_round()
        blockchain.add_block({
            "event": "auto_round",
            "karma_snapshot": garden.get_all_karma()
        })
        socketio.emit('garden_update', garden.get_full_state())
        socketio.emit('chain_update', blockchain.get_all_blocks())

if __name__ == '__main__':
    threading.Thread(target=background_simulation, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5050, debug=True)