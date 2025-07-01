from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.attachment import Attachment

class AttachmentService(ABC):
    """Interface para casos de uso relacionados a anexos."""
    
    @abstractmethod
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Obtém todos os anexos de uma nota específica."""
        pass
    
    @abstractmethod
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Obtém um anexo pelo seu ID."""
        pass
    
    @abstractmethod
    def add_attachment(self, note_id: int, file_path: str) -> int:
        """Adiciona um novo anexo a uma nota e retorna seu ID."""
        pass
    
    @abstractmethod
    def delete_attachment(self, attachment_id: int) -> bool:
        """Exclui um anexo pelo seu ID e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Obtém o caminho do sistema de arquivos para um anexo."""
        pass
    
    @abstractmethod
    def open_attachment(self, attachment_id: int) -> bool:
        """Abre um anexo com o aplicativo padrão do sistema."""
        pass