from typing import List, Optional, Tuple

from domain.entities.folder import Folder
from domain.repositories.folder_repository import FolderRepository
from application.interfaces.folder_service import FolderService

class FolderServiceImpl(FolderService):
    """Implementação dos casos de uso do serviço de pastas."""
    
    def __init__(self, folder_repository: FolderRepository):
        self.folder_repository = folder_repository
    
    def get_all_folders(self) -> List[Folder]:
        """Obtém todas as pastas."""
        return self.folder_repository.get_all_folders()
    
    def get_folder_by_id(self, folder_id: int) -> Optional[Folder]:
        """Obtém uma pasta pelo seu ID."""
        return self.folder_repository.get_folder_by_id(folder_id)
    
    def get_folder_hierarchy(self) -> List[Tuple[Folder, int]]:
        """Obtém a hierarquia de pastas como uma lista de tuplas (pasta, profundidade)."""
        folders = self.folder_repository.get_all_folders()
        result = []
        
        # Primeiro, encontra todas as pastas raiz (parent_id é None)
        root_folders = [f for f in folders if f.parent_id is None]
        
        # Processa cada pasta raiz e seus filhos recursivamente
        for root_folder in root_folders:
            self._add_folder_with_depth(result, root_folder, 0, folders)
        
        return result
    
    def _add_folder_with_depth(self, result: List[Tuple[Folder, int]], folder: Folder, depth: int, all_folders: List[Folder]) -> None:
        """Método auxiliar para construir recursivamente a hierarquia de pastas."""
        result.append((folder, depth))
        
        # Encontra todos os filhos desta pasta
        children = [f for f in all_folders if f.parent_id == folder.id]
        
        # Processa cada filho recursivamente
        for child in children:
            self._add_folder_with_depth(result, child, depth + 1, all_folders)
    
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> int:
        """Cria uma nova pasta e retorna seu ID."""
        folder = Folder(name=name, parent_id=parent_id)
        return self.folder_repository.create_folder(folder)
    
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Renomeia uma pasta e retorna o status de sucesso."""
        return self.folder_repository.rename_folder(folder_id, new_name)
    
    def delete_folder(self, folder_id: int) -> bool:
        """Exclui uma pasta e retorna o status de sucesso."""
        return self.folder_repository.delete_folder(folder_id)
    
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move uma pasta para um novo pai e retorna o status de sucesso."""
        return self.folder_repository.move_folder(folder_id, new_parent_id)
    
    def get_folder_note_count(self, folder_id: int) -> int:
        """Obtém o número de notas em uma pasta."""
        return self.folder_repository.get_folder_note_count(folder_id)