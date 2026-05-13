from flask import Flask, jsonify, request
from flask_cors import CORS
from tm_devices import DeviceManager
import time
import sys

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"])

# Endereço da Keithley
KEITHLEY_ADDRESS = "USB0::0x05E6::0x2611::4629001::INSTR"

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({"status": "ok", "servico": "Keithley API"})

@app.route('/api/testar_conexao', methods=['GET', 'OPTIONS'])
def testar_conexao():
    if request.method == 'OPTIONS':
        return '', 200
    
    print("\n🔌 Testando conexão com Keithley...")
    try:
        with DeviceManager() as dm:
            keithley = dm.add_smu(KEITHLEY_ADDRESS)
            keithley.write('*IDN?')
            time.sleep(0.2)
            idn = keithley.read()
            print(f"✅ Conectado: {idn.strip()}")
            return jsonify({"status": "conectado", "instrumento": idn.strip()})
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/medir', methods=['POST', 'OPTIONS'])
def medir():
    if request.method == 'OPTIONS':
        return '', 200
    
    print("\n📊 Iniciando medição...")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Body: {request.get_json()}")
    
    try:
        # Obtém os parâmetros do JSON
        data = request.get_json()
        if not data:
            data = {}
        
        num_leituras = data.get('num_leituras', 1)
        modo = data.get('modo_medicao', 'tensao')
        tensao_aplicada = data.get('nivel_tensao_aplicada', 0.0)
        
        print(f"   Parâmetros: leituras={num_leituras}, modo={modo}, tensão={tensao_aplicada}V")
        
        with DeviceManager() as dm:
            keithley = dm.add_smu(KEITHLEY_ADDRESS)
            
            # Configuração
            keithley.write('smua.reset()')
            time.sleep(0.5)
            
            keithley.write('smua.measure.autorangev = smua.AUTORANGE_ON')
            keithley.write('smua.source.levelv = 0.0')
            
            if modo == "tensao":
                keithley.write('smua.measure.func = smua.MEASURE_FUNC_DCVOLTAGE')
                print("   Modo: Tensão")
            else:
                keithley.write('smua.measure.func = smua.MEASURE_FUNC_DCURRENT')
                keithley.write('smua.measure.autorangei = smua.AUTORANGE_ON')
                print("   Modo: Corrente")
            
            if tensao_aplicada > 0:
                keithley.write(f'smua.source.levelv = {tensao_aplicada}')
            
            resultados = []
            
            for i in range(num_leituras):
                print(f"   Medição {i+1}/{num_leituras}...")
                
                keithley.write('smua.source.output = smua.OUTPUT_ON')
                time.sleep(0.2)
                
                if modo == "tensao":
                    keithley.write('print(smua.measure.v())')
                else:
                    keithley.write('print(smua.measure.i())')
                
                time.sleep(0.3)
                resposta = keithley.read()
                
                keithley.write('smua.source.output = smua.OUTPUT_OFF')
                
                try:
                    valor = float(resposta.strip().split()[-1])
                except:
                    valor = 0.0
                
                resultados.append(valor)
                print(f"      Valor: {valor:.6f}")
                
                if i < num_leituras - 1:
                    time.sleep(0.5)
            
            print(f"✅ Medição concluída!")
            
            return jsonify({
                "status": "sucesso",
                "medicoes": resultados,
                "mensagem": f"{len(resultados)} medições realizadas"
            })
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Servidor Keithley (modo debug)")
    print("="*50)
    print("📍 http://localhost:8000")
    print("📡 Endpoints disponíveis:")
    print("   GET  - /api/health")
    print("   GET  - /api/testar_conexao")
    print("   POST - /api/medir")
    print("\n✅ Aguardando requisições...")
    print("="*50 + "\n")
    
    app.run(host='127.0.0.1', port=8000, debug=True, use_reloader=False)