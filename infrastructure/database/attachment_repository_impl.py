import os
from datetime import datetime
from typing import List, Optional

from domain.entities.attachment import Attachment
from domain.repositories.attachment_repository import AttachmentRepository

class AttachmentRepositoryImpl(AttachmentRepository):
    """Implementação SQLite do repositório de anexos."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Recupera todos os anexos de uma nota específica."""
        cursor = self.db.cursor()
        
        if note_id is None:
            # Obtém todos os anexos se note_id for None
            cursor.execute(
                "SELECT id, note_id, file_path, file_name, file_type, created_at FROM attachments ORDER BY created_at DESC"
            )
        else:
            cursor.execute(
                "SELECT id, note_id, file_path, file_name, file_type, created_at FROM attachments WHERE note_id = ? ORDER BY created_at DESC",
                (note_id,)
            )
        
        attachments = []
        for row in cursor.fetchall():
            attachment = Attachment(
                id=row[0],
                note_id=row[1],
                file_path=row[2],
                file_name=row[3],
                file_type=row[4],
                created_at=datetime.fromisoformat(row[5])
            )
            attachments.append(attachment)
        
        return attachments
    
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Recupera um anexo pelo seu ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, note_id, file_path, file_name, file_type, created_at FROM attachments WHERE id = ?",
            (attachment_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return Attachment(
            id=row[0],
            note_id=row[1],
            file_path=row[2],
            file_name=row[3],
            file_type=row[4],
            created_at=datetime.fromisoformat(row[5])
        )
    
    def add_attachment(self, attachment: Attachment) -> int:
        """Adiciona um novo anexo e retorna seu ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO attachments (note_id, file_path, file_name, file_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                attachment.note_id,
                attachment.file_path,
                attachment.file_name,
                attachment.file_type,
                attachment.created_at.isoformat()
            )
        )
        
        self.db.commit()
        return cursor.lastrowid
    
    def delete_attachment(self, attachment_id: int) -> bool:
        """Exclui um anexo pelo seu ID e retorna o status de sucesso."""
        cursor = self.db.cursor()
        
        # Obtém o caminho do arquivo para excluir o arquivo físico
        cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        
        file_path = row[0]
        
        # Exclui o registro do anexo
        cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        
        # Exclui o arquivo físico se existir
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                # Apenas registra o erro e continua com a exclusão no banco
                pass
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Obtém o caminho do sistema de arquivos para um anexo."""
        cursor = self.db.cursor()
        cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return row[0]