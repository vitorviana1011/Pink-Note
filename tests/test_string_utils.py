import unittest
from shared.utils.string_utils import StringUtils

class TestStringUtils(unittest.TestCase):
    """Casos de teste para a classe StringUtils."""
    
    def test_truncate(self):
        """Testa o método truncate."""
        # Testa truncamento normal
        self.assertEqual(StringUtils.truncate("Hello, world!", 5), "Hello...")
        
        # Testa quando não é necessário truncar
        self.assertEqual(StringUtils.truncate("Hello", 10), "Hello")
        
        # Testa sufixo personalizado
        self.assertEqual(StringUtils.truncate("Hello, world!", 5, "..."), "Hello...")
        
        # Testa string vazia
        self.assertEqual(StringUtils.truncate("", 5), "")
    
    def test_is_empty_or_whitespace(self):
        """Testa o método is_empty_or_whitespace."""
        # Testa string vazia
        self.assertTrue(StringUtils.is_empty_or_whitespace(""))
        
        # Testa string com apenas espaços em branco
        self.assertTrue(StringUtils.is_empty_or_whitespace(" \t\n"))
        
        # Testa string não vazia
        self.assertFalse(StringUtils.is_empty_or_whitespace("Hello"))
    
    def test_normalize_for_search(self):
        """Testa o método normalize_for_search."""
        # Testa normalização sem diferenciar maiúsculas/minúsculas
        self.assertEqual(StringUtils.normalize_for_search("  Hello,  World! "), "hello, world!")
        
        # Testa normalização diferenciando maiúsculas/minúsculas
        self.assertEqual(StringUtils.normalize_for_search("  Hello,  World! ", True), "Hello, World!")
        
        # Testa string vazia
        self.assertEqual(StringUtils.normalize_for_search(""), "")

if __name__ == '__main__':
    unittest.main()