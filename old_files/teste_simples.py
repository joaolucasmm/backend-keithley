from tm_devices import DeviceManager
import time

ADDRESS = "USB0::0x05E6::0x2611::4629001::INSTR"

print("Teste simples de comunicação com Keithley 2611B")
print("="*50)

try:
    print("1. Conectando ao instrumento...")
    with DeviceManager() as dm:
        print("   DeviceManager aberto")
        
        keithley = dm.add_smu(ADDRESS)
        print("   SMU conectado")
        
        print("2. Enviando comando *IDN?")
        # Usando query com timeout maior
        keithley.write("*IDN?")
        time.sleep(0.5)
        idn = keithley.read()
        print(f"   Resposta: {idn}")
        
        print("3. Testando comando TSP simples")
        keithley.write('print(smua.reset())')  # Note o print
        time.sleep(0.5)
        
        print("4. Medindo tensão (sem aplicar sinal)")
        keithley.write('smua.source.output = smua.OUTPUT_ON')
        time.sleep(0.2)
        keithley.write('print(smua.measure.v())')
        time.sleep(0.5)
        valor = keithley.read()
        keithley.write('smua.source.output = smua.OUTPUT_OFF')
        
        print(f"   Tensão medida: {valor}")
        
    print("\n✅ Teste concluído com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    print("\nPossíveis causas:")
    print("1. A Keithley não está ligada ou desconectada")
    print("2. Outro programa (como TSB) está usando a porta USB")
    print("3. Driver USB não está correto")
    print("4. O endereço do instrumento está incorreto")