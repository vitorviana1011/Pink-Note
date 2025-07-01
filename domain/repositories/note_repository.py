from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.note import Note

class NoteRepository(ABC):
    """Interface para operações do repositório de notas."""
    
    @abstractmethod
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Recupera todas as notas, opcionalmente filtradas pelo ID da pasta."""
        pass
    
    @abstractmethod
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Recupera uma nota pelo seu ID."""
        pass
    
    @abstractmethod
    def add_note(self, note: Note) -> int:
        """Adiciona uma nova nota e retorna seu ID."""
        pass
    
    @abstractmethod
    def update_note(self, note: Note) -> bool:
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
    def search_notes(self, search_term: str) -> List[Note]:
        """Busca notas contendo o termo de busca no título ou conteúdo."""
        pass