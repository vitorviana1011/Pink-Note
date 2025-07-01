import re
from typing import List, Optional

class StringUtils:
    """Classe utilitária para operações com strings."""
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """Trunca uma string para um comprimento máximo e adiciona um sufixo se truncada.
        
        Args:
            text: A string a ser truncada
            max_length: O comprimento máximo
            suffix: O sufixo a ser adicionado se truncada (padrão: '...')
            
        Returns:
            A string truncada
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def is_empty_or_whitespace(text: Optional[str]) -> bool:
        """Verifica se uma string é None, vazia ou contém apenas espaços em branco.
        
        Args:
            text: A string a ser verificada
            
        Returns:
            True se a string for None, vazia ou contiver apenas espaços em branco, False caso contrário
        """
        return text is None or text.strip() == ''
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """Extrai palavras-chave de um texto removendo palavras comuns e pontuação.
        
        Args:
            text: O texto do qual extrair palavras-chave
            min_length: O comprimento mínimo de uma palavra-chave (padrão: 3)
            
        Returns:
            Uma lista de palavras-chave
        """
        if StringUtils.is_empty_or_whitespace(text):
            return []
        
        # Converte para minúsculas
        text = text.lower()
        
        # Remove pontuação e substitui por espaços
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Divide em palavras
        words = text.split()
        
        # Palavras comuns em português para filtrar
        stop_words = {
            'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'até',
            'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois', 'do',
            'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era', 'eram', 'éramos',
            'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este', 'estes', 'eu', 'foi',
            'fomos', 'for', 'foram', 'fosse', 'fossem', 'fui', 'há', 'isso', 'isto', 'já', 'lhe',
            'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'muito',
            'na', 'não', 'nas', 'nem', 'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos',
            'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por',
            'qual', 'quando', 'que', 'quem', 'são', 'se', 'seja', 'sejam', 'sem', 'será',
            'serão', 'seu', 'seus', 'só', 'somos', 'sou', 'sua', 'suas', 'também', 'te', 'tem',
            'tém', 'temos', 'tenho', 'teu', 'teus', 'tu', 'tua', 'tuas', 'um', 'uma', 'você',
            'vocês', 'vos', 'vosso', 'vossos'
        }
        
        # Filtra palavras comuns e palavras menores que min_length
        keywords = [word for word in words if word not in stop_words and len(word) >= min_length]
        
        return keywords
    
    @staticmethod
    def normalize_for_search(text: str, case_sensitive: bool = False) -> str:
        """Normaliza uma string para fins de busca.
        
        Args:
            text: A string a ser normalizada
            case_sensitive: Se deve preservar maiúsculas/minúsculas (padrão: False)
            
        Returns:
            A string normalizada
        """
        if StringUtils.is_empty_or_whitespace(text):
            return ''
        
        # Remove espaços em branco extras
        normalized = ' '.join(text.split())
        
        # Converte para minúsculas se não diferenciar maiúsculas/minúsculas
        if not case_sensitive:
            normalized = normalized.lower()
        
        return normalized
    
    @staticmethod
    def highlight_matches(text: str, search_term: str, case_sensitive: bool = False) -> str:
        """Destaca correspondências de um termo de busca em um texto usando HTML.
        
        Args:
            text: O texto onde buscar
            search_term: O termo de busca a ser destacado
            case_sensitive: Se a busca diferencia maiúsculas/minúsculas (padrão: False)
            
        Returns:
            O texto com correspondências destacadas usando tags HTML span
        """
        if StringUtils.is_empty_or_whitespace(text) or StringUtils.is_empty_or_whitespace(search_term):
            return text
        
        # Escapa caracteres especiais de HTML
        escaped_text = StringUtils.escape_html(text)
        
        # Prepara o termo de busca para regex
        escaped_search = re.escape(search_term)
        
        # Cria o padrão regex
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(f'({escaped_search})', flags)
        
        # Substitui correspondências pela versão destacada
        highlighted = pattern.sub(r'<span class="highlight">\1</span>', escaped_text)
        
        return highlighted
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escapa caracteres especiais de HTML em uma string.
        
        Args:
            text: A string a ser escapada
            
        Returns:
            A string escapada
        """
        if StringUtils.is_empty_or_whitespace(text):
            return ''
        
        # Substitui caracteres especiais de HTML por suas versões escapadas
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text