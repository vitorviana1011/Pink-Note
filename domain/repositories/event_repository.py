from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain.entities.event import Event

class EventRepository(ABC):
    """Interface para operações do repositório de eventos."""
    
    @abstractmethod
    def get_all_events(self) -> List[Event]:
        """Recupera todos os eventos."""
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Recupera um evento pelo seu ID."""
        pass
    
    @abstractmethod
    def get_events_by_date(self, event_date: date) -> List[Event]:
        """Recupera todos os eventos para uma data específica."""
        pass
    
    @abstractmethod
    def add_event(self, event: Event) -> int:
        """Adiciona um novo evento e retorna seu ID."""
        pass
    
    @abstractmethod
    def update_event(self, event: Event) -> bool:
        """Atualiza um evento existente e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def delete_event(self, event_id: int) -> bool:
        """Exclui um evento pelo seu ID e retorna o status de sucesso."""
        pass