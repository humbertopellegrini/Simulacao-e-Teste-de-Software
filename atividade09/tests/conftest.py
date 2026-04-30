import sys
from pathlib import Path

# Garante que o diretório raiz do pacote esteja no caminho do Python
# para que os imports `task_manager.*` funcionem durante os testes.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
