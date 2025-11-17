#!/usr/bin/env python3
import yaml
import sys
import re
import time
from typing import List, Dict, Optional, Tuple

# ====== COLORES ANSI PARA TERMINAL ======
RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"


def ok(msg: str) -> str:
    return f"{GREEN}{msg}{RESET}"


def err(msg: str) -> str:
    return f"{RED}{msg}{RESET}"


def warn(msg: str) -> str:
    return f"{YELLOW}{msg}{RESET}"


def info(msg: str) -> str:
    return f"{CYAN}{msg}{RESET}"


def title(msg: str) -> str:
    return f"{BOLD}{BLUE}{msg}{RESET}"


def make_writer(output_file: Optional[str]):
    """
    Devuelve una función write(text) que escribe con colores en consola.
    No escribe directamente en archivo: el guardado en archivo (sin colores)
    se maneja al final de run_all_simulations usando plain_lines.
    """
    def write_console(text: str = ""):
        print(text)
    return write_console


ANSI_RE = re.compile(r"\033\[[0-9;]*m")


class TuringMachineValidator:
    """Valida la configuración de la Máquina de Turing"""

    @staticmethod
    def validate_config(config: dict) -> List[str]:
        errors: List[str] = []

        # Validar estructura base
        required_keys = ['q_states', 'alphabet', 'tape_alphabet', 'delta']
        for key in required_keys:
            if key not in config:
                errors.append(err(f"Falta la clave requerida: '{key}'"))

        if errors:
            return errors

        # Validar estados
        if 'q_list' not in config['q_states']:
            errors.append(err("Falta 'q_list' en q_states"))
        if 'initial' not in config['q_states']:
            errors.append(err("Falta 'initial' en q_states"))
        if 'final' not in config['q_states']:
            errors.append(err("Falta 'final' en q_states"))

        if not errors:
            states = config['q_states']['q_list']
            initial = config['q_states']['initial']
            final = config['q_states']['final']

            if initial not in states:
                errors.append(err(f"Estado inicial '{initial}' no está en q_list"))

            final_states = [final] if isinstance(final, str) else final
            for f in final_states:
                if f not in states:
                    errors.append(err(f"Estado final '{f}' no está en q_list"))

            if len(states) != len(set(states)):
                errors.append(err("Hay estados duplicados en q_list"))

        # Validar alfabetos
        alphabet = config.get('alphabet', [])
        tape_alphabet = config.get('tape_alphabet', [])

        if not alphabet:
            errors.append(err("El alfabeto de entrada está vacío"))

        if not tape_alphabet:
            errors.append(err("El alfabeto de cinta está vacío"))

        for symbol in alphabet:
            if symbol and symbol not in tape_alphabet:
                errors.append(err(f"Símbolo '{symbol}' del alfabeto no está en tape_alphabet"))

        # Validar transiciones
        delta = config.get('delta', [])
        if not delta:
            errors.append(warn("No hay transiciones definidas (delta vacío)"))

        for i, transition in enumerate(delta):
            if 'params' not in transition:
                errors.append(err(f"Transición {i}: falta 'params'"))
                continue
            if 'output' not in transition:
                errors.append(err(f"Transición {i}: falta 'output'"))
                continue

            params = transition['params']
            output = transition['output']

            if 'initial_state' not in params:
                errors.append(err(f"Transición {i}: falta 'initial_state'"))
            elif params['initial_state'] not in states:
                errors.append(err(f"Transición {i}: estado '{params['initial_state']}' no existe"))

            if 'final_state' not in output:
                errors.append(err(f"Transición {i}: falta 'final_state'"))
            elif output['final_state'] not in states:
                errors.append(err(f"Transición {i}: estado '{output['final_state']}' no existe"))

            if 'tape_displacement' not in output:
                errors.append(err(f"Transición {i}: falta 'tape_displacement'"))
            elif output['tape_displacement'] not in ['L', 'R', 'S']:
                errors.append(err(f"Transición {i}: movimiento '{output['tape_displacement']}' inválido"))

        # Validar cadenas de simulación
        if 'simulation_strings' in config:
            for i, string in enumerate(config['simulation_strings']):
                for char in string:
                    if char not in alphabet:
                        errors.append(warn(
                            f"Cadena {i} ('{string}'): contiene símbolo '{char}' no definido"
                        ))
                        break

        return errors


class TuringMachine:
    """Simulador de Máquina de Turing"""

    def __init__(self, config_file: str):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.validation_errors = TuringMachineValidator.validate_config(config)
        if self.validation_errors:
            raise ValueError("Errores de validación encontrados")

        self.states = config['q_states']['q_list']
        self.initial_state = config['q_states']['initial']
        final = config['q_states']['final']
        self.final_states = [final] if isinstance(final, str) else final

        self.alphabet = config['alphabet']
        self.tape_alphabet = config['tape_alphabet']
        self.blank = ''

        # detectar blank en tape_alphabet ('' o None)
        for s in self.tape_alphabet:
            if s == '' or s is None:
                self.blank = ''
                break

        self.delta: Dict[Tuple[str, str, str], Tuple[str, str, str, str]] = {}
        for transition in config['delta']:
            params = transition['params']
            output = transition['output']

            tape_in = params.get('tape_input', '') if params.get('tape_input', '') != None else self.blank
            tape_in = tape_in if tape_in else self.blank
            tape_out = output.get('tape_output', '') if output.get('tape_output', '') != None else self.blank
            tape_out = tape_out if tape_out else self.blank
            mem_cache = params.get('mem_cache_value', '') or ''

            key = (params['initial_state'], mem_cache, tape_in)
            value = (
                output['final_state'],
                output.get('mem_cache_value', '') or '',
                tape_out,
                output['tape_displacement'],
            )
            self.delta[key] = value

        self.simulation_strings = config.get('simulation_strings', [])

    # -----------------------------------------------------------
    # FORMATEO DE ID
    # -----------------------------------------------------------
    def _format_id(self, tape: List[str], head: int, state: str, mem_cache: str) -> str:
        tape_copy = tape.copy()
        while len(tape_copy) > 1 and tape_copy[-1] == self.blank:
            tape_copy.pop()

        left = ''.join(tape_copy[:head])
        current = tape_copy[head] if head < len(tape_copy) else self.blank
        right = ''.join(tape_copy[head + 1:]) if head + 1 < len(tape_copy) else ''

        if current == self.blank:
            current = '␣'

        cache_str = f"[{mem_cache}]" if mem_cache else ""

        return f"{left}[{state}{cache_str}]{current}{right}"

    # -----------------------------------------------------------
    # OBTENER CINTA FINAL
    # -----------------------------------------------------------
    def _get_final_tape(self, tape: List[str]) -> str:
        tape_copy = tape.copy()
        while len(tape_copy) > 1 and tape_copy[-1] == self.blank:
            tape_copy.pop()
        return ''.join(tape_copy)

    # -----------------------------------------------------------
    # SIMULAR
    # -----------------------------------------------------------
    def simulate(self, input_string: str, max_steps: int = 10000) -> Tuple[bool, List[str], str, Dict, str]:
        start = time.time()
        tape = list(input_string) if input_string else [self.blank]
        head = 0
        state = self.initial_state
        mem_cache = ''
        steps = 0
        ids: List[str] = []

        max_size = len(tape)
        visited = {state: 1}
        used_trans = set()

        ids.append(self._format_id(tape, head, state, mem_cache))

        while steps < max_steps:
            if head < 0:
                tape.insert(0, self.blank)
                head = 0
            elif head >= len(tape):
                tape.append(self.blank)

            current_symbol = tape[head] if tape[head] else self.blank
            key = (state, mem_cache, current_symbol)

            if key not in self.delta:
                accepted = state in self.final_states
                msg = (
                    "Estado final alcanzado"
                    if accepted
                    else f"No hay transición desde estado '{state}' con símbolo '{current_symbol}'"
                )

                stats = {
                    "steps": steps,
                    "execution_time": time.time() - start,
                    "max_tape_size": max_size,
                    "states_visited": dict(visited),
                    "unique_transitions": len(used_trans),
                    "final_state": state,
                }

                return accepted, ids, msg, stats, self._get_final_tape(tape)

            new_state, new_mem, out_symbol, move = self.delta[key]
            used_trans.add(key)

            tape[head] = out_symbol if out_symbol else self.blank

            state = new_state
            mem_cache = new_mem if new_mem else ''
            visited[state] = visited.get(state, 0) + 1

            if move == 'R':
                head += 1
            elif move == 'L':
                head -= 1
            # 'S' -> stay

            steps += 1
            max_size = max(max_size, len(tape))
            ids.append(self._format_id(tape, head, state, mem_cache))

            if state in self.final_states:
                stats = {
                    "steps": steps,
                    "execution_time": time.time() - start,
                    "max_tape_size": max_size,
                    "states_visited": dict(visited),
                    "unique_transitions": len(used_trans),
                    "final_state": state,
                }
                return True, ids, "Estado final alcanzado", stats, self._get_final_tape(tape)

        stats = {
            "steps": steps,
            "execution_time": time.time() - start,
            "max_tape_size": max_size,
            "states_visited": dict(visited),
            "unique_transitions": len(used_trans),
            "final_state": state,
        }

        return False, ids, f"Límite de {max_steps} pasos excedido (posible bucle infinito)", stats, self._get_final_tape(tape)

    # -----------------------------------------------------------
    # EJECUTAR TODAS LAS CADENAS
    # -----------------------------------------------------------
    def run_all_simulations(self, output_file: Optional[str] = None, verbose: bool = True,
                            max_ids_display: Optional[int] = None):
        """
        Ejecuta todas las simulaciones definidas en el archivo.
        - En consola: imprime con colores.
        - Si se especifica output_file: guarda un reporte sin colores ANSI.
        """
        # writer para consola (siempre imprime en consola con colores)
        write_console = make_writer(output_file)

        # coleccionamos plain_lines (sin ANSI) para escribir en archivo al final
        plain_lines: List[str] = []

        def write_both(text: str = ""):
            # Escribe en consola (con colores)
            write_console(text)
            # Guarda versión sin ANSI para archivo
            plain_lines.append(ANSI_RE.sub("", text))

        write_both(title("=" * 70))
        write_both(title("SIMULADOR DE MÁQUINA DE TURING"))
        write_both(title("=" * 70))
        write_both(f"\nEstados: {', '.join(self.states)}")
        write_both(f"Estado inicial: {self.initial_state}")
        write_both(f"Estados finales: {', '.join(self.final_states)}")
        write_both(f"Alfabeto: {{{', '.join(self.alphabet)}}}")
        write_both(f"Alfabeto de cinta: {{{', '.join([s if s else '␣' for s in self.tape_alphabet])}}}")
        write_both(f"\nNúmero de transiciones: {len(self.delta)}")
        write_both(title("=" * 70))

        all_stats = []

        for i, input_string in enumerate(self.simulation_strings, 1):
            write_both(title("\n" + "=" * 70))
            write_both(title(f"SIMULACIÓN {i}: \"{input_string}\""))
            write_both(title("=" * 70))

            accepted, ids, msg, stats, final_tape = self.simulate(input_string)

            all_stats.append({
                "string": input_string,
                "accepted": accepted,
                "stats": stats,
                "final_tape": final_tape
            })

            write_both(f"\nDescripciones Instantáneas ({len(ids)} pasos):")
            write_both("-" * 70)

            # Mostrar IDs (compacto / limitado / completo)
            if not verbose:
                write_both(f"  0: {ids[0]}")
                if len(ids) > 1:
                    write_both("  ...")
                    write_both(f"  {len(ids)-1}: {ids[-1]}")
            elif max_ids_display and len(ids) > max_ids_display:
                half = max_ids_display // 2
                for j in range(half):
                    write_both(f"  {j}: {ids[j]}")
                write_both(f"  ... ({len(ids)-max_ids_display} pasos omitidos) ...")
                for j in range(len(ids)-half, len(ids)):
                    write_both(f"  {j}: {ids[j]}")
            else:
                for j, id_str in enumerate(ids):
                    write_both(f"  {j}: {id_str}")

            write_both("-" * 70)

            # =====================================
            # CINTA FINAL
            # =====================================
            write_both(info("\nCINTA FINAL:"))
            write_both(f"   Entrada: \"{input_string}\"")
            write_both(f"   Salida:  \"{final_tape}\"")

            if final_tape != input_string:
                write_both(warn("   La cinta fue modificada"))
            else:
                write_both(info("   La cinta no fue modificada"))

            # =====================================
            # ESTADÍSTICAS
            # =====================================
            write_both(info("\nESTADÍSTICAS:"))
            write_both(f"   Pasos ejecutados: {stats['steps']}")
            write_both(f"   Tiempo de ejecución: {stats['execution_time']:.6f} s")
            write_both(f"   Tamaño máximo de cinta: {stats['max_tape_size']} celdas")
            write_both(f"   Transiciones únicas usadas: {stats['unique_transitions']}/{len(self.delta)}")
            write_both(f"   Estado final: {stats['final_state']}")

            sorted_states = sorted(stats['states_visited'].items(), key=lambda x: x[1], reverse=True)
            write_both("   Estados más visitados:")
            for st, count in sorted_states[:3]:
                write_both(f"     - {st}: {count} veces")

            write_both(info("\nMensaje: " + msg))

            if accepted:
                write_both(ok("RESULTADO: CADENA ACEPTADA"))
            else:
                write_both(err("RESULTADO: CADENA RECHAZADA"))

            write_both(title("=" * 70))

        # ============================================
        # Resumen global
        # ============================================
        if len(all_stats) > 1:
            write_both(title("\n" + "=" * 70))
            write_both(title("RESUMEN COMPARATIVO"))
            write_both(title("=" * 70))

            write_both(f"\n{'Entrada':<15} {'Salida':<15} {'Resultado':<12} {'Pasos':<8} {'Tiempo (s)':<12}")
            write_both("-" * 70)

            for item in all_stats:
                result_label = "ACEPTADA" if item['accepted'] else "RECHAZADA"
                # result colored only in console (we write plain result into plain_lines)
                colored_result = ok(result_label) if item['accepted'] else err(result_label)
                entrada = item['string'][:12] + "..." if len(item['string']) > 15 else item['string']
                salida = item['final_tape'][:12] + "..." if len(item['final_tape']) > 15 else item['final_tape']

                # When writing the table line, include the colored result for console,
                # plain_lines will store the ANSI-stripped version.
                write_both(f"{entrada:<15} {salida:<15} {colored_result:<12} {item['stats']['steps']:<8} "
                           f"{item['stats']['execution_time']:<12.6f}")

            write_both("-" * 70)

            total_steps = sum(s['stats']['steps'] for s in all_stats)
            total_time = sum(s['stats']['execution_time'] for s in all_stats)
            accepted_count = sum(1 for s in all_stats if s['accepted'])

            write_both(info("\nESTADÍSTICAS GLOBALES:"))
            write_both(f"   Total simulaciones: {len(all_stats)}")
            write_both(f"   Cadenas aceptadas: {accepted_count}/{len(all_stats)}")
            write_both(f"   Cadenas rechazadas: {len(all_stats)-accepted_count}/{len(all_stats)}")
            write_both(f"   Pasos totales: {total_steps}")
            write_both(f"   Tiempo total: {total_time:.6f} s")
            write_both(f"   Promedio pasos/cadena: {total_steps/len(all_stats):.2f}")
            write_both(f"   Promedio tiempo/cadena: {total_time/len(all_stats):.6f} s")
            write_both(title("=" * 70))

        # Guardar en archivo sin ANSI si se solicitó
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(plain_lines))
                # Print confirmation in console (colored)
                print(ok(f"Reporte guardado en {output_file}"))
            except Exception as e:
                print(err(f"Error al guardar el archivo: {e}"))


# =============================================================
# MAIN
# =============================================================
def main():
    if len(sys.argv) < 2:
        print(title("=" * 70))
        print(title("SIMULADOR DE MÁQUINA DE TURING"))
        print(title("=" * 70))
        print("\nUso:")
        print("  python turing_simulator.py <archivo_yaml> [opciones]")
        print("\nOpciones:")
        print("  -o, --output <archivo>     Guardar reporte en archivo (sin colores)")
        print("  -c, --compact              Modo compacto (solo inicio y fin)")
        print("  -l, --limit <n>            Mostrar máximo n IDs")
        sys.exit(1)

    config_file = sys.argv[1]
    output_file: Optional[str] = None
    verbose = True
    max_ids_display: Optional[int] = None

    # Parseo de argumentos simple
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                print(err("-o/--output requiere un nombre de archivo"))
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
                    print(err("--limit requiere un número entero"))
                    sys.exit(1)
            else:
                print(err("--limit requiere un número"))
                sys.exit(1)
        else:
            print(err(f"Argumento desconocido: {arg}"))
            sys.exit(1)

    # Validación inicial (solo consola)
    print(info("Validando configuración..."))
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        errors = TuringMachineValidator.validate_config(config)

        if errors:
            print(err("\nERRORES DE VALIDACIÓN ENCONTRADOS:"))
            for e in errors:
                # e may already contain color codes from validator; print directly
                print(" -", e)
            sys.exit(1)

        print(ok("Configuración válida\n"))

        tm = TuringMachine(config_file)
        tm.run_all_simulations(output_file=output_file, verbose=verbose, max_ids_display=max_ids_display)

    except FileNotFoundError:
        print(err(f"No se encontró el archivo '{config_file}'"))
        sys.exit(1)
    except yaml.YAMLError as e:
        print(err("Error al parsear YAML"))
        print(e)
        sys.exit(1)
    except ValueError:
        # errores de validación ya mostrados
        sys.exit(1)
    except Exception as e:
        print(err("Error inesperado:"))
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()

