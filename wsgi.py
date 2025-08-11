import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH
# Isso permite que o Python encontre o módulo 'src.main'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.main import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
