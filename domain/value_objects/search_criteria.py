from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class SearchCriteria:
    """Objeto de valor que representa critérios de busca para notas."""
    search_term: str
    folder_ids: List[int] = field(default_factory=list)  # Lista vazia significa buscar em todas as pastas
    include_title: bool = True
    include_content: bool = True
    case_sensitive: bool = False
    
    def __post_init__(self):
        """Valida os critérios de busca."""
        if not self.search_term.strip():
            raise ValueError("O termo de busca não pode ser vazio")
        
        if not self.include_title and not self.include_content:
            raise ValueError("Pelo menos um dos campos include_title ou include_content deve ser True")
    
    @property
    def normalized_search_term(self) -> str:
        """Obtém o termo de busca normalizado de acordo com a sensibilidade a maiúsculas/minúsculas."""
        if self.case_sensitive:
            return self.search_term
        return self.search_term.lower()