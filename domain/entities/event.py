from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    """Entidade que representa um evento de calendário no sistema."""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    date: datetime = field(default_factory=datetime.now)
    
    def update_title(self, new_title: str) -> None:
        """Atualiza o título do evento."""
        self.title = new_title
    
    def update_description(self, new_description: str) -> None:
        """Atualiza a descrição do evento."""
        self.description = new_description
    
    def update_date(self, new_date: datetime) -> None:
        """Atualiza a data do evento."""
        self.date = new_date