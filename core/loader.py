"""
Config Loader - Carga y parseo de archivos de configuración YAML
"""
import yaml
from typing import Dict


class ConfigLoader:
    """Cargador de archivos de configuración"""
    
    @staticmethod
    def load(filepath: str) -> Dict:
        """
        Carga un archivo YAML de configuración
        
        Args:
            filepath: Ruta al archivo YAML
            
        Returns:
            Diccionario con la configuración parseada
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            yaml.YAMLError: Si hay errores de parseo YAML
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                raise ValueError("El archivo YAML está vacío")
            
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo '{filepath}'")
        
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error al parsear YAML: {e}")
