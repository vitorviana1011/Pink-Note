from typing import List, Optional

from domain.entities.note import Note
from domain.repositories.note_repository import NoteRepository
from domain.value_objects.search_criteria import SearchCriteria
from application.interfaces.note_service import NoteService

class NoteServiceImpl(NoteService):
    """Implementação dos casos de uso do serviço de notas."""
    
    def __init__(self, note_repository: NoteRepository):
        self.note_repository = note_repository
    
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Obtém todas as notas, opcionalmente filtradas pelo ID da pasta."""
        return self.note_repository.get_all_notes(folder_id)
    
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Obtém uma nota pelo seu ID."""
        return self.note_repository.get_note_by_id(note_id)
    
    def create_note(self, title: str, content: str, folder_id: Optional[int] = None) -> int:
        """Cria uma nova nota e retorna seu ID."""
        note = Note(title=title, content=content)
        if folder_id is not None:
            note.folder_id = folder_id
        return self.note_repository.add_note(note)
    
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Atualiza uma nota existente e retorna o status de sucesso."""
        note = self.note_repository.get_note_by_id(note_id)
        if note is None:
            return False
        
        note.update_title(title)
        note.update_content(content)
        return self.note_repository.update_note(note)
    
    def delete_note(self, note_id: int) -> bool:
        """Exclui uma nota pelo seu ID e retorna o status de sucesso."""
        return self.note_repository.delete_note(note_id)
    
    def move_note(self, note_id: int, folder_id: int) -> bool:
        """Move uma nota para outra pasta e retorna o status de sucesso."""
        return self.note_repository.move_note(note_id, folder_id)
    
    def search_notes(self, criteria: SearchCriteria) -> List[Note]:
        """Busca notas com base nos critérios fornecidos."""
        # Esta é uma implementação simplificada que delega ao repositório
        # Em um sistema mais complexo, poderíamos aplicar lógica de negócio adicional aqui
        return self.note_repository.search_notes(criteria)
        
    def get_notes_by_folder(self, folder_id: int) -> List[Note]:
        """Obtém todas as notas em uma pasta específica.
        
        Args:
            folder_id: O ID da pasta
            
        Returns:
            Uma lista de notas na pasta
        """
        return self.get_all_notes(folder_id=folder_id)