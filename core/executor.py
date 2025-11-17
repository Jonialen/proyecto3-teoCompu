"""
Executor - Motor de ejecución de la Máquina de Turing
"""
import time
from typing import List, Tuple, Dict
from core.machine import TuringMachine


class ExecutionResult:
    """Resultado de la ejecución de una Máquina de Turing"""
    
    def __init__(self, accepted: bool, ids: List[str], message: str, 
                 stats: Dict, final_tape: str):
        self.accepted = accepted
        self.ids = ids
        self.message = message
        self.stats = stats
        self.final_tape = final_tape


class TuringExecutor:
    """Motor de ejecución de Máquinas de Turing"""
    
    def __init__(self, machine: TuringMachine, max_steps: int = 10000):
        """
        Inicializa el ejecutor
        
        Args:
            machine: Máquina de Turing a ejecutar
            max_steps: Número máximo de pasos antes de detenerse
        """
        self.machine = machine
        self.max_steps = max_steps
    
    def execute(self, input_string: str) -> ExecutionResult:
        """
        Ejecuta la máquina de Turing con una cadena de entrada
        
        Args:
            input_string: Cadena de entrada
            
        Returns:
            ExecutionResult con los resultados de la ejecución
        """
        start_time = time.time()
        
        # Inicializar cinta y estado
        tape = list(input_string) if input_string else [self.machine.blank]
        head = 0
        state = self.machine.initial_state
        mem_cache = ''
        steps = 0
        
        # Estadísticas
        max_tape_size = len(tape)
        states_visited = {state: 1}
        transitions_used = set()
        
        # Descripciones instantáneas
        ids = [self._format_id(tape, head, state, mem_cache)]
        
        # Bucle principal de ejecución
        while steps < self.max_steps:
            # Expandir cinta si es necesario
            head, tape = self._ensure_tape_bounds(head, tape)
            
            current_symbol = tape[head] if tape[head] else self.machine.blank
            
            # Buscar transición
            transition = self.machine.get_transition(state, mem_cache, current_symbol)
            
            if transition is None:
                # No hay transición - verificar si es estado final
                return self._create_result(
                    accepted=self.machine.is_final_state(state),
                    ids=ids,
                    message=self._get_halt_message(state, current_symbol),
                    stats=self._build_stats(steps, start_time, max_tape_size, 
                                           states_visited, transitions_used, state),
                    tape=tape
                )
            
            # Aplicar transición
            new_state, new_mem, out_symbol, move = transition
            transitions_used.add((state, mem_cache, current_symbol))
            
            tape[head] = out_symbol if out_symbol else self.machine.blank
            state = new_state
            mem_cache = new_mem if new_mem else ''
            
            # Mover cabezal
            if move == 'R':
                head += 1
            elif move == 'L':
                head -= 1
            # 'S' -> stay
            
            # Actualizar estadísticas
            steps += 1
            max_tape_size = max(max_tape_size, len(tape))
            states_visited[state] = states_visited.get(state, 0) + 1
            ids.append(self._format_id(tape, head, state, mem_cache))
            
            # Verificar si alcanzamos estado final
            if self.machine.is_final_state(state):
                return self._create_result(
                    accepted=True,
                    ids=ids,
                    message="Estado final alcanzado",
                    stats=self._build_stats(steps, start_time, max_tape_size,
                                           states_visited, transitions_used, state),
                    tape=tape
                )
        
        # Límite de pasos excedido
        return self._create_result(
            accepted=False,
            ids=ids,
            message=f"Límite de {self.max_steps} pasos excedido (posible bucle infinito)",
            stats=self._build_stats(steps, start_time, max_tape_size,
                                   states_visited, transitions_used, state),
            tape=tape
        )
    
    def _ensure_tape_bounds(self, head: int, tape: List[str]) -> Tuple[int, List[str]]:
        """
        Asegura que el cabezal esté dentro de los límites de la cinta
        
        Args:
            head: Posición del cabezal
            tape: Cinta actual
            
        Returns:
            Tupla (nueva_posición, nueva_cinta)
        """
        if head < 0:
            tape.insert(0, self.machine.blank)
            head = 0
        elif head >= len(tape):
            tape.append(self.machine.blank)
        
        return head, tape
    
    def _format_id(self, tape: List[str], head: int, state: str, 
                   mem_cache: str) -> str:
        """
        Formatea una descripción instantánea (ID)
        
        Args:
            tape: Cinta actual
            head: Posición del cabezal
            state: Estado actual
            mem_cache: Valor de memoria caché
            
        Returns:
            String con la descripción instantánea
        """
        # Copiar y limpiar cinta (eliminar blanks al final)
        tape_copy = tape.copy()
        while len(tape_copy) > 1 and tape_copy[-1] == self.machine.blank:
            tape_copy.pop()
        
        # Construir partes de la ID
        left = ''.join(tape_copy[:head])
        current = tape_copy[head] if head < len(tape_copy) else self.machine.blank
        right = ''.join(tape_copy[head + 1:]) if head + 1 < len(tape_copy) else ''
        
        # Mostrar blank como símbolo especial
        if current == self.machine.blank:
            current = '␣'
        
        cache_str = f"[{mem_cache}]" if mem_cache else ""
        
        return f"{left}[{state}{cache_str}]{current}{right}"
    
    def _get_final_tape(self, tape: List[str]) -> str:
        """
        Obtiene el contenido final de la cinta (sin blanks al final)
        
        Args:
            tape: Cinta actual
            
        Returns:
            String con el contenido de la cinta
        """
        tape_copy = tape.copy()
        while len(tape_copy) > 1 and tape_copy[-1] == self.machine.blank:
            tape_copy.pop()
        return ''.join(tape_copy)
    
    def _get_halt_message(self, state: str, symbol: str) -> str:
        """Genera mensaje de parada"""
        if self.machine.is_final_state(state):
            return "Estado final alcanzado"
        return f"No hay transición desde estado '{state}' con símbolo '{symbol}'"
    
    def _build_stats(self, steps: int, start_time: float, max_tape_size: int,
                     states_visited: Dict, transitions_used: set, 
                     final_state: str) -> Dict:
        """Construye diccionario de estadísticas"""
        return {
            "steps": steps,
            "execution_time": time.time() - start_time,
            "max_tape_size": max_tape_size,
            "states_visited": dict(states_visited),
            "unique_transitions": len(transitions_used),
            "final_state": final_state
        }
    
    def _create_result(self, accepted: bool, ids: List[str], message: str,
                       stats: Dict, tape: List[str]) -> ExecutionResult:
        """Crea un objeto ExecutionResult"""
        return ExecutionResult(
            accepted=accepted,
            ids=ids,
            message=message,
            stats=stats,
            final_tape=self._get_final_tape(tape)
        )
