"""
Reporter - Generación y formato de reportes de simulación
"""
from typing import Optional, List
from core.machine import TuringMachine
from core.executor import ExecutionResult
from utils.output import ColorOutput as out, TextFormatter as fmt


class Reporter:
    """Generador de reportes de simulación"""
    
    def __init__(self, output_file: Optional[str] = None, 
                 verbose: bool = True, 
                 max_ids_display: Optional[int] = None):
        """
        Inicializa el reportero
        
        Args:
            output_file: Archivo para guardar reporte sin colores
            verbose: Mostrar todas las IDs
            max_ids_display: Límite de IDs a mostrar
        """
        self.output_file = output_file
        self.verbose = verbose
        self.max_ids_display = max_ids_display
        self.plain_lines: List[str] = []
    
    def _write(self, text: str = ""):
        """Escribe en consola y guarda versión sin colores"""
        print(text)
        self.plain_lines.append(out.strip_ansi(text))
    
    def print_header(self, machine: TuringMachine):
        """Imprime encabezado del reporte"""
        self._write(out.title(fmt.separator()))
        self._write(out.title("SIMULADOR DE MÁQUINA DE TURING"))
        self._write(out.title(fmt.separator()))
        
        self._write(f"\nEstados: {', '.join(machine.states)}")
        self._write(f"Estado inicial: {machine.initial_state}")
        self._write(f"Estados finales: {', '.join(machine.final_states)}")
        self._write(f"Alfabeto: {{{', '.join(machine.alphabet)}}}")
        
        tape_symbols = [s if s else '␣' for s in machine.tape_alphabet]
        self._write(f"Alfabeto de cinta: {{{', '.join(tape_symbols)}}}")
        self._write(f"\nNúmero de transiciones: {len(machine.delta)}")
        self._write(out.title(fmt.separator()))
    
    def print_simulation_header(self, index: int, input_string: str):
        """Imprime encabezado de una simulación"""
        self._write(out.title("\n" + fmt.separator()))
        self._write(out.title(f"SIMULACIÓN {index}: \"{input_string}\""))
        self._write(out.title(fmt.separator()))
    
    def print_execution_result(self, result: ExecutionResult, input_string: str):
        """Imprime resultados de una ejecución"""
        
        # Descripciones instantáneas
        self._print_ids(result.ids)
        
        # Cinta final
        self._print_final_tape(input_string, result.final_tape)
        
        # Estadísticas
        self._print_statistics(result.stats)
        
        # Mensaje y resultado
        self._write(out.info("\nMensaje: " + result.message))
        
        if result.accepted:
            self._write(out.success("RESULTADO: CADENA ACEPTADA"))
        else:
            self._write(out.error("RESULTADO: CADENA RECHAZADA"))
        
        self._write(out.title(fmt.separator()))
    
    def _print_ids(self, ids: List[str]):
        """Imprime descripciones instantáneas"""
        self._write(f"\nDescripciones Instantáneas ({len(ids)} pasos):")
        self._write(fmt.separator("-"))
        
        if not self.verbose:
            # Modo compacto: solo inicio y fin
            self._write(f"  0: {ids[0]}")
            if len(ids) > 1:
                self._write("  ...")
                self._write(f"  {len(ids)-1}: {ids[-1]}")
        
        elif self.max_ids_display and len(ids) > self.max_ids_display:
            # Modo limitado: mostrar primeros y últimos
            half = self.max_ids_display // 2
            
            for j in range(half):
                self._write(f"  {j}: {ids[j]}")
            
            self._write(f"  ... ({len(ids)-self.max_ids_display} pasos omitidos) ...")
            
            for j in range(len(ids)-half, len(ids)):
                self._write(f"  {j}: {ids[j]}")
        
        else:
            # Modo completo: mostrar todas
            for j, id_str in enumerate(ids):
                self._write(f"  {j}: {id_str}")
        
        self._write(fmt.separator("-"))
    
    def _print_final_tape(self, input_string: str, final_tape: str):
        """Imprime información de la cinta final"""
        self._write(out.info("\nCINTA FINAL:"))
        self._write(f"   Entrada: \"{input_string}\"")
        self._write(f"   Salida:  \"{final_tape}\"")
        
        if final_tape != input_string:
            self._write(out.warn("   La cinta fue modificada"))
        else:
            self._write(out.info("   La cinta no fue modificada"))
    
    def _print_statistics(self, stats: dict):
        """Imprime estadísticas de ejecución"""
        self._write(out.info("\nESTADÍSTICAS:"))
        self._write(f"   Pasos ejecutados: {stats['steps']}")
        self._write(f"   Tiempo de ejecución: {stats['execution_time']:.6f} s")
        self._write(f"   Tamaño máximo de cinta: {stats['max_tape_size']} celdas")
        self._write(f"   Transiciones únicas usadas: {stats['unique_transitions']}")
        self._write(f"   Estado final: {stats['final_state']}")
        
        # Estados más visitados
        sorted_states = sorted(
            stats['states_visited'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        self._write("   Estados más visitados:")
        for state, count in sorted_states[:3]:
            self._write(f"     - {state}: {count} veces")
    
    def print_comparative_summary(self, results: List[ExecutionResult], 
                                 input_strings: List[str]):
        """Imprime resumen comparativo de todas las simulaciones"""
        self._write(out.title("\n" + fmt.separator()))
        self._write(out.title("RESUMEN COMPARATIVO"))
        self._write(out.title(fmt.separator()))
        
        # Tabla de resultados
        self._write(f"\n{'Entrada':<15} {'Salida':<15} {'Resultado':<12} "
                   f"{'Pasos':<8} {'Tiempo (s)':<12}")
        self._write(fmt.separator("-"))
        
        for i, result in enumerate(results):
            entrada = fmt.truncate(input_strings[i], 12)
            salida = fmt.truncate(result.final_tape, 12)
            
            result_label = "ACEPTADA" if result.accepted else "RECHAZADA"
            colored_result = (out.success(result_label) if result.accepted 
                            else out.error(result_label))
            
            self._write(f"{entrada:<15} {salida:<15} {colored_result:<12} "
                       f"{result.stats['steps']:<8} "
                       f"{result.stats['execution_time']:<12.6f}")
        
        self._write(fmt.separator("-"))
        
        # Estadísticas globales
        self._print_global_statistics(results)
    
    def _print_global_statistics(self, results: List[ExecutionResult]):
        """Imprime estadísticas globales"""
        total_steps = sum(r.stats['steps'] for r in results)
        total_time = sum(r.stats['execution_time'] for r in results)
        accepted_count = sum(1 for r in results if r.accepted)
        rejected_count = len(results) - accepted_count
        
        self._write(out.info("\nESTADÍSTICAS GLOBALES:"))
        self._write(f"   Total simulaciones: {len(results)}")
        self._write(f"   Cadenas aceptadas: {accepted_count}/{len(results)}")
        self._write(f"   Cadenas rechazadas: {rejected_count}/{len(results)}")
        self._write(f"   Pasos totales: {total_steps}")
        self._write(f"   Tiempo total: {total_time:.6f} s")
        self._write(f"   Promedio pasos/cadena: {total_steps/len(results):.2f}")
        self._write(f"   Promedio tiempo/cadena: {total_time/len(results):.6f} s")
        self._write(out.title(fmt.separator()))
    
    def save_to_file(self):
        """Guarda el reporte en un archivo sin colores ANSI"""
        if not self.output_file:
            return
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.plain_lines))
            print(out.success(f"\nReporte guardado en {self.output_file}"))
        except Exception as e:
            print(out.error(f"Error al guardar el archivo: {e}"))
