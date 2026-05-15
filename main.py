from flask import Flask, request, jsonify
from flask_cors import CORS
from tm_devices import DeviceManager
import time

app = Flask(__name__)

# Configuração CORS mais completa
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Endereço da Keithley
KEITHLEY_ADDRESS = "USB0::0x05E6::0x2611::4629001::INSTR"

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({"status": "ok", "servico": "Keithley Controller API"})

@app.route('/api/testar_conexao', methods=['GET', 'OPTIONS'])
def testar_conexao():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("🔄 Testando conexão com a Keithley...")
        with DeviceManager() as dm:
            keithley = dm.add_smu(KEITHLEY_ADDRESS)
            keithley.write("*IDN?")
            time.sleep(0.2)
            idn = keithley.read()
            print(f"✅ Conectado a: {idn}")
            return jsonify({"status": "conectado", "instrumento": idn.strip()})
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/medir', methods=['POST', 'OPTIONS'])
def medir():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"\n📊 Dados recebidos do frontend: {data}")
        
        num_leituras = data.get('num_leituras', 5)
        delay = data.get('delay_entre_leituras', 0.5)
        modo = data.get('modo_medicao', 'tensao')
        tensao_aplicada = data.get('nivel_tensao_aplicada', 0.0)
        
        print(f"   - Leituras: {num_leituras}")
        print(f"   - Modo: {modo}")
        print(f"   - Delay: {delay}s")
        print(f"   - Tensão aplicada: {tensao_aplicada}V")
        
        resultados = []
        
        with DeviceManager() as dm:
            keithley = dm.add_smu(KEITHLEY_ADDRESS)
            
            # Configuração
            keithley.write('smua.reset()')
            time.sleep(0.5)
            
            keithley.write('smua.measure.autorangev = smua.AUTORANGE_ON')
            keithley.write('smua.source.levelv = 0.0')
            
            if modo == "tensao":
                keithley.write('smua.measure.func = smua.MEASURE_FUNC_DCVOLTAGE')
            else:
                keithley.write('smua.measure.func = smua.MEASURE_FUNC_DCURRENT')
                keithley.write('smua.measure.autorangei = smua.AUTORANGE_ON')
            
            if tensao_aplicada > 0:
                keithley.write(f'smua.source.levelv = {tensao_aplicada}')
            
            for i in range(num_leituras):
                print(f"   📈 Medição {i+1}/{num_leituras}...")
                
                keithley.write('smua.source.output = smua.OUTPUT_ON')
                time.sleep(0.1)
                
                if modo == "tensao":
                    keithley.write('print(smua.measure.v())')
                else:
                    keithley.write('print(smua.measure.i())')
                
                time.sleep(0.2)
                resposta = keithley.read()
                
                keithley.write('smua.source.output = smua.OUTPUT_OFF')
                
                try:
                    valor = float(resposta.strip().split()[-1])
                except:
                    valor = 0.0
                
                resultados.append(valor)
                print(f"      Valor: {valor:.6f}")
                
                if i < num_leituras - 1:
                    time.sleep(delay)
        
        print(f"✅ Medição concluída!")
        
        return jsonify({
            "status": "sucesso",
            "medicoes": resultados,
            "mensagem": f"{len(resultados)} medições realizadas com sucesso"
        })
        
    except Exception as e:
        print(f"❌ Erro durante a medição: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# ============================================
# NOVO ENDPOINT: Medição I/V Simultânea
# ============================================
@app.route('/api/medir_iv', methods=['POST', 'OPTIONS'])
def medir_iv():
    """Medição simultânea de corrente e tensão"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"\n⚡ Medição I/V Simultânea - Dados recebidos: {data}")
        
        num_leituras = data.get('num_leituras', 5)
        delay = data.get('delay_entre_leituras', 0.5)
        modo = data.get('modo', 'tensao_fixa')  # 'tensao_fixa' ou 'corrente_fixa'
        valor_fixo = data.get('valor_fixo', 1.0)
        
        print(f"   - Leituras: {num_leituras}")
        print(f"   - Modo: {modo}")
        print(f"   - Valor fixo: {valor_fixo}")
        print(f"   - Delay: {delay}s")
        
        resultados = []
        
        with DeviceManager() as dm:
            keithley = dm.add_smu(KEITHLEY_ADDRESS)
            
            # Reset e configuração inicial
            keithley.write('smua.reset()')
            time.sleep(0.5)
            
            # Habilita autorange para tensão e corrente
            keithley.write('smua.measure.autorangev = smua.AUTORANGE_ON')
            keithley.write('smua.measure.autorangei = smua.AUTORANGE_ON')
            
            # Configura o modo de source (fonte)
            if modo == "tensao_fixa":
                keithley.write('smua.source.func = smua.OUTPUT_DCVOLTAGE')
                keithley.write(f'smua.source.levelv = {valor_fixo}')
                keithley.write('smua.source.limiti = 0.1')  # Limite de corrente (segurança)
                print(f"   Configurado: Aplicando tensão fixa de {valor_fixo}V")
            else:  # corrente_fixa
                keithley.write('smua.source.func = smua.OUTPUT_DCCURRENT')
                keithley.write(f'smua.source.leveli = {valor_fixo}')
                keithley.write('smua.source.limitv = 40')  # Limite de tensão (segurança)
                print(f"   Configurado: Aplicando corrente fixa de {valor_fixo}A")
            
            # Configura o modo de medição (sempre mede ambos)
            keithley.write('smua.measure.func = smua.MEASURE_FUNC_DCVOLTAGE')
            
            for i in range(num_leituras):
                print(f"   📈 Medição IV {i+1}/{num_leituras}...")
                
                # Liga a saída
                keithley.write('smua.source.output = smua.OUTPUT_ON')
                time.sleep(0.2)  # Tempo de estabilização
                
                # Método 1: Usar measure.iv() que retorna corrente e tensão
                # O comando retorna: corrente, tensão
                keithley.write('print(smua.measure.iv())')
                time.sleep(0.3)
                resposta = keithley.read()
                
                # Desliga a saída
                keithley.write('smua.source.output = smua.OUTPUT_OFF')
                
                # Processa a resposta (espera dois valores: corrente, tensão)
                try:
                    # Remove espaços e quebra linhas
                    resposta_limpa = resposta.strip()
                    # Separa os valores por vírgula ou espaço
                    if ',' in resposta_limpa:
                        partes = resposta_limpa.split(',')
                    else:
                        partes = resposta_limpa.split()
                    
                    # Extrai corrente e tensão
                    corrente = float(partes[0].strip())
                    tensao = float(partes[1].strip()) if len(partes) > 1 else 0.0
                    
                    # Se estamos aplicando tensão fixa, a tensão medida deve ser próxima do valor fixo
                    # Se estamos aplicando corrente fixa, a corrente medida deve ser próxima do valor fixo
                    
                except Exception as e:
                    print(f"      Erro ao processar resposta: '{resposta}'")
                    corrente = 0.0
                    tensao = 0.0
                
                potencia = corrente * tensao
                
                resultado = {
                    'corrente': round(corrente, 12),
                    'tensao': round(tensao, 6),
                    'potencia': round(potencia, 9)
                }
                
                resultados.append(resultado)
                print(f"      I = {corrente:.6e} A, V = {tensao:.4f} V, P = {potencia:.6f} W")
                
                if i < num_leituras - 1:
                    time.sleep(delay)
        
        print(f"✅ Medição IV concluída! {len(resultados)} leituras")
        
        return jsonify({
            "status": "sucesso",
            "medicoes": resultados,
            "mensagem": f"{len(resultados)} medições I/V realizadas com sucesso"
        })
        
    except Exception as e:
        print(f"❌ Erro durante a medição IV: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Iniciando servidor Keithley Controller")
    print("="*50)
    print("📍 API disponível em: http://localhost:8001")
    print("🌐 CORS permitido para: http://localhost:5173")
    print("\n📡 Endpoints disponíveis:")
    print("   GET  - /api/health")
    print("   GET  - /api/testar_conexao")
    print("   POST - /api/medir (medição simples)")
    print("   POST - /api/medir_iv (medição I/V simultânea)")
    print("\n⚠️  Mantenha este terminal aberto enquanto usa a interface")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=8001, debug=True)