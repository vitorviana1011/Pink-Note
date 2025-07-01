from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterator, List

@dataclass(frozen=True)
class DateRange:
    """Objeto de valor que representa um intervalo de datas."""
    start_date: date
    end_date: date
    
    def __post_init__(self):
        """Valida se start_date é anterior ou igual a end_date."""
        if self.start_date > self.end_date:
            raise ValueError("start_date deve ser anterior ou igual a end_date")
    
    def contains(self, check_date: date) -> bool:
        """Verifica se uma data está dentro deste intervalo."""
        return self.start_date <= check_date <= self.end_date
    
    def days(self) -> int:
        """Obtém o número de dias neste intervalo."""
        return (self.end_date - self.start_date).days + 1
    
    def iterate_days(self) -> Iterator[date]:
        """Itera por todos os dias neste intervalo."""
        current = self.start_date
        while current <= self.end_date:
            yield current
            current += timedelta(days=1)
    
    def to_list(self) -> List[date]:
        """Converte o intervalo para uma lista de datas."""
        return list(self.iterate_days())