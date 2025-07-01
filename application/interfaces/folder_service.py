from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from domain.entities.folder import Folder

class FolderService(ABC):
    """Interface para casos de uso relacionados a pastas."""
    
    @abstractmethod
    def get_all_folders(self) -> List[Folder]:
        """Obtém todas as pastas."""
        pass
    
    @abstractmethod
    def get_folder_by_id(self, folder_id: int) -> Optional[Folder]:
        """Obtém uma pasta pelo seu ID."""
        pass
    
    @abstractmethod
    def get_folder_hierarchy(self) -> List[Tuple[Folder, int]]:
        """Obtém a hierarquia de pastas como uma lista de tuplas (pasta, profundidade)."""
        pass
    
    @abstractmethod
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> int:
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