import yaml
import sys

def yaml_to_dot(yaml_file, dot_file):
    with open(yaml_file, 'r') as f:
        machine = yaml.safe_load(f)

    with open(dot_file, 'w') as f:
        f.write('digraph G {\n')
        f.write('  rankdir=LR;\n')
        f.write('  node [shape = circle];\n')

        # Mark final states
        for final_state in machine.get('final_states', []):
            f.write(f'  {final_state} [shape = doublecircle];\n')

        # Add transitions
        for state, transitions in machine.get('transitions', {}).items():
            for symbol, transition in transitions.items():
                if isinstance(transition, dict):
                    next_state = transition.get('next_state')
                    write = transition.get('write', symbol)
                    move = transition.get('move', 'R')
                    label = f'{symbol}/{write},{move}'
                    f.write(f'  {state} -> {next_state} [label="{label}"];\n')

        f.write('}\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python yaml_to_dot.py <input.yaml> <output.dot>")
        sys.exit(1)

    yaml_to_dot(sys.argv[1], sys.argv[2])
