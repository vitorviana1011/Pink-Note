from typing import List, Optional, Dict, Any

from domain.entities.note import Note
from domain.value_objects.search_criteria import SearchCriteria
from application.interfaces.note_service import NoteService
from application.interfaces.folder_service import FolderService
from shared.utils.logger import Logger

class NoteController:
    """Controlador responsável pelas operações de notas."""
    
    def __init__(self, note_service: NoteService, folder_service: FolderService):
        """Inicializa o controlador com os serviços necessários.
        
        Args:
            note_service: O serviço de notas
            folder_service: O serviço de pastas
        """
        self.note_service = note_service
        self.folder_service = folder_service
        self.logger = Logger.get_instance()
    
    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Obtém todas as notas.
        
        Returns:
            Uma lista de dicionários representando as notas
        """
        try:
            notes = self.note_service.get_all_notes()
            return [self._note_to_dict(note) for note in notes]
        except Exception as e:
            self.logger.error(f"Error getting all notes: {str(e)}")
            return []
    
    def get_notes_by_folder(self, folder_id: int) -> List[Dict[str, Any]]:
        """Obtém todas as notas em uma pasta específica.
        
        Args:
            folder_id: O ID da pasta
            
        Returns:
            Uma lista de dicionários representando as notas
        """
        try:
            notes = self.note_service.get_notes_by_folder(folder_id)
            return [self._note_to_dict(note) for note in notes]
        except Exception as e:
            self.logger.error(f"Error getting notes for folder {folder_id}: {str(e)}")
            return []
    
    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma nota pelo ID.
        
        Args:
            note_id: O ID da nota
        
        Returns:
            Os dados da nota ou None se não encontrada
        """
        try:
            note = self.note_service.get_note_by_id(note_id)
            if note:
                return self._note_to_dict(note)
            return None
        except Exception as e:
            self.logger.error(f"Error getting note {note_id}: {str(e)}")
            return None
    
    def create_note(self, title: str, content: str, folder_id: int) -> Optional[Dict[str, Any]]:
        """Cria uma nova nota.
        
        Args:
            title: O título da nota
            content: O conteúdo da nota
            folder_id: O ID da pasta
            
        Returns:
            Um dicionário representando a nota criada, ou None se a criação falhou
        """
        try:
            # Valida se a pasta existe
            folder = self.folder_service.get_folder_by_id(folder_id)
            if not folder:
                self.logger.error(f"Cannot create note: Folder {folder_id} not found")
                return None
            
            # Cria a nota
            note_id = self.note_service.create_note(title, content, folder_id)
            if note_id:
                return self.get_note_by_id(note_id)
            return None
        except Exception as e:
            self.logger.error(f"Error creating note: {str(e)}")
            return None
    
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Atualiza uma nota existente.
        
        Args:
            note_id: O ID da nota
            title: O novo título
            content: O novo conteúdo
            
        Returns:
            True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            return self.note_service.update_note(note_id, title, content)
        except Exception as e:
            self.logger.error(f"Error updating note {note_id}: {str(e)}")
            return False
    
    def delete_note(self, note_id: int) -> bool:
        """Exclui uma nota.
        
        Args:
            note_id: O ID da nota
            
        Returns:
            True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            return self.note_service.delete_note(note_id)
        except Exception as e:
            self.logger.error(f"Error deleting note {note_id}: {str(e)}")
            return False
    
    def move_note(self, note_id: int, target_folder_id: int) -> bool:
        """Move uma nota para uma pasta diferente.
        
        Args:
            note_id: O ID da nota
            target_folder_id: O ID da pasta de destino
            
        Returns:
            True se a movimentação foi bem-sucedida, False caso contrário
        """
        try:
            # Valida se a pasta existe
            folder = self.folder_service.get_folder_by_id(target_folder_id)
            if not folder:
                self.logger.error(f"Cannot move note: Folder {target_folder_id} not found")
                return False
            
            return self.note_service.move_note(note_id, target_folder_id)
        except Exception as e:
            self.logger.error(f"Error moving note {note_id} to folder {target_folder_id}: {str(e)}")
            return False
    
    def search_notes(self, search_term: str, folder_ids: Optional[List[int]] = None,
                     include_title: bool = True, include_content: bool = True,
                     case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Busca notas com base em critérios.
        
        Args:
            search_term: O termo de busca
            folder_ids: Lista opcional de IDs de pastas para buscar
            include_title: Se deve buscar nos títulos
            include_content: Se deve buscar no conteúdo
            case_sensitive: Se a busca deve ser sensível a maiúsculas e minúsculas
            
        Returns:
            Uma lista de dicionários representando as notas que correspondem à busca
        """
        try:
            # Cria os critérios de busca
            criteria = SearchCriteria(
                search_term=search_term,
                folder_ids=folder_ids or [],
                include_title=include_title,
                include_content=include_content,
                case_sensitive=case_sensitive
            )
            
            # Realiza a busca
            notes = self.note_service.search_notes(criteria)
            return [self._note_to_dict(note) for note in notes]
        except Exception as e:
            self.logger.error(f"Error searching notes: {str(e)}")
            return []
    
    def _note_to_dict(self, note: Note) -> Dict[str, Any]:
        """Converte uma entidade Note para um dicionário.
        
        Args:
            note: A entidade Note
            
        Returns:
            Uma representação em dicionário da nota
        """
        return {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat() if note.created_at else None,
            'modified_at': note.modified_at.isoformat() if note.modified_at else None,
            'folder_id': note.folder_id,
            'attachment_ids': note.attachment_ids
        }