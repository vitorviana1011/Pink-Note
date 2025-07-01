from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Note:
    """Entidade que representa uma nota no sistema."""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    folder_id: int = 1  # Padrão para a pasta 'Geral'
    attachment_ids: List[int] = field(default_factory=list)
    
    def update_content(self, new_content: str) -> None:
        """Atualiza o conteúdo da nota e o horário de modificação."""
        self.content = new_content
        self.modified_at = datetime.now()
    
    def update_title(self, new_title: str) -> None:
        """Atualiza o título da nota e o horário de modificação."""
        self.title = new_title
        self.modified_at = datetime.now()
    
    def move_to_folder(self, new_folder_id: int) -> None:
        """Move a nota para outra pasta."""
        self.folder_id = new_folder_id
        self.modified_at = datetime.now()