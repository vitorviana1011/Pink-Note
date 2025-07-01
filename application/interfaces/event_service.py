from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain.entities.event import Event
from domain.value_objects.date_range import DateRange

class EventService(ABC):
    """Interface para casos de uso relacionados a eventos."""
    
    @abstractmethod
    def get_all_events(self) -> List[Event]:
        """Obtém todos os eventos."""
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Obtém um evento pelo seu ID."""
        pass
    
    @abstractmethod
    def get_events_by_date(self, event_date: date) -> List[Event]:
        """Obtém todos os eventos para uma data específica."""
        pass
    
    @abstractmethod
    def get_events_in_range(self, date_range: DateRange) -> List[Event]:
        """Obtém todos os eventos dentro de um intervalo de datas."""
        pass
    
    @abstractmethod
    def create_event(self, title: str, description: str, event_date: date) -> int:
        """Cria um novo evento e retorna seu ID."""
        pass
    
    @abstractmethod
    def update_event(self, event_id: int, title: str, description: str, event_date: date) -> bool:
        """Atualiza um evento existente e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def delete_event(self, event_id: int) -> bool:
        """Exclui um evento pelo seu ID e retorna o status de sucesso."""
        pass
    
    @abstractmethod
    def get_dates_with_events(self, date_range: DateRange) -> List[date]:
        """Obtém todas as datas dentro de um intervalo que possuem eventos."""
        pass