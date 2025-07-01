from typing import List, Optional

from domain.entities.folder import Folder
from domain.repositories.folder_repository import FolderRepository

class FolderRepositoryImpl(FolderRepository):
    """Implementação SQLite do repositório de pastas."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_all_folders(self) -> List[Folder]:
        """Recupera todas as pastas."""
        cursor = self.db.cursor()
        cursor.execute("SELECT id, name, parent_id, path FROM folders ORDER BY path")
        
        folders = []
        for row in cursor.fetchall():
            folder = Folder(
                id=row[0],
                name=row[1],
                parent_id=row[2],
                path=row[3]
            )
            folders.append(folder)
        
        return folders
    
    def get_folder_by_id(self, folder_id: int) -> Optional[Folder]:
        """Recupera uma pasta pelo seu ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, name, parent_id, path FROM folders WHERE id = ?",
            (folder_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return Folder(
            id=row[0],
            name=row[1],
            parent_id=row[2],
            path=row[3]
        )
    
    def get_subfolders(self, parent_id: Optional[int] = None) -> List[Folder]:
        """Recupera todas as subpastas de uma pasta pai."""
        cursor = self.db.cursor()
        
        if parent_id is None:
            cursor.execute(
                "SELECT id, name, parent_id, path FROM folders WHERE parent_id IS NULL ORDER BY name"
            )
        else:
            cursor.execute(
                "SELECT id, name, parent_id, path FROM folders WHERE parent_id = ? ORDER BY name",
                (parent_id,)
            )
        
        folders = []
        for row in cursor.fetchall():
            folder = Folder(
                id=row[0],
                name=row[1],
                parent_id=row[2],
                path=row[3]
            )
            folders.append(folder)
        
        return folders
    
    def create_folder(self, folder: Folder) -> int:
        """Cria uma nova pasta e retorna seu ID."""
        cursor = self.db.cursor()
        
        # Verifica se já existe uma pasta com o mesmo nome no mesmo nível
        if folder.parent_id is None:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id IS NULL",
                (folder.name,)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id = ?",
                (folder.name, folder.parent_id)
            )
        
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"Já existe uma pasta chamada '{folder.name}' neste nível")
        
        # Calcula o caminho completo para a nova pasta
        path = folder.name
        if folder.parent_id is not None:
            cursor.execute("SELECT path FROM folders WHERE id = ?", (folder.parent_id,))
            parent_path = cursor.fetchone()[0]
            path = f"{parent_path}/{folder.name}"
        
        # Insere a nova pasta
        cursor.execute(
            "INSERT INTO folders (name, parent_id, path) VALUES (?, ?, ?)",
            (folder.name, folder.parent_id, path)
        )
        
        self.db.commit()
        return cursor.lastrowid
    
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Renomeia uma pasta e retorna o status de sucesso."""
        cursor = self.db.cursor()
        
        # Obtém informações atuais da pasta
        cursor.execute(
            "SELECT parent_id, path FROM folders WHERE id = ?",
            (folder_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return False
        
        parent_id, old_path = row
        
        # Verifica se já existe uma pasta com o mesmo nome no mesmo nível
        if parent_id is None:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id IS NULL AND id != ?",
                (new_name, folder_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id = ? AND id != ?",
                (new_name, parent_id, folder_id)
            )
        
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"Já existe uma pasta chamada '{new_name}' neste nível")
        
        # Calcula o novo caminho
        old_name = old_path.split('/')[-1]
        new_path = old_path.replace(old_name, new_name)
        
        # Inicia uma transação
        self.db.execute("BEGIN TRANSACTION")
        
        try:
            # Atualiza o nome e caminho da pasta
            cursor.execute(
                "UPDATE folders SET name = ?, path = ? WHERE id = ?",
                (new_name, new_path, folder_id)
            )
            
            # Atualiza os caminhos de todas as subpastas
            cursor.execute(
                "SELECT id, path FROM folders WHERE path LIKE ?",
                (f"{old_path}/%",)
            )
            
            for subfolder_id, subfolder_path in cursor.fetchall():
                new_subfolder_path = subfolder_path.replace(old_path, new_path)
                cursor.execute(
                    "UPDATE folders SET path = ? WHERE id = ?",
                    (new_subfolder_path, subfolder_id)
                )
            
            self.db.execute("COMMIT")
            return True
        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e
    
    def delete_folder(self, folder_id: int) -> bool:
        """Exclui uma pasta e retorna o status de sucesso."""
        cursor = self.db.cursor()
        
        # Verifica se é a pasta 'Geral' (ID 1), que não pode ser excluída
        if folder_id == 1:
            return False
        
        # Obtém todas as notas nesta pasta e em suas subpastas
        cursor.execute(
            """SELECT n.id 
               FROM notes n 
               JOIN folders f ON n.folder_id = f.id 
               WHERE f.id = ? OR f.path LIKE (SELECT path || '/%' FROM folders WHERE id = ?)""",
            (folder_id, folder_id)
        )
        
        note_ids = [row[0] for row in cursor.fetchall()]
        
        # Inicia uma transação
        self.db.execute("BEGIN TRANSACTION")
        
        try:
            # Move todas as notas para a pasta 'Geral' (ID 1)
            for note_id in note_ids:
                cursor.execute(
                    "UPDATE notes SET folder_id = 1 WHERE id = ?",
                    (note_id,)
                )
            
            # Exclui a pasta (subpastas serão excluídas via ON DELETE CASCADE)
            cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            
            self.db.execute("COMMIT")
            return True
        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e
    
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move uma pasta para um novo pai e retorna o status de sucesso."""
        cursor = self.db.cursor()
        
        # Verifica se é a pasta 'Geral' (ID 1), que não pode ser movida
        if folder_id == 1:
            return False
        
        # Obtém informações atuais da pasta
        cursor.execute(
            "SELECT name, parent_id, path FROM folders WHERE id = ?",
            (folder_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return False
        
        name, old_parent_id, old_path = row
        
        # Verifica se a pasta já está no local solicitado
        if old_parent_id == new_parent_id:
            return True
        
        # Verifica se o novo pai existe (se não for None)
        if new_parent_id is not None:
            cursor.execute("SELECT id FROM folders WHERE id = ?", (new_parent_id,))
            if cursor.fetchone() is None:
                return False
            
            # Verifica se o novo pai é a própria pasta ou uma de suas subpastas
            if new_parent_id == folder_id:
                return False
            
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE id = ? AND path LIKE ?",
                (new_parent_id, f"{old_path}/%")
            )
            if cursor.fetchone()[0] > 0:
                return False
        
        # Verifica se já existe uma pasta com o mesmo nome no destino
        if new_parent_id is None:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id IS NULL AND id != ?",
                (name, folder_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id = ? AND id != ?",
                (name, new_parent_id, folder_id)
            )
        
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"Já existe uma pasta chamada '{name}' no destino")
        
        # Calcula o novo caminho
        new_path = name
        if new_parent_id is not None:
            cursor.execute("SELECT path FROM folders WHERE id = ?", (new_parent_id,))
            parent_path = cursor.fetchone()[0]
            new_path = f"{parent_path}/{name}"
        
        # Inicia uma transação
        self.db.execute("BEGIN TRANSACTION")
        
        try:
            # Atualiza o pai e caminho da pasta
            cursor.execute(
                "UPDATE folders SET parent_id = ?, path = ? WHERE id = ?",
                (new_parent_id, new_path, folder_id)
            )
            
            # Atualiza os caminhos de todas as subpastas
            cursor.execute(
                "SELECT id, path FROM folders WHERE path LIKE ?",
                (f"{old_path}/%",)
            )
            
            for subfolder_id, subfolder_path in cursor.fetchall():
                new_subfolder_path = subfolder_path.replace(old_path, new_path)
                cursor.execute(
                    "UPDATE folders SET path = ? WHERE id = ?",
                    (new_subfolder_path, subfolder_id)
                )
            
            self.db.execute("COMMIT")
            return True
        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e
    
    def get_folder_note_count(self, folder_id: int) -> int:
        """Obtém o número de notas em uma pasta."""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM notes WHERE folder_id = ?", (folder_id,))
        return cursor.fetchone()[0]