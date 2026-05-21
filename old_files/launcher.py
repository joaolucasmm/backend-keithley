import webview
import threading
import subprocess
import sys
import os
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

# Configura variável de ambiente para o Flask
os.environ['FLASK_APP'] = 'main.py'

# Tenta importar webview
try:
    import webview
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False
    print("PyWebview não encontrado, usando navegador padrão")

def start_flask():
    """Inicia o servidor Flask em uma thread separada"""
    try:
        # Adiciona o diretório atual ao path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Importa e executa o Flask
        from main import app
        app.run(host='127.0.0.1', port=8001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Erro ao iniciar Flask: {e}")
        import traceback
        traceback.print_exc()

def start_app():
    """Inicia a janela desktop com pywebview"""
    # Aguarda o Flask iniciar completamente
    time.sleep(2)
    
    # Tenta conectar algumas vezes
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            import requests
            response = requests.get('http://127.0.0.1:8001/api/health', timeout=1)
            if response.status_code == 200:
                print("Flask iniciado com sucesso!")
                break
        except:
            print(f"Aguardando Flask iniciar... (tentativa {attempt+1}/{max_attempts})")
            time.sleep(1)
    
    # Abre a janela
    webview.create_window(
        title='Keithley 2611B Controller',
        url='http://127.0.0.1:8001',
        width=1200,
        height=800,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600)
    )
    webview.start()

def check_dependencies():
    """Verifica se as dependências necessárias estão disponíveis"""
    missing = []
    
    try:
        import flask
    except ImportError:
        missing.append("flask")
    
    try:
        import flask_cors
    except ImportError:
        missing.append("flask_cors")
    
    try:
        import tm_devices
    except ImportError:
        missing.append("tm_devices")
    
    try:
        import webview
    except ImportError:
        missing.append("pywebview")
    
    if missing:
        print(f"ERRO: Dependências faltando: {', '.join(missing)}")
        print("Instale com: pip install " + " ".join(missing))
        input("Pressione Enter para sair...")
        sys.exit(1)

def open_browser():
    """Abre a interface no navegador padrão"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8001')

def start_webview():
    """Inicia a janela desktop com pywebview"""
    time.sleep(2)
    try:
        webview.create_window(
            title='Keithley 2611B Controller',
            url='http://127.0.0.1:8001',
            width=1200,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600)
        )
        webview.start()
    except Exception as e:
        print(f"Erro ao iniciar webview: {e}")
        open_browser()

def test_server():
    """Testa se o servidor está respondendo"""
    import urllib.request
    import urllib.error
    
    max_attempts = 15
    for i in range(max_attempts):
        try:
            req = urllib.request.Request('http://127.0.0.1:8001/api/health')
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print("✅ Servidor pronto!")
                    return True
        except urllib.error.URLError:
            print(f"⏳ Aguardando servidor... ({i+1}/{max_attempts})")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Erro: {e}")
            time.sleep(1)
    
    print("❌ Servidor não respondeu após 15 segundos")
    return False

if __name__ == '__main__':
    print("Iniciando Keithley Controller...")
    check_dependencies()
    
    # Inicia Flask em background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Abre a janela desktop
    start_app()

    # Inicia Flask em background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
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
        input("Pressione Enter para sair...")