from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Folder:
    """Entidade que representa uma pasta na estrutura hierárquica."""
    id: Optional[int] = None
    name: str = ""
    parent_id: Optional[int] = None  # None para pastas raiz
    path: str = ""  # Representação do caminho completo (ex: "Raiz/Subpasta/SubSubpasta")
    
    @property
    def is_root(self) -> bool:
        """Verifica se esta é uma pasta de nível raiz."""
        return self.parent_id is None
    
    def get_folder_name(self) -> str:
        """Obtém o nome da pasta a partir do caminho."""
        if not self.path:
            return self.name
        return self.path.split("/")[-1]
    
    def get_parent_path(self) -> str:
        """Obtém o caminho do pai."""
        if not self.path or "/" not in self.path:
            return ""
        return "/".join(self.path.split("/")[:-1])