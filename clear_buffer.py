# clear_buffer.py
from tm_devices import DeviceManager
import time

KEITHLEY_ADDRESS = "USB0::0x05E6::0x2611::4629001::INSTR"

def clear_keithley():
    print("Limpando buffers da Keithley...")
    
    with DeviceManager() as dm:
        keithley = dm.add_smu(KEITHLEY_ADDRESS)
        
        # Reset completo
        keithley.write('reset()')
        time.sleep(1)
        
        # Limpar todos os buffers
        keithley.write('errorqueue.clear()')
        keithley.write('status.clear()')
        keithley.write('*CLS')
        
        # Ler e descartar dados pendentes
        for i in range(5):
            try:
                keithley.write('print("")')
                time.sleep(0.1)
                resposta = keithley.read()
                print(f"Descartado: {resposta}")
            except:
                pass
        
        print("Limpeza concluída!")

if __name__ == "__main__":
    clear_keithley()