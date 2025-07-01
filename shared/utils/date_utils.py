from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple

class DateUtils:
    """Classe utilitária para operações com datas e horários."""
    
    @staticmethod
    def get_current_datetime() -> datetime:
        """Obtém a data e hora atual.
        
        Returns:
            O datetime atual
        """
        return datetime.now()
    
    @staticmethod
    def get_current_date() -> date:
        """Obtém a data atual.
        
        Returns:
            A data atual
        """
        return date.today()
    
    @staticmethod
    def format_date(dt: date, format_str: str = '%d/%m/%Y') -> str:
        """Formata uma data de acordo com o formato especificado.
        
        Args:
            dt: A data a ser formatada
            format_str: A string de formato (padrão: '%d/%m/%Y')
            
        Returns:
            A data formatada como string
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = '%d/%m/%Y %H:%M:%S') -> str:
        """Formata um datetime de acordo com o formato especificado.
        
        Args:
            dt: O datetime a ser formatado
            format_str: A string de formato (padrão: '%d/%m/%Y %H:%M:%S')
            
        Returns:
            O datetime formatado como string
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = '%d/%m/%Y') -> Optional[date]:
        """Converte uma string em data de acordo com o formato especificado.
        
        Args:
            date_str: A string de data a ser convertida
            format_str: A string de formato (padrão: '%d/%m/%Y')
            
        Returns:
            A data convertida ou None se falhar
        """
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            # Tenta converter no formato ISO (YYYY-MM-DD) se o padrão falhar
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None
    
    @staticmethod
    def parse_datetime(datetime_str: str, format_str: str = '%d/%m/%Y %H:%M:%S') -> Optional[datetime]:
        """Converte uma string em datetime de acordo com o formato especificado.
        
        Args:
            datetime_str: A string de datetime a ser convertida
            format_str: A string de formato (padrão: '%d/%m/%Y %H:%M:%S')
            
        Returns:
            O datetime convertido ou None se falhar
        """
        try:
            return datetime.strptime(datetime_str, format_str)
        except ValueError:
            return None
    
    @staticmethod
    def parse_time(time_str: str, format_str: str = '%H:%M') -> Optional[datetime.time]:
        """Converte uma string em hora de acordo com o formato especificado.
        
        Args:
            time_str: A string de hora a ser convertida
            format_str: A string de formato (padrão: '%H:%M')
            
        Returns:
            A hora convertida ou None se falhar
        """
        try:
            return datetime.strptime(time_str, format_str).time()
        except ValueError:
            return None
    
    @staticmethod
    def get_month_range(year: int, month: int) -> Tuple[date, date]:
        """Obtém o primeiro e o último dia de um mês específico.
        
        Args:
            year: O ano
            month: O mês (1-12)
            
        Returns:
            Uma tupla com o primeiro e o último dia do mês
        """
        start_date = date(year, month, 1)
        
        # Calcula o último dia do mês
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    @staticmethod
    def get_week_range(dt: date) -> Tuple[date, date]:
        """Obtém o primeiro e o último dia da semana que contém a data especificada.
        
        Args:
            dt: A data
            
        Returns:
            Uma tupla com o primeiro (segunda-feira) e o último dia (domingo) da semana
        """
        # Calcula o início da semana (segunda-feira)
        start_date = dt - timedelta(days=dt.weekday())
        
        # Calcula o fim da semana (domingo)
        end_date = start_date + timedelta(days=6)
        
        return start_date, end_date
    
    @staticmethod
    def get_days_in_month(year: int, month: int) -> List[date]:
        """Obtém uma lista com todos os dias de um mês específico.
        
        Args:
            year: O ano
            month: O mês (1-12)
            
        Returns:
            Uma lista de datas para cada dia do mês
        """
        start_date, end_date = DateUtils.get_month_range(year, month)
        
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date)
            current_date += timedelta(days=1)
        
        return days
    
    @staticmethod
    def get_days_in_week(dt: date) -> List[date]:
        """Obtém uma lista com todos os dias da semana que contém a data especificada.
        
        Args:
            dt: A data
            
        Returns:
            Uma lista de datas para cada dia da semana
        """
        start_date, end_date = DateUtils.get_week_range(dt)
        
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date)
            current_date += timedelta(days=1)
        
        return days
    
    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """Verifica se dois datetimes estão no mesmo dia.
        
        Args:
            dt1: O primeiro datetime
            dt2: O segundo datetime
            
        Returns:
            True se ambos estiverem no mesmo dia, False caso contrário
        """
        return dt1.date() == dt2.date()
    
    @staticmethod
    def time_elapsed_since(dt: datetime) -> str:
        """Obtém uma string legível representando o tempo decorrido desde o datetime especificado.
        
        Args:
            dt: O datetime
            
        Returns:
            Uma string representando o tempo decorrido (ex: '2 horas atrás', '3 dias atrás')
        """
        now = datetime.now()
        delta = now - dt
        
        # Calcula o tempo decorrido em diferentes unidades
        seconds = delta.total_seconds()
        minutes = seconds // 60
        hours = minutes // 60
        days = delta.days
        
        if days > 0:
            if days == 1:
                return "1 dia atrás"
            else:
                return f"{days} dias atrás"
        elif hours > 0:
            if hours == 1:
                return "1 hora atrás"
            else:
                return f"{int(hours)} horas atrás"
        elif minutes > 0:
            if minutes == 1:
                return "1 minuto atrás"
            else:
                return f"{int(minutes)} minutos atrás"
        else:
            return "agora mesmo"