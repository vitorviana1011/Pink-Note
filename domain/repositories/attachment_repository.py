from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.attachment import Attachment

class AttachmentRepository(ABC):
    """Interface para operações do repositório de anexos."""
    
    @abstractmethod
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Recupera todos os anexos de uma nota específica."""
        pass
    
    @abstractmethod
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Recupera um anexo pelo seu ID."""
        pass
    
    @abstractmethod
    def add_attachment(self, attachment: Attachment) -> int:
        """Adiciona um novo anexo e retorna seu ID."""
        pass
    
    @abstractmethod
    def delete_attachment(self, attachment_id: int) -> bool:
        """Exclui um anexo pelo seu ID e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Obtém o caminho do sistema de arquivos para um anexo."""
        pass