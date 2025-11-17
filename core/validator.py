"""
Validator - Validación de configuración de Máquina de Turing
"""
from typing import List, Dict
from utils.output import ColorOutput as out


class TuringMachineValidator:
    """Validador de configuración de Máquina de Turing"""
    
    @staticmethod
    def validate(config: Dict) -> List[str]:
        """
        Valida la configuración de una Máquina de Turing
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            Lista de errores encontrados (vacía si es válida)
        """
        errors: List[str] = []
        
        # Validar estructura base
        errors.extend(TuringMachineValidator._validate_structure(config))
        
        if errors:
            return errors
        
        # Validar estados
        errors.extend(TuringMachineValidator._validate_states(config))
        
        # Validar alfabetos
        errors.extend(TuringMachineValidator._validate_alphabets(config))
        
        # Validar transiciones
        errors.extend(TuringMachineValidator._validate_transitions(config))
        
        # Validar cadenas de simulación
        errors.extend(TuringMachineValidator._validate_simulation_strings(config))
        
        return errors
    
    @staticmethod
    def _validate_structure(config: Dict) -> List[str]:
        """Valida la estructura base de la configuración"""
        errors = []
        required_keys = ['q_states', 'alphabet', 'tape_alphabet', 'delta']
        
        for key in required_keys:
            if key not in config:
                errors.append(out.error(f"Falta la clave requerida: '{key}'"))
        
        return errors
    
    @staticmethod
    def _validate_states(config: Dict) -> List[str]:
        """Valida la configuración de estados"""
        errors = []
        
        if 'q_list' not in config['q_states']:
            errors.append(out.error("Falta 'q_list' en q_states"))
        if 'initial' not in config['q_states']:
            errors.append(out.error("Falta 'initial' en q_states"))
        if 'final' not in config['q_states']:
            errors.append(out.error("Falta 'final' en q_states"))
        
        if errors:
            return errors
        
        states = config['q_states']['q_list']
        initial = config['q_states']['initial']
        final = config['q_states']['final']
        
        # Validar estado inicial
        if initial not in states:
            errors.append(out.error(f"Estado inicial '{initial}' no está en q_list"))
        
        # Validar estados finales
        final_states = [final] if isinstance(final, str) else final
        for f in final_states:
            if f not in states:
                errors.append(out.error(f"Estado final '{f}' no está en q_list"))
        
        # Validar estados únicos
        if len(states) != len(set(states)):
            errors.append(out.error("Hay estados duplicados en q_list"))
        
        return errors
    
    @staticmethod
    def _validate_alphabets(config: Dict) -> List[str]:
        """Valida los alfabetos de entrada y cinta"""
        errors = []
        
        alphabet = config.get('alphabet', [])
        tape_alphabet = config.get('tape_alphabet', [])
        
        if not alphabet:
            errors.append(out.error("El alfabeto de entrada está vacío"))
        
        if not tape_alphabet:
            errors.append(out.error("El alfabeto de cinta está vacío"))
        
        # Validar que el alfabeto de entrada esté contenido en el de cinta
        for symbol in alphabet:
            if symbol and symbol not in tape_alphabet:
                errors.append(out.error(
                    f"Símbolo '{symbol}' del alfabeto no está en tape_alphabet"
                ))
        
        return errors
    
    @staticmethod
    def _validate_transitions(config: Dict) -> List[str]:
        """Valida las transiciones (función delta)"""
        errors = []
        
        delta = config.get('delta', [])
        if not delta:
            errors.append(out.warn("No hay transiciones definidas (delta vacío)"))
            return errors
        
        states = config['q_states']['q_list']
        
        for i, transition in enumerate(delta):
            if 'params' not in transition:
                errors.append(out.error(f"Transición {i}: falta 'params'"))
                continue
            if 'output' not in transition:
                errors.append(out.error(f"Transición {i}: falta 'output'"))
                continue
            
            params = transition['params']
            output = transition['output']
            
            # Validar estado inicial de la transición
            if 'initial_state' not in params:
                errors.append(out.error(f"Transición {i}: falta 'initial_state'"))
            elif params['initial_state'] not in states:
                errors.append(out.error(
                    f"Transición {i}: estado '{params['initial_state']}' no existe"
                ))
            
            # Validar estado final de la transición
            if 'final_state' not in output:
                errors.append(out.error(f"Transición {i}: falta 'final_state'"))
            elif output['final_state'] not in states:
                errors.append(out.error(
                    f"Transición {i}: estado '{output['final_state']}' no existe"
                ))
            
            # Validar movimiento de cinta
            if 'tape_displacement' not in output:
                errors.append(out.error(f"Transición {i}: falta 'tape_displacement'"))
            elif output['tape_displacement'] not in ['L', 'R', 'S']:
                errors.append(out.error(
                    f"Transición {i}: movimiento '{output['tape_displacement']}' inválido"
                ))
        
        return errors
    
    @staticmethod
    def _validate_simulation_strings(config: Dict) -> List[str]:
        """Valida las cadenas de simulación"""
        errors = []
        
        if 'simulation_strings' not in config:
            return errors
        
        alphabet = config.get('alphabet', [])
        
        for i, string in enumerate(config['simulation_strings']):
            for char in string:
                if char not in alphabet:
                    errors.append(out.warn(
                        f"Cadena {i} ('{string}'): contiene símbolo '{char}' no definido"
                    ))
                    break
        
        return errors