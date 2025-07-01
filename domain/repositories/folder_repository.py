from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.folder import Folder

class FolderRepository(ABC):
    """Interface para operações do repositório de pastas."""
    
    @abstractmethod
    def get_all_folders(self) -> List[Folder]:
        """Recupera todas as pastas."""
        pass
    
    @abstractmethod
    def get_folder_by_id(self, folder_id: int) -> Optional[Folder]:
        """Recupera uma pasta pelo seu ID."""
        pass
    
    @abstractmethod
    def get_subfolders(self, parent_id: Optional[int] = None) -> List[Folder]:
        """Recupera todas as subpastas de uma pasta pai."""
        pass
    
    @abstractmethod
    def create_folder(self, folder: Folder) -> int:
        """Cria uma nova pasta e retorna seu ID."""
        pass
    
    @abstractmethod
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Renomeia uma pasta e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def delete_folder(self, folder_id: int) -> bool:
        """Exclui uma pasta e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move uma pasta para um novo pai e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def get_folder_note_count(self, folder_id: int) -> int:
        """Obtém o número de notas em uma pasta."""
        pass