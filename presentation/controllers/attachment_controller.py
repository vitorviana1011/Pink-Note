from typing import List, Optional, Dict, Any
import os

from domain.entities.attachment import Attachment
from application.interfaces.attachment_service import AttachmentService
from application.interfaces.note_service import NoteService
from shared.utils.logger import Logger
from shared.constants.app_constants import SUPPORTED_FILE_EXTENSIONS

class AttachmentController:
    """Controlador para operações relacionadas a anexos na camada de apresentação."""
    
    def __init__(self, attachment_service: AttachmentService, note_service: NoteService):
        """Inicializa o controlador com os serviços necessários.
        
        Args:
            attachment_service: O serviço de anexos
            note_service: O serviço de notas
        """
        self.attachment_service = attachment_service
        self.note_service = note_service
        self.logger = Logger.get_instance()
    
    def get_attachments_for_note(self, note_id: int) -> List[Dict[str, Any]]:
        """Obtém todos os anexos de uma nota específica.
        
        Args:
            note_id: O ID da nota
            
        Returns:
            Uma lista de dicionários representando os anexos
        """
        try:
            # Valida se a nota existe
            note = self.note_service.get_note_by_id(note_id)
            if not note:
                self.logger.error(f"Não é possível obter anexos: Nota {note_id} não encontrada")
                return []
            
            attachments = self.attachment_service.get_attachments_for_note(note_id)
            return [self._attachment_to_dict(attachment) for attachment in attachments]
        except Exception as e:
            self.logger.error(f"Erro ao obter anexos da nota {note_id}: {str(e)}")
            return []
    
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um anexo pelo seu ID.
        
        Args:
            attachment_id: O ID do anexo
            
        Returns:
            Um dicionário representando o anexo, ou None se não encontrado
        """
        try:
            attachment = self.attachment_service.get_attachment_by_id(attachment_id)
            if attachment:
                return self._attachment_to_dict(attachment)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter anexo {attachment_id}: {str(e)}")
            return None
    
    def add_attachment(self, note_id: int, file_path: str) -> Optional[Dict[str, Any]]:
        """Adiciona um novo anexo a uma nota.
        
        Args:
            note_id: O ID da nota
            file_path: O caminho do arquivo a ser anexado
            
        Returns:
            Um dicionário representando o anexo adicionado, ou None se falhar
        """
        try:
            # Valida se a nota existe
            note = self.note_service.get_note_by_id(note_id)
            if not note:
                self.logger.error(f"Não é possível adicionar anexo: Nota {note_id} não encontrada")
                return None
            
            # Valida se o arquivo existe
            if not os.path.exists(file_path):
                self.logger.error(f"Não é possível adicionar anexo: Arquivo {file_path} não encontrado")
                return None
            
            # Valida extensão do arquivo
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in SUPPORTED_FILE_EXTENSIONS:
                self.logger.error(f"Não é possível adicionar anexo: Extensão de arquivo não suportada {file_ext}")
                return None
            
            # Adiciona o anexo
            attachment_id = self.attachment_service.add_attachment(note_id, file_path)
            if attachment_id:
                return self.get_attachment_by_id(attachment_id)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao adicionar anexo à nota {note_id}: {str(e)}")
            return None
    
    def delete_attachment(self, attachment_id: int) -> bool:
        """Exclui um anexo.
        
        Args:
            attachment_id: O ID do anexo
            
        Returns:
            True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            return self.attachment_service.delete_attachment(attachment_id)
        except Exception as e:
            self.logger.error(f"Erro ao excluir anexo {attachment_id}: {str(e)}")
            return False
    
    def open_attachment(self, attachment_id: int) -> bool:
        """Abre um anexo com o aplicativo padrão do sistema.
        
        Args:
            attachment_id: O ID do anexo
            
        Returns:
            True se o anexo foi aberto com sucesso, False caso contrário
        """
        try:
            return self.attachment_service.open_attachment(attachment_id)
        except Exception as e:
            self.logger.error(f"Erro ao abrir anexo {attachment_id}: {str(e)}")
            return False
    
    def _attachment_to_dict(self, attachment: Attachment) -> Dict[str, Any]:
        """Converte uma entidade Attachment para um dicionário.
        
        Args:
            attachment: A entidade Attachment
            
        Returns:
            Um dicionário representando o anexo
        """
        return {
            'id': attachment.id,
            'note_id': attachment.note_id,
            'file_path': attachment.file_path,
            'file_name': attachment.file_name,
            'file_type': attachment.file_type,
            'created_at': attachment.created_at.isoformat() if attachment.created_at else None,
            'is_image': attachment.is_image,
            'is_pdf': attachment.is_pdf
        }