"""
CLI Parser - Manejo de argumentos de línea de comandos
"""
import sys
from typing import Optional, Dict
from utils.output import ColorOutput as out


class CLIParser:
    """Parseador de argumentos de línea de comandos"""
    
    @staticmethod
    def parse_args() -> Optional[Dict]:
        """
        Parsea los argumentos de línea de comandos
        
        Returns:
            Dict con las opciones parseadas o None si no hay suficientes argumentos
        """
        if len(sys.argv) < 2:
            return None
        
        config_file = sys.argv[1]
        output_file: Optional[str] = None
        verbose = True
        max_ids_display: Optional[int] = None
        
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            
            if arg in ['-o', '--output']:
                if i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                else:
                    print(out.error("-o/--output requiere un nombre de archivo"))
                    sys.exit(1)
                    
            elif arg in ['-c', '--compact']:
                verbose = False
                i += 1
                
            elif arg in ['-l', '--limit']:
                if i + 1 < len(sys.argv):
                    try:
                        max_ids_display = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        print(out.error("--limit requiere un número entero"))
                        sys.exit(1)
                else:
                    print(out.error("--limit requiere un número"))
                    sys.exit(1)
                    
            else:
                print(out.error(f"Argumento desconocido: {arg}"))
                sys.exit(1)
        
        return {
            'config_file': config_file,
            'output_file': output_file,
            'verbose': verbose,
            'max_ids_display': max_ids_display
        }
    
    @staticmethod
    def print_usage():
        """Imprime la ayuda de uso del programa"""
        print(out.title("=" * 70))
        print(out.title("SIMULADOR DE MÁQUINA DE TURING"))
        print(out.title("=" * 70))
        print("\nUso:")
        print("  python main.py <archivo_yaml> [opciones]")
        print("\nOpciones:")
        print("  -o, --output <archivo>     Guardar reporte en archivo (sin colores)")
        print("  -c, --compact              Modo compacto (solo inicio y fin)")
        print("  -l, --limit <n>            Mostrar máximo n IDs")
        print("\nEjemplos:")
        print("  python main.py mt_recognizer_anbn.yaml")
        print("  python main.py mt_recognizer_anbn.yaml -o reporte.txt")
        print("  python main.py mt_recognizer_anbn.yaml -c -o reporte.txt")
        print("  python main.py mt_recognizer_anbn.yaml -l 20")
