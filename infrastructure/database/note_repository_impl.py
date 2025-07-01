from datetime import datetime
from typing import List, Optional

from domain.entities.note import Note
from domain.repositories.note_repository import NoteRepository

class NoteRepositoryImpl(NoteRepository):
    """Implementação SQLite do repositório de notas."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Recupera todas as notas, opcionalmente filtradas pelo ID da pasta."""
        cursor = self.db.cursor()
        
        if folder_id is not None:
            cursor.execute(
                "SELECT id, title, content, created_at, modified_at, folder_id FROM notes WHERE folder_id = ? ORDER BY modified_at DESC",
                (folder_id,)
            )
        else:
            cursor.execute(
                "SELECT id, title, content, created_at, modified_at, folder_id FROM notes ORDER BY modified_at DESC"
            )
        
        notes = []
        for row in cursor.fetchall():
            note = Note(
                id=row[0],
                title=row[1],
                content=row[2],
                created_at=datetime.fromisoformat(row[3]),
                modified_at=datetime.fromisoformat(row[4]),
                folder_id=row[5]
            )
            notes.append(note)
        
        return notes
    
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Recupera uma nota pelo seu ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, title, content, created_at, modified_at, folder_id FROM notes WHERE id = ?",
            (note_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        note = Note(
            id=row[0],
            title=row[1],
            content=row[2],
            created_at=datetime.fromisoformat(row[3]),
            modified_at=datetime.fromisoformat(row[4]),
            folder_id=row[5]
        )
        
        # Obtém os IDs dos anexos desta nota
        cursor.execute("SELECT id FROM attachments WHERE note_id = ?", (note_id,))
        attachment_ids = [row[0] for row in cursor.fetchall()]
        note.attachment_ids = attachment_ids
        
        return note
    
    def add_note(self, note: Note) -> int:
        """Adiciona uma nova nota e retorna seu ID."""
        cursor = self.db.cursor()
        
        # Garante que folder_id esteja definido (padrão para pasta 'Geral' com ID 1)
        folder_id = note.folder_id if note.folder_id is not None else 1
        
        cursor.execute(
            "INSERT INTO notes (title, content, created_at, modified_at, folder_id) VALUES (?, ?, ?, ?, ?)",
            (note.title, note.content, note.created_at.isoformat(), note.modified_at.isoformat(), folder_id)
        )
        
        self.db.commit()
        return cursor.lastrowid
    
    def update_note(self, note: Note) -> bool:
        """Atualiza uma nota existente e retorna o status de sucesso."""
        if note.id is None:
            return False
        
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE notes SET title = ?, content = ?, modified_at = ? WHERE id = ?",
            (note.title, note.content, note.modified_at.isoformat(), note.id)
        )
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete_note(self, note_id: int) -> bool:
        """Exclui uma nota pelo seu ID e retorna o status de sucesso."""
        cursor = self.db.cursor()
        
        # Primeiro, exclui todos os anexos desta nota
        cursor.execute("SELECT id FROM attachments WHERE note_id = ?", (note_id,))
        attachment_ids = [row[0] for row in cursor.fetchall()]
        
        for attachment_id in attachment_ids:
            # Obtém o caminho do arquivo para excluir o arquivo físico
            cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
            file_path = cursor.fetchone()[0]
            
            # Exclui o registro do anexo
            cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            
            # Excluir o arquivo físico (isso seria feito por um serviço de arquivos em uma implementação real)
            # os.remove(file_path)
        
        # Agora exclui a nota
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def move_note(self, note_id: int, folder_id: int) -> bool:
        """Move uma nota para outra pasta e retorna o status de sucesso."""
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE notes SET folder_id = ?, modified_at = ? WHERE id = ?",
            (folder_id, datetime.now().isoformat(), note_id)
        )
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def search_notes(self, criteria) -> List[Note]:
        """Busca notas com base nos critérios fornecidos."""
        cursor = self.db.cursor()
        search_term = criteria.search_term
        
        # Aplica sensibilidade a maiúsculas/minúsculas
        if not criteria.case_sensitive:
            search_term = search_term.lower()
            title_clause = "LOWER(n.title) LIKE ?"
            content_clause = "LOWER(n.content) LIKE ?"
        else:
            title_clause = "n.title LIKE ?"
            content_clause = "n.content LIKE ?"
        
        search_pattern = f"%{search_term}%"
        
        # Monta a consulta com base nos critérios de busca
        query = """SELECT n.id, n.title, n.content, n.created_at, n.modified_at, n.folder_id, f.name as folder_name 
                 FROM notes n 
                 JOIN folders f ON n.folder_id = f.id 
                 WHERE """
        
        conditions = []
        params = []
        
        # Adiciona condição de título se necessário
        if criteria.include_title:
            conditions.append(f"({title_clause})")
            params.append(search_pattern)
        
        # Adiciona condição de conteúdo se necessário
        if criteria.include_content:
            conditions.append(f"({content_clause})")
            params.append(search_pattern)
        
        # Combina condições com OR
        if conditions:
            query += " OR ".join(conditions)
        else:
            # Se não houver condições, retorna lista vazia
            return []
        
        # Adiciona filtro de pasta se especificado
        if criteria.folder_ids:
            placeholders = ", ".join(["?" for _ in criteria.folder_ids])
            query += f" AND n.folder_id IN ({placeholders})"
            params.extend(criteria.folder_ids)
        
        query += " ORDER BY n.modified_at DESC"
        
        cursor.execute(query, params)
        
        notes = []
        for row in cursor.fetchall():
            note = Note(
                id=row[0],
                title=row[1],
                content=row[2],
                created_at=datetime.fromisoformat(row[3]),
                modified_at=datetime.fromisoformat(row[4]),
                folder_id=row[5]
            )
            # Adiciona o nome da pasta como propriedade para exibição
            note.folder_name = row[6]
            notes.append(note)
        
        return notes