import os
import subprocess
import sys

def instalar():
    caminho_msi = os.path.join(os.path.dirname(__file__), 'connectwise.msi')
    try:
        print(f"Executando instalador: {caminho_msi}")
        subprocess.run(['msiexec', '/i', caminho_msi], check=True)
    except Exception as e:
        print(f"Erro ao executar o instalador: {e}")
        sys.exit(1)
