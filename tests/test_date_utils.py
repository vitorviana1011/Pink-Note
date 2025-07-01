import unittest
from datetime import datetime, date, timedelta
from shared.utils.date_utils import DateUtils

class TestDateUtils(unittest.TestCase):
    """Casos de teste para a classe DateUtils."""
    
    def test_format_date(self):
        """Testa o método format_date."""
        # Cria uma data de teste
        test_date = date(2023, 5, 15)
        
        # Testa formato padrão
        self.assertEqual(DateUtils.format_date(test_date), "15/05/2023")
        
        # Testa formato personalizado
        self.assertEqual(DateUtils.format_date(test_date, "%Y-%m-%d"), "2023-05-15")
    
    def test_parse_date(self):
        """Testa o método parse_date."""
        # Testa formato padrão
        parsed_date = DateUtils.parse_date("15/05/2023")
        self.assertEqual(parsed_date, date(2023, 5, 15))
        
        # Testa formato personalizado
        parsed_date = DateUtils.parse_date("2023-05-15", "%Y-%m-%d")
        self.assertEqual(parsed_date, date(2023, 5, 15))
        
        # Testa data inválida
        self.assertIsNone(DateUtils.parse_date("invalid date"))
    
    def test_get_month_range(self):
        """Testa o método get_month_range."""
        # Testa para maio de 2023
        start_date, end_date = DateUtils.get_month_range(2023, 5)
        
        self.assertEqual(start_date, date(2023, 5, 1))
        self.assertEqual(end_date, date(2023, 5, 31))
        
        # Testa para fevereiro de 2023 (ano não bissexto)
        start_date, end_date = DateUtils.get_month_range(2023, 2)
        
        self.assertEqual(start_date, date(2023, 2, 1))
        self.assertEqual(end_date, date(2023, 2, 28))
        
        # Testa para fevereiro de 2024 (ano bissexto)
        start_date, end_date = DateUtils.get_month_range(2024, 2)
        
        self.assertEqual(start_date, date(2024, 2, 1))
        self.assertEqual(end_date, date(2024, 2, 29))

if __name__ == '__main__':
    unittest.main()