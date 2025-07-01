import os
import logging
from datetime import datetime
from typing import Optional

class Logger:
    """Um logger simples para a aplicação.
    
    Esta classe fornece um mecanismo centralizado de logging com diferentes
    níveis de log e opções de saída (console e/ou arquivo).
    """
    
    # Instância singleton
    _instance = None
    
    @classmethod
    def get_instance(cls, log_level: int = logging.INFO, log_to_file: bool = True, log_dir: Optional[str] = None):
        """Obtém ou cria a instância singleton do logger.
        
        Args:
            log_level: O nível de logging (padrão: INFO)
            log_to_file: Se deve registrar em arquivo (padrão: True)
            log_dir: Diretório para arquivos de log (padrão: 'logs' no diretório da aplicação)
            
        Returns:
            A instância do Logger
        """
        if cls._instance is None:
            cls._instance = Logger(log_level, log_to_file, log_dir)
        return cls._instance
    
    def __init__(self, log_level: int = logging.INFO, log_to_file: bool = True, log_dir: Optional[str] = None):
        """Inicializa o logger.
        
        Args:
            log_level: O nível de logging (padrão: INFO)
            log_to_file: Se deve registrar em arquivo (padrão: True)
            log_dir: Diretório para arquivos de log (padrão: 'logs' no diretório da aplicação)
        """
        self.logger = logging.getLogger('notepad')
        self.logger.setLevel(log_level)
        
        # Limpa handlers existentes
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Cria handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Cria formatador
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Adiciona handler de console ao logger
        self.logger.addHandler(console_handler)
        
        # Adiciona handler de arquivo se solicitado
        if log_to_file:
            if log_dir is None:
                # Diretório padrão de logs é 'logs' no diretório da aplicação
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                log_dir = os.path.join(base_dir, 'logs')
            
            # Garante que o diretório de logs exista
            os.makedirs(log_dir, exist_ok=True)
            
            # Cria arquivo de log com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(log_dir, f'notepad_{timestamp}.log')
            
            # Cria handler de arquivo
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            
            # Adiciona handler de arquivo ao logger
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Registra uma mensagem de debug.
        
        Args:
            message: A mensagem a ser registrada
        """
        self.logger.debug(message)
    
    def info(self, message: str):
        """Registra uma mensagem de informação.
        
        Args:
            message: A mensagem a ser registrada
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """Registra uma mensagem de aviso.
        
        Args:
            message: A mensagem a ser registrada
        """
        self.logger.warning(message)
    
    def error(self, message: str):
        """Registra uma mensagem de erro.
        
        Args:
            message: A mensagem a ser registrada
        """
        self.logger.error(message)
    
    def critical(self, message: str):
        """Registra uma mensagem crítica.
        
        Args:
            message: A mensagem a ser registrada
        """
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Registra uma exceção com traceback.
        
        Args:
            message: A mensagem a ser registrada
        """
        self.logger.exception(message)