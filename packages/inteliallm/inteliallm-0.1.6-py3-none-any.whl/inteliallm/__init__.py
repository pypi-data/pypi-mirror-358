# Importa a classe do módulo 'client.py' para o nível do pacote 'inteliallm'.
from .client import InteliaLLMClient

# Também é uma boa prática expor a versão do pacote aqui.
# Poetry pode gerenciar isso para você com plugins, ou você pode definir manualmente.
__version__ = "0.1.1"