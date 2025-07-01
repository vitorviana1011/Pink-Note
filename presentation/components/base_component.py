from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QWidget

class BaseComponent(QWidget):
    """Classe base para todos os componentes de UI na camada de apresentação.
    
    Esta classe fornece funcionalidades comuns para componentes de UI, como
    acesso a controladores e manipulação de eventos.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, controllers: Optional[Dict[str, Any]] = None):
        """Inicializa o componente.
        
        Args:
            parent: O widget pai
            controllers: Um dicionário de controladores
        """
        super().__init__(parent)
        self.controllers = controllers or {}
        
        # Inicializa a interface
        self._init_ui()
        
        # Conecta sinais e slots
        self._connect_signals()
    
    def _init_ui(self):
        """Inicializa os componentes da interface.
        
        Este método deve ser sobrescrito pelas subclasses para configurar a interface.
        """
        pass
    
    def _connect_signals(self):
        """Conecta sinais e slots.
        
        Este método deve ser sobrescrito pelas subclasses para conectar seus sinais e slots.
        """
        pass
    
    def refresh(self):
        """Atualiza os dados e a interface do componente.
        
        Este método deve ser sobrescrito pelas subclasses para atualizar seus dados e interface.
        """
        pass