import sys
import os
import threading
import time
import subprocess
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
        # Importa e configura o Flask
        import flask
        from main import app
        
        # Configura os caminhos para templates e static
        dist_path = os.path.join(application_path, 'frontend', 'dist')
        if os.path.exists(dist_path):
            app.template_folder = dist_path
            app.static_folder = dist_path
        
        print(f"Servidor iniciando em http://127.0.0.1:8001")
        print(f"Arquivos frontend em: {dist_path}")
        app.run(host='127.0.0.1', port=8001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Erro ao iniciar Flask: {e}")
        import traceback
        traceback.print_exc()
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
    print("="*50)
    print("🔬 Keithley 2611B Controller")
    print("="*50)
    print(f"Modo: {'Executável' if getattr(sys, 'frozen', False) else 'Script Python'}")
    print(f"Path: {application_path}")
    print("="*50)
    print()
    
    print("🚀 Iniciando servidor...")
    
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