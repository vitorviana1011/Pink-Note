from datetime import date, datetime
from typing import List, Optional, Dict, Any

from domain.entities.event import Event
from domain.value_objects.date_range import DateRange
from application.interfaces.event_service import EventService
from shared.utils.logger import Logger
from shared.utils.date_utils import DateUtils

class EventController:
    """Controlador para operações relacionadas a eventos na camada de apresentação."""
    
    def __init__(self, event_service: EventService):
        """Inicializa o controlador com os serviços necessários.
        
        Args:
            event_service: O serviço de eventos
        """
        self.event_service = event_service
        self.logger = Logger.get_instance()
        self.date_utils = DateUtils()
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Obtém todos os eventos.
        
        Returns:
            Uma lista de dicionários representando os eventos
        """
        try:
            events = self.event_service.get_all_events()
            return [self._event_to_dict(event) for event in events]
        except Exception as e:
            self.logger.error(f"Erro ao obter todos os eventos: {str(e)}")
            return []
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um evento pelo seu ID.
        
        Args:
            event_id: O ID do evento
            
        Returns:
            Um dicionário representando o evento, ou None se não encontrado
        """
        try:
            event = self.event_service.get_event_by_id(event_id)
            if event:
                return self._event_to_dict(event)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter evento {event_id}: {str(e)}")
            return None
    
    def get_events_by_date(self, event_date: date) -> List[Dict[str, Any]]:
        """Obtém todos os eventos para uma data específica.
        
        Args:
            event_date: A data
            
        Returns:
            Uma lista de dicionários representando os eventos
        """
        try:
            events = self.event_service.get_events_by_date(event_date)
            return [self._event_to_dict(event) for event in events]
        except Exception as e:
            self.logger.error(f"Erro ao obter eventos para a data {event_date}: {str(e)}")
            return []
    
    def get_events_in_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Obtém todos os eventos dentro de um intervalo de datas.
        
        Args:
            start_date: A data inicial
            end_date: A data final
            
        Returns:
            Uma lista de dicionários representando os eventos
        """
        try:
            # Cria intervalo de datas
            date_range = DateRange(start_date=start_date, end_date=end_date)
            
            # Obtém eventos no intervalo
            events = self.event_service.get_events_in_range(date_range)
            return [self._event_to_dict(event) for event in events]
        except Exception as e:
            self.logger.error(f"Erro ao obter eventos no intervalo {start_date} a {end_date}: {str(e)}")
            return []
    
    def get_events_for_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Obtém todos os eventos para um mês específico.
        
        Args:
            year: O ano
            month: O mês (1-12)
            
        Returns:
            Uma lista de dicionários representando os eventos
        """
        try:
            # Obtém as datas inicial e final do mês
            start_date, end_date = self.date_utils.get_month_range(year, month)
            
            # Obtém eventos no intervalo do mês
            return self.get_events_in_range(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Erro ao obter eventos para o mês {month}/{year}: {str(e)}")
            return []
    
    def get_events_for_week(self, week_date: date) -> List[Dict[str, Any]]:
        """Obtém todos os eventos para a semana que contém a data especificada.
        
        Args:
            week_date: Uma data da semana desejada
            
        Returns:
            Uma lista de dicionários representando os eventos
        """
        try:
            # Obtém as datas inicial e final da semana
            start_date, end_date = self.date_utils.get_week_range(week_date)
            
            # Obtém eventos no intervalo da semana
            return self.get_events_in_range(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Erro ao obter eventos para a semana de {week_date}: {str(e)}")
            return []
    
    def create_event(self, title: str, description: str, event_date: date) -> Optional[Dict[str, Any]]:
        """Cria um novo evento.
        
        Args:
            title: O título do evento
            description: A descrição do evento
            event_date: A data do evento
            
        Returns:
            Um dicionário representando o evento criado, ou None se falhar
        """
        try:
            # Converte para datetime se necessário
            event_datetime = event_date
            if isinstance(event_date, date) and not isinstance(event_date, datetime):
                # Converte para datetime à meia-noite
                event_datetime = datetime.combine(event_date, datetime.min.time())
            
            # Cria o evento
            event_id = self.event_service.create_event(title, description, event_datetime)
            if event_id:
                return self.get_event_by_id(event_id)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao criar evento: {str(e)}")
            return None
    
    def update_event(self, event_id: int, title: str, description: str, event_date: date) -> bool:
        """Atualiza um evento existente.
        
        Args:
            event_id: O ID do evento
            title: O novo título
            description: A nova descrição
            event_date: A nova data do evento
            
        Returns:
            True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            # Converte para datetime se necessário
            event_datetime = event_date
            if isinstance(event_date, date) and not isinstance(event_date, datetime):
                # Converte para datetime à meia-noite
                event_datetime = datetime.combine(event_date, datetime.min.time())
            
            return self.event_service.update_event(event_id, title, description, event_datetime)
        except Exception as e:
            self.logger.error(f"Erro ao atualizar evento {event_id}: {str(e)}")
            return False
    
    def delete_event(self, event_id: int) -> bool:
        """Exclui um evento.
        
        Args:
            event_id: O ID do evento
            
        Returns:
            True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            return self.event_service.delete_event(event_id)
        except Exception as e:
            self.logger.error(f"Erro ao excluir evento {event_id}: {str(e)}")
            return False
    
    def get_dates_with_events(self, year: int, month: int) -> List[str]:
        """Obtém todas as datas de um mês que possuem eventos.
        
        Args:
            year: O ano
            month: O mês (1-12)
            
        Returns:
            Uma lista de strings de datas no formato ISO (YYYY-MM-DD)
        """
        try:
            # Obtém as datas inicial e final do mês
            start_date, end_date = self.date_utils.get_month_range(year, month)
            
            # Cria intervalo de datas
            date_range = DateRange(start_date=start_date, end_date=end_date)
            
            # Obtém datas com eventos
            dates = self.event_service.get_dates_with_events(date_range)
            
            # Converte para strings no formato ISO
            return [date.isoformat() for date in dates]
        except Exception as e:
            self.logger.error(f"Erro ao obter datas com eventos para {month}/{year}: {str(e)}")
            return []
    
    def _event_to_dict(self, event: Event) -> Dict[str, Any]:
        """Converte uma entidade Event para um dicionário.
        
        Args:
            event: A entidade Event
            
        Returns:
            Um dicionário representando o evento
        """
        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.isoformat() if event.date else None,
            'formatted_date': self.date_utils.format_datetime(event.date) if event.date else None
        }