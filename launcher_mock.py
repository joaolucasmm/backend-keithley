import sys
import os
import threading
import time
import webbrowser

# Determina se está rodando como executável
if getattr(sys, 'frozen', False):
    # Rodando como executável PyInstaller
    application_path = sys._MEIPASS
else:
    # Rodando como script Python
    application_path = os.path.dirname(os.path.abspath(__file__))

# Adiciona o caminho da aplicação ao sys.path
if application_path not in sys.path:
    sys.path.insert(0, application_path)

# Configura variável de ambiente
os.environ['FLASK_APP'] = 'mock_server.py'

# Tenta importar webview
try:
    import webview
    HAS_WEBVIEW = True
    print("✅ PyWebview encontrado")
except ImportError:
    HAS_WEBVIEW = False
    print("⚠️ PyWebview não encontrado, usando navegador padrão")

def start_flask_mock():
    """Inicia o servidor Flask Mock em uma thread separada"""
    try:
        # Força a importação do mock_server
        import mock_server
        
        print(f"✅ Mock server importado com sucesso")
        print(f"Servidor MOCK iniciando em http://127.0.0.1:8000")
        
        # Inicia o servidor
        mock_server.app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)
    except ImportError as e:
        print(f"❌ Erro ao importar mock_server: {e}")
        print("Verificando arquivos disponíveis:")
        print(f"Arquivos em {application_path}:")
        try:
            for file in os.listdir(application_path):
                print(f"  - {file}")
        except:
            pass
        input("Pressione Enter para sair...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao iniciar Flask Mock: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
        sys.exit(1)

def open_browser():
    """Abre a interface no navegador padrão"""
    print("🌐 Abrindo navegador...")
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8000')

def start_webview():
    """Inicia a janela desktop com pywebview"""
    print("🪟 Iniciando janela desktop...")
    time.sleep(2)
    try:
        webview.create_window(
            title='Keithley 2611B Controller (MOCK)',
            url='http://127.0.0.1:8000',
            width=1200,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600)
        )
        webview.start()
    except Exception as e:
        print(f"❌ Erro ao iniciar webview: {e}")
        print("Usando navegador como fallback...")
        open_browser()

def test_server():
    """Testa se o servidor está respondendo"""
    import urllib.request
    import urllib.error
    
    print("⏳ Aguardando servidor iniciar...")
    max_attempts = 20
    for i in range(max_attempts):
        try:
            req = urllib.request.Request('http://127.0.0.1:8000/api/health')
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print("✅ Servidor MOCK pronto!")
                    return True
        except urllib.error.URLError:
            print(f"⏳ Tentativa {i+1}/{max_attempts}...")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Erro: {e}")
            time.sleep(1)
    
    print("❌ Servidor MOCK não respondeu")
    return False

def main():
    print("="*50)
    print("🎭 Keithley 2611B Controller (MOCK MODE)")
    print("="*50)
    print(f"Modo: {'Executável' if getattr(sys, 'frozen', False) else 'Script Python'}")
    print(f"Path: {application_path}")
    print("="*50)
    print()
    
    print("🚀 Iniciando servidor MOCK...")
    
    # Inicia Flask em background
    flask_thread = threading.Thread(target=start_flask_mock, daemon=True)
    flask_thread.start()
    
    # Aguarda o servidor iniciar
    if test_server():
        # Abre a interface
        if HAS_WEBVIEW:
            print("🪟 Abrindo janela desktop...")
            start_webview()
        else:
            print("🌐 Abrindo navegador...")
            open_browser()
            # Mantém o programa rodando
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Encerrando...")
    else:
        print("❌ Falha ao iniciar o servidor")
        print("Verifique se o arquivo mock_server.py está presente")
        input("Pressione Enter para sair...")

if __name__ == '__main__':
    main()