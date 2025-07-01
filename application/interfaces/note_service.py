from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.note import Note
from domain.value_objects.search_criteria import SearchCriteria

class NoteService(ABC):
    """Interface para casos de uso relacionados a notas."""
    
    @abstractmethod
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Obtém todas as notas, opcionalmente filtradas pelo ID da pasta."""
        pass
    
    @abstractmethod
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Obtém uma nota pelo seu ID."""
        pass
    
    @abstractmethod
    def create_note(self, title: str, content: str, folder_id: Optional[int] = None) -> int:
        """Cria uma nova nota e retorna seu ID."""
        pass
    
    @abstractmethod
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Atualiza uma nota existente e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def delete_note(self, note_id: int) -> bool:
        """Exclui uma nota pelo seu ID e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def move_note(self, note_id: int, folder_id: int) -> bool:
        """Move uma nota para outra pasta e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def search_notes(self, criteria: SearchCriteria) -> List[Note]:
        """Busca notas com base nos critérios fornecidos."""
        pass