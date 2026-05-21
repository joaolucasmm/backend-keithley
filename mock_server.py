import sys
import os
import math
import random
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Determina o caminho base (funciona tanto em script quanto executável)
if getattr(sys, 'frozen', False):
    # Rodando como executável PyInstaller
    base_path = sys._MEIPASS
else:
    # Rodando como script Python
    base_path = os.path.dirname(os.path.abspath(__file__))

# Caminho para o frontend
frontend_path = os.path.join(base_path, 'frontend', 'dist')

# Configura o Flask para servir o frontend se existir
if os.path.exists(frontend_path):
    app = Flask(__name__, 
                static_folder=frontend_path,
                static_url_path='',
                template_folder=frontend_path)
    
    # Rota para servir o index.html do Vue
    @app.route('/')
    def serve_vue():
        return send_from_directory(frontend_path, 'index.html')
    
    # Rota para servir arquivos estáticos do Vue
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(frontend_path, path)
else:
    app = Flask(__name__)
    print(f"Aviso: Frontend não encontrado em {frontend_path}")

# Configuração CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuração do modo mock
MOCK_CONFIG = {
    "modo": "realista",  # "realista", "sine", "random", "linear", "constante"
    "ruido": 0.001,      # Nível de ruído (em % do valor)
    "delay_artificial": 0  # Delay artificial em segundos (0 = sem delay)
}

# Parâmetros para modos específicos
MODO_DATA = {
    "sine": {
        "amplitude": 1.0,
        "frequencia": 0.5,
        "fase": 0
    },
    "linear": {
        "inicio": 0,
        "fim": 10,
        "step": 1
    },
    "random": {
        "min": 0,
        "max": 10
    }
}

# Contador para simular variação temporal
contador = 0

def gerar_valor_mock(modo_medicao, parametros):
    """
    Gera valores mock baseado no modo configurado
    """
    global contador
    contador += 1
    
    num_leituras = parametros.get('num_leituras', 5)
    delay = parametros.get('delay_entre_leituras', 0.5)
    modo = parametros.get('modo_medicao', 'tensao')
    
    resultados = []
    
    for i in range(num_leituras):
        # Delay artificial para simular medição real
        if MOCK_CONFIG["delay_artificial"] > 0:
            time.sleep(MOCK_CONFIG["delay_artificial"])
        
        # Gera valor base de acordo com o modo configurado
        if MOCK_CONFIG["modo"] == "constante":
            valor_base = 1.0
            
        elif MOCK_CONFIG["modo"] == "random":
            # Valores aleatórios entre min e max
            valor_base = random.uniform(
                MODO_DATA["random"]["min"],
                MODO_DATA["random"]["max"]
            )
            
        elif MOCK_CONFIG["modo"] == "sine":
            # Onda senoidal
            t = contador * delay + i * delay
            amplitude = MODO_DATA["sine"]["amplitude"]
            frequencia = MODO_DATA["sine"]["frequencia"]
            fase = MODO_DATA["sine"]["fase"]
            valor_base = amplitude * math.sin(2 * math.pi * frequencia * t + fase)
            
        elif MOCK_CONFIG["modo"] == "linear":
            # Valores variando linearmente com cada medição
            inicio = MODO_DATA["linear"]["inicio"]
            fim = MODO_DATA["linear"]["fim"]
            step = MODO_DATA["linear"]["step"]
            valor_base = inicio + (contador * step) % (fim - inicio)
            
        elif MOCK_CONFIG["modo"] == "exponencial":
            # Decaimento exponencial
            valor_base = math.exp(-(contador + i) * 0.1)
            
        else:  # "realista" (padrão)
            # Simula medições típicas de um diodo ou resistor
            tensao_aplicada = parametros.get('nivel_tensao_aplicada', 0)
            if modo == "tensao":
                # Medição de tensão - simula ruído em torno de 2.5V
                valor_base = 2.5 + random.uniform(-0.1, 0.1)
            else:
                # Medição de corrente - simula resposta de um diodo
                if tensao_aplicada < 0.7:
                    valor_base = random.uniform(0, 1e-6)  # Corrente de fuga
                else:
                    # Corrente exponencial no diodo
                    valor_base = 1e-6 * math.exp((tensao_aplicada - 0.7) / 0.025)
        
        # Adiciona ruído
        ruido = valor_base * MOCK_CONFIG["ruido"] * random.uniform(-1, 1)
        valor = valor_base + ruido
        
        # Limita valores para serem realistas
        if modo == "tensao":
            valor = max(0, min(200, valor))  # 0-200V
        else:
            valor = max(0, min(1.5, valor))  # 0-1.5A
        
        resultados.append(round(valor, 9))
    
    return resultados

def gerar_valor_iv_mock(parametros):
    """
    Gera valores mock para medição simultânea I/V
    """
    global contador
    contador += 1
    
    num_leituras = parametros.get('num_leituras', 5)
    delay = parametros.get('delay_entre_leituras', 0.5)
    modo = parametros.get('modo', 'tensao_fixa')
    valor_fixo = parametros.get('valor_fixo', 1.0)
    
    resultados = []
    
    for i in range(num_leituras):
        if MOCK_CONFIG["delay_artificial"] > 0:
            time.sleep(MOCK_CONFIG["delay_artificial"])
        
        # Simula características realistas
        if modo == "tensao_fixa":
            # Aplicando tensão, medindo corrente
            tensao = valor_fixo
            
            # Simula corrente de um diodo ou resistor
            if tensao < 0.7:
                corrente = random.uniform(0, 1e-6)  # Corrente de fuga (nA)
            else:
                # Modelo do diodo: I = Is * exp(V/(n*Vt))
                Is = 1e-12  # Corrente de saturação
                Vt = 0.025  # Tensão térmica
                n = 1.5     # Fator de idealidade
                corrente_base = Is * math.exp(tensao / (n * Vt))
                
                # Adiciona ruído
                ruido = corrente_base * MOCK_CONFIG["ruido"] * random.uniform(-1, 1)
                corrente = corrente_base + ruido
        
        else:  # corrente_fixa
            # Aplicando corrente, medindo tensão
            corrente = valor_fixo
            
            # Simula tensão em um diodo ou resistor
            # Lei de Ohm para resistor de 1k
            if corrente < 1e-6:  # Corrente muito baixa
                tensao = random.uniform(0, 0.1)
            else:
                tensao_base = corrente * 1000  # R = 1kΩ
                ruido = tensao_base * MOCK_CONFIG["ruido"] * random.uniform(-1, 1)
                tensao = tensao_base + ruido
        
        potencia = corrente * tensao
        
        resultados.append({
            'corrente': round(corrente, 12),
            'tensao': round(tensao, 6),
            'potencia': round(potencia, 9)
        })
        
        if i < num_leituras - 1:
            time.sleep(delay)
    
    return resultados

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        "status": "ok",
        "servico": "Keithley Controller API (MOCK)",
        "modo_mock": MOCK_CONFIG["modo"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/testar_conexao', methods=['GET', 'OPTIONS'])
def testar_conexao():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Simula resposta da Keithley
    time.sleep(0.1)
    return jsonify({
        "status": "conectado",
        "instrumento": f"Keithley 2611B MOCK (Modo: {MOCK_CONFIG['modo']})"
    })

@app.route('/api/medir', methods=['POST', 'OPTIONS'])
def medir():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"\n[MOCK] 📊 Medição solicitada: {data}")
        
        resultados = gerar_valor_mock("tensao", data)
        
        print(f"[MOCK] ✅ Resultados: {resultados}")
        
        return jsonify({
            "status": "sucesso",
            "medicoes": resultados,
            "mensagem": f"{len(resultados)} medições realizadas (MOCK)",
            "mock_mode": MOCK_CONFIG["modo"]
        })
        
    except Exception as e:
        print(f"[MOCK] ❌ Erro: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/medir_iv', methods=['POST', 'OPTIONS'])
def medir_iv():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"\n[MOCK] 📊 Medição IV solicitada: {data}")
        
        resultados = gerar_valor_iv_mock(data)
        
        print(f"[MOCK] ✅ Resultados IV: {len(resultados)} leituras")
        
        return jsonify({
            "status": "sucesso",
            "medicoes": resultados,
            "mensagem": f"{len(resultados)} medições IV realizadas (MOCK)",
            "mock_mode": MOCK_CONFIG["modo"]
        })
        
    except Exception as e:
        print(f"[MOCK] ❌ Erro: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/mock/config', methods=['GET', 'POST', 'OPTIONS'])
def mock_config():
    """Endpoint para configurar o comportamento do mock"""
    if request.method == 'OPTIONS':
        return '', 200
    
    global MOCK_CONFIG, MODO_DATA, contador
    
    if request.method == 'GET':
        return jsonify({
            "config": MOCK_CONFIG,
            "modo_data": MODO_DATA,
            "contador": contador
        })
    
    else:  # POST
        data = request.get_json()
        
        if 'modo' in data:
            MOCK_CONFIG["modo"] = data["modo"]
        
        if 'ruido' in data:
            MOCK_CONFIG["ruido"] = max(0, min(0.5, data["ruido"]))
        
        if 'delay_artificial' in data:
            MOCK_CONFIG["delay_artificial"] = max(0, min(5, data["delay_artificial"]))
        
        if 'amplitude' in data and MOCK_CONFIG["modo"] == "sine":
            MODO_DATA["sine"]["amplitude"] = data["amplitude"]
        
        if 'frequencia' in data and MOCK_CONFIG["modo"] == "sine":
            MODO_DATA["sine"]["frequencia"] = data["frequencia"]
        
        if 'min' in data and MOCK_CONFIG["modo"] == "random":
            MODO_DATA["random"]["min"] = data["min"]
        
        if 'max' in data and MOCK_CONFIG["modo"] == "random":
            MODO_DATA["random"]["max"] = data["max"]
        
        if 'reset_counter' in data and data["reset_counter"]:
            contador = 0
        
        return jsonify({
            "status": "configurado",
            "config": MOCK_CONFIG,
            "modo_data": MODO_DATA
        })

@app.route('/api/mock/reset', methods=['POST', 'OPTIONS'])
def mock_reset():
    """Reseta o contador de medições"""
    if request.method == 'OPTIONS':
        return '', 200
    
    global contador
    contador = 0
    return jsonify({"status": "resetado", "contador": contador})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎭 SERVIDOR MOCK KEITHLEY 2611B")
    print("="*60)
    print(f"📍 API disponível em: http://localhost:8000")
    print(f"📁 Frontend path: {frontend_path if os.path.exists(frontend_path) else 'Não encontrado'}")
    print("\n📡 Modos de simulação disponíveis:")
    print("   - realista:  Simula comportamentos reais de componentes")
    print("   - random:    Valores aleatórios")
    print("   - sine:      Onda senoidal")
    print("   - linear:    Variação linear")
    print("   - constante: Valor fixo")
    print("   - exponencial: Decaimento exponencial")
    print("\n⚠️  Modo MOCK ativo - Nenhum hardware real está sendo usado")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)