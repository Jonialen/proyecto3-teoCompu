"""
Simulator - Orquestador de simulaciones y reportes
"""
from typing import Optional, List
from core.machine import TuringMachine
from core.executor import TuringExecutor, ExecutionResult
from utils.reporter import Reporter


class Simulator:
    """Orquestador de simulaciones de Máquina de Turing"""
    
    def __init__(self, machine: TuringMachine, output_file: Optional[str] = None,
                 verbose: bool = True, max_ids_display: Optional[int] = None):
        """
        Inicializa el simulador
        
        Args:
            machine: Máquina de Turing a simular
            output_file: Archivo de salida para el reporte (opcional)
            verbose: Mostrar todas las descripciones instantáneas
            max_ids_display: Límite de IDs a mostrar (None = todos)
        """
        self.machine = machine
        self.executor = TuringExecutor(machine)
        self.reporter = Reporter(output_file, verbose, max_ids_display)
        self.results: List[ExecutionResult] = []
    
    def run_all_simulations(self):
        """Ejecuta todas las simulaciones configuradas"""
        
        # Imprimir encabezado
        self.reporter.print_header(self.machine)
        
        # Ejecutar cada cadena de simulación
        for i, input_string in enumerate(self.machine.simulation_strings, 1):
            result = self._run_single_simulation(i, input_string)
            self.results.append(result)
        
        # Imprimir resumen comparativo
        if len(self.results) > 1:
            self.reporter.print_comparative_summary(self.results, 
                                                   self.machine.simulation_strings)
        
        # Guardar reporte en archivo si se especificó
        self.reporter.save_to_file()
    
    def _run_single_simulation(self, index: int, input_string: str) -> ExecutionResult:
        """
        Ejecuta una simulación individual
        
        Args:
            index: Número de la simulación
            input_string: Cadena de entrada
            
        Returns:
            ExecutionResult con los resultados
        """
        # Imprimir encabezado de simulación
        self.reporter.print_simulation_header(index, input_string)
        
        # Ejecutar la máquina
        result = self.executor.execute(input_string)
        
        # Imprimir resultados
        self.reporter.print_execution_result(result, input_string)
        
        return result
