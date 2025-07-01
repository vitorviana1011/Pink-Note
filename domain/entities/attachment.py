from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Attachment:
    """Entidade que representa um anexo de arquivo para uma nota."""
    id: Optional[int] = None
    note_id: int = 0
    file_path: str = ""
    file_name: str = ""
    file_type: str = ""  # ex: "pdf", "image", etc.
    created_at: datetime = datetime.now()
    
    @property
    def is_pdf(self) -> bool:
        """Verifica se o anexo é um arquivo PDF."""
        return self.file_type.lower() == "pdf"
    
    @property
    def is_image(self) -> bool:
        """Verifica se o anexo é um arquivo de imagem."""
        image_types = ["jpg", "jpeg", "png", "gif", "bmp"]
        return self.file_type.lower() in image_types