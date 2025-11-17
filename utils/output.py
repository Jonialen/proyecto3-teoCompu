"""
Output Utils - Utilidades para colores ANSI y formato de texto
"""
import re


class ANSIColors:
    """Códigos de colores ANSI para terminal"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"


class ColorOutput:
    """Utilidades para output con colores"""
    
    @staticmethod
    def success(msg: str) -> str:
        """Formatea mensaje de éxito (verde)"""
        return f"{ANSIColors.GREEN}{msg}{ANSIColors.RESET}"
    
    @staticmethod
    def error(msg: str) -> str:
        """Formatea mensaje de error (rojo)"""
        return f"{ANSIColors.RED}{msg}{ANSIColors.RESET}"
    
    @staticmethod
    def warn(msg: str) -> str:
        """Formatea mensaje de advertencia (amarillo)"""
        return f"{ANSIColors.YELLOW}{msg}{ANSIColors.RESET}"
    
    @staticmethod
    def info(msg: str) -> str:
        """Formatea mensaje informativo (cyan)"""
        return f"{ANSIColors.CYAN}{msg}{ANSIColors.RESET}"
    
    @staticmethod
    def title(msg: str) -> str:
        """Formatea título (azul negrita)"""
        return f"{ANSIColors.BOLD}{ANSIColors.BLUE}{msg}{ANSIColors.RESET}"
    
    @staticmethod
    def strip_ansi(text: str) -> str:
        """
        Elimina códigos ANSI de un texto
        
        Args:
            text: Texto con códigos ANSI
            
        Returns:
            Texto sin códigos ANSI
        """
        ansi_pattern = re.compile(r'\033\[[0-9;]*m')
        return ansi_pattern.sub('', text)


class TextFormatter:
    """Utilidades para formateo de texto"""
    
    @staticmethod
    def separator(char: str = "=", length: int = 70) -> str:
        """Genera una línea separadora"""
        return char * length
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Trunca texto si excede longitud máxima
        
        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            suffix: Sufijo para texto truncado
            
        Returns:
            Texto truncado o original si es menor a max_length
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def pad_right(text: str, width: int) -> str:
        """Rellena texto a la derecha con espacios"""
        return text.ljust(width)
    
    @staticmethod
    def pad_left(text: str, width: int) -> str:
        """Rellena texto a la izquierda con espacios"""
        return text.rjust(width)
