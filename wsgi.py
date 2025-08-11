import sys
import os

# Adiciona o diretório pai ao PYTHONPATH para que as importações funcionem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.main import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
