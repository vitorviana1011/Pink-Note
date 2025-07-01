import os
import subprocess
from datetime import datetime
from typing import List, Optional

from domain.entities.attachment import Attachment
from domain.repositories.attachment_repository import AttachmentRepository
from application.interfaces.attachment_service import AttachmentService

class AttachmentServiceImpl(AttachmentService):
    """Implementação dos casos de uso do serviço de anexos."""
    
    def __init__(self, attachment_repository: AttachmentRepository):
        self.attachment_repository = attachment_repository
    
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Obtém todos os anexos de uma nota específica."""
        return self.attachment_repository.get_attachments_for_note(note_id)
    
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Obtém um anexo pelo seu ID."""
        # Este método pode não estar disponível diretamente no repositório
        # Podemos implementá-lo filtrando o resultado de get_attachments_for_note
        attachments = self.attachment_repository.get_attachments_for_note(None)  # Obtém todos os anexos
        for attachment in attachments:
            if attachment.id == attachment_id:
                return attachment
        return None
    
    def add_attachment(self, note_id: int, file_path: str) -> int:
        """Adiciona um novo anexo a uma nota e retorna seu ID."""
        # Extrai nome e tipo do arquivo a partir do caminho
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_name)[1].lstrip('.')
        
        # Cria uma nova entidade de anexo
        attachment = Attachment(
            note_id=note_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            created_at=datetime.now()
        )
        
        return self.attachment_repository.add_attachment(attachment)
    
    def delete_attachment(self, attachment_id: int) -> bool:
        """Exclui um anexo pelo seu ID e retorna o status de sucesso."""
        return self.attachment_repository.delete_attachment(attachment_id)
    
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Obtém o caminho do sistema de arquivos para um anexo."""
        return self.attachment_repository.get_attachment_path(attachment_id)
    
    def open_attachment(self, attachment_id: int) -> bool:
        """Abre um anexo com o aplicativo padrão do sistema."""
        path = self.get_attachment_path(attachment_id)
        if not path or not os.path.exists(path):
            return False
        
        try:
            # Usa o comando apropriado de acordo com o sistema operacional
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS e Linux
                if 'darwin' in os.uname().sysname.lower():  # macOS
                    subprocess.call(['open', path])
                else:  # Linux
                    subprocess.call(['xdg-open', path])
            return True
        except Exception:
            return False