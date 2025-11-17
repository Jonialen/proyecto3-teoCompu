#!/usr/bin/env python3
"""
Simulador de Máquina de Turing - Punto de Entrada Principal
"""
import sys
from pathlib import Path

from core.cli import CLIParser
from core.loader import ConfigLoader
from core.validator import TuringMachineValidator
from core.machine import TuringMachine
from core.simulator import Simulator
from utils.output import ColorOutput as out


def main():
    """Punto de entrada principal del simulador"""
    
    # Parsear argumentos de línea de comandos
    args = CLIParser.parse_args()
    
    if not args:
        CLIParser.print_usage()
        sys.exit(1)
    
    config_file = args['config_file']
    
    # Validar que el archivo existe
    if not Path(config_file).exists():
        print(out.error(f"No se encontró el archivo '{config_file}'"))
        sys.exit(1)
    
    try:
        # Cargar configuración
        print(out.info("Cargando configuración..."))
        config = ConfigLoader.load(config_file)
        
        # Validar configuración
        print(out.info("Validando configuración..."))
        errors = TuringMachineValidator.validate(config)
        
        if errors:
            print(out.error("\nERRORES DE VALIDACIÓN ENCONTRADOS:"))
            for error in errors:
                print(f" - {error}")
            sys.exit(1)
        
        print(out.success("Configuración válida\n"))
        
        # Crear máquina de Turing
        machine = TuringMachine(config)
        
        # Crear y ejecutar simulador
        simulator = Simulator(
            machine=machine,
            output_file=args.get('output_file'),
            verbose=args.get('verbose', True),
            max_ids_display=args.get('max_ids_display')
        )
        
        simulator.run_all_simulations()
        
    except Exception as e:
        print(out.error(f"Error inesperado: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
