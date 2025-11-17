"""
Turing Machine - Representación de la Máquina de Turing
"""
from typing import Dict, List, Tuple


class TuringMachine:
    """Representación de una Máquina de Turing"""
    
    def __init__(self, config: Dict):
        """
        Inicializa la máquina de Turing desde una configuración
        
        Args:
            config: Diccionario con la configuración validada
        """
        # Estados
        self.states: List[str] = config['q_states']['q_list']
        self.initial_state: str = config['q_states']['initial']
        
        final = config['q_states']['final']
        self.final_states: List[str] = [final] if isinstance(final, str) else final
        
        # Alfabetos
        self.alphabet: List[str] = config['alphabet']
        self.tape_alphabet: List[str] = config['tape_alphabet']
        self.blank: str = ''
        
        # Detectar símbolo blank en tape_alphabet
        for symbol in self.tape_alphabet:
            if symbol == '' or symbol is None:
                self.blank = ''
                break
        
        # Función de transición delta
        self.delta: Dict[Tuple[str, str, str], Tuple[str, str, str, str]] = {}
        self._build_transition_function(config['delta'])
        
        # Cadenas de simulación
        self.simulation_strings: List[str] = config.get('simulation_strings', [])
    
    def _build_transition_function(self, delta_config: List[Dict]):
        """
        Construye la función de transición delta
        
        Args:
            delta_config: Lista de transiciones de la configuración
        """
        for transition in delta_config:
            params = transition['params']
            output = transition['output']
            
            # Normalizar símbolos de cinta
            tape_in = self._normalize_symbol(params.get('tape_input'))
            tape_out = self._normalize_symbol(output.get('tape_output'))
            mem_cache = params.get('mem_cache_value', '') or ''
            
            # Crear entrada y salida de la transición
            key = (params['initial_state'], mem_cache, tape_in)
            value = (
                output['final_state'],
                output.get('mem_cache_value', '') or '',
                tape_out,
                output['tape_displacement']
            )
            
            self.delta[key] = value
    
    def _normalize_symbol(self, symbol) -> str:
        """
        Normaliza un símbolo de cinta (maneja None y strings vacíos)
        
        Args:
            symbol: Símbolo a normalizar
            
        Returns:
            Símbolo normalizado (blank si es None o '')
        """
        if symbol is None or symbol == '':
            return self.blank
        return symbol
    
    def get_transition(self, state: str, mem_cache: str, tape_symbol: str) -> Tuple:
        """
        Obtiene la transición para un estado, memoria y símbolo dados
        
        Args:
            state: Estado actual
            mem_cache: Valor de la memoria caché
            tape_symbol: Símbolo actual en la cinta
            
        Returns:
            Tupla (nuevo_estado, nueva_memoria, símbolo_salida, movimiento)
            o None si no existe transición
        """
        key = (state, mem_cache, tape_symbol)
        return self.delta.get(key)
    
    def is_final_state(self, state: str) -> bool:
        """
        Verifica si un estado es final
        
        Args:
            state: Estado a verificar
            
        Returns:
            True si es un estado final
        """
        return state in self.final_states
    
    def get_stats_summary(self) -> Dict:
        """
        Obtiene un resumen de estadísticas de la máquina
        
        Returns:
            Diccionario con estadísticas básicas
        """
        return {
            'num_states': len(self.states),
            'num_transitions': len(self.delta),
            'alphabet_size': len(self.alphabet),
            'tape_alphabet_size': len(self.tape_alphabet),
            'num_final_states': len(self.final_states),
            'num_simulation_strings': len(self.simulation_strings)
        }
