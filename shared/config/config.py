import os
import json
from typing import Dict, Any, Optional

class Config:
    """Gerenciador de configuração da aplicação.
    
    Esta classe é responsável por carregar, acessar e gerenciar
    as configurações da aplicação.
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """Inicializa o gerenciador de configuração.
        
        Args:
            config_file_path: Caminho para o arquivo de configuração (opcional)
        """
        self.config: Dict[str, Any] = {}
        self.config_file_path = config_file_path
        
        # Valores padrão de configuração
        self._set_defaults()
        
        # Carrega configuração do arquivo se fornecido
        if config_file_path and os.path.exists(config_file_path):
            self._load_from_file(config_file_path)
    
    def _set_defaults(self):
        """Define valores padrão de configuração."""
        # Obtém o diretório base da aplicação
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Configurações do banco de dados
        self.config['db_path'] = os.path.join(base_dir, 'data', 'notepad.db')
        
        # Configurações de armazenamento
        self.config['storage_path'] = os.path.join(base_dir, 'data', 'attachments')
        
        # Configurações de UI
        self.config['theme'] = 'light'
        self.config['font_size'] = 12
        
        # Garante que os diretórios de dados existam
        os.makedirs(os.path.dirname(self.config['db_path']), exist_ok=True)
        os.makedirs(self.config['storage_path'], exist_ok=True)
    
    def _load_from_file(self, file_path: str):
        """Carrega configuração de um arquivo JSON.
        
        Args:
            file_path: Caminho para o arquivo de configuração
        """
        try:
            with open(file_path, 'r') as f:
                file_config = json.load(f)
                # Atualiza a configuração com valores do arquivo
                self.config.update(file_config)
        except (json.JSONDecodeError, IOError) as e:
            from shared.utils.logger import Logger
            logger = Logger.get_instance()
            logger.error(f"Erro ao carregar configuração de {file_path}: {e}")
    
    def save_to_file(self, file_path: str):
        """Salva a configuração atual em um arquivo JSON.
        
        Args:
            file_path: Caminho onde salvar a configuração
        """
        try:
            # Garante que o diretório exista
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            from shared.utils.logger import Logger
            logger = Logger.get_instance()
            logger.error(f"Erro ao salvar configuração em {file_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração.
        
        Args:
            key: A chave de configuração
            default: Valor padrão se a chave não existir
            
        Returns:
            O valor da configuração ou o padrão
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Define um valor de configuração.
        
        Args:
            key: A chave de configuração
            value: O valor a ser definido
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Obtém todos os valores de configuração.
        
        Returns:
            Um dicionário com todos os valores de configuração
        """
        return self.config.copy()
        
    def load(self):
        """Carrega configuração do arquivo especificado na inicialização.
        
        Se nenhum caminho de arquivo foi fornecido na inicialização, este método não faz nada.
        """
        if self.config_file_path and os.path.exists(self.config_file_path):
            self._load_from_file(self.config_file_path)