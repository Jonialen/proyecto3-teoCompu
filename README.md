# Turing Machine Simulator

This project is a Turing Machine simulator implemented in Python. It can load machine definitions from YAML files, validate them, and execute them on a given input tape.

## How to Use

1.  **Define a Turing Machine:** Create a YAML file that describes the Turing Machine. The file should include the initial state, final states, the blank symbol, and the transition function.

2.  **Run the Simulator:** Use the `main.py` script to run the simulator. You need to provide the path to the machine definition file and the input tape.

    ```bash
    python main.py <path_to_machine.yaml> <input_tape>
    ```

## Example: Binary Incrementer

The `mt_increment.yaml` file defines a Turing Machine that increments a binary number.

```yaml
initial_state: q0
final_states: [qf]
blank_symbol: 'B'

transitions:
  # Scan to the right end of the tape
  q0:
    '0': {write: '0', move: R, next_state: q0}
    '1': {write: '1', move: R, next_state: q0}
    'B': {write: 'B', move: L, next_state: q1}

  # Move left and flip the last digit
  q1:
    '0': {write: '1', move: L, next_state: qf}
    '1': {write: '0', move: L, next_state: q1}
    'B': {write: '1', move: L, next_state: qf}
```

### How it Works

1.  **`q0` (Scan Right):** The machine starts in state `q0` and moves right until it finds a blank symbol (`B`). This positions the head at the end of the input string.

2.  **`q1` (Increment):** The machine moves left, flipping `1`s to `0`s until it finds a `0`. It flips the `0` to a `1` and then halts (`qf`). If it reaches the beginning of the tape (finds a `B`), it writes a `1` and halts. This handles the case where the input is all `1`s (e.g., `111` -> `1000`).

### How to Run

```bash
python main.py mt_increment.yaml 1011
```

This will output the result of the simulation, which should be `1100`.

## Other Examples

*   **`mt_recognizer_anbn.yaml`:** This machine recognizes strings of the form `a^n b^n` (e.g., `aaabbb`).
*   **`mt_duplicator.yaml`:** This machine takes a string of `0`s and `1`s and duplicates it (e.g., `101` -> `101101`).
*   **`mt_palindrome.yaml`:** This machine recognizes palindromic strings of `0`s and `1`s (e.g., `101101`).
*   **`test_invalid.yaml`:** This is an example of an invalid machine definition, used for testing the validator.

## Transition Diagrams

To better understand the transitions of a Turing Machine, you can generate a state diagram. This project includes a script to convert a YAML machine definition into a `dot` file, which can then be used with [Graphviz](https://graphviz.org/) to generate an image.

### Generating a Diagram

1.  **Install Graphviz:** If you don't have it already, install Graphviz. On most Linux distributions, you can install it using your package manager:

    ```bash
    sudo apt-get install graphviz
    ```

2.  **Convert YAML to `dot`:** Use the `utils/yaml_to_dot.py` script to convert your machine definition to a `dot` file.

    ```bash
    python utils/yaml_to_dot.py <path_to_machine.yaml> <output.dot>
    ```

    For example, to generate a `dot` file for the `mt_increment.yaml` machine:

    ```bash
    python utils/yaml_to_dot.py mt_increment.yaml mt_increment.dot
    ```

3.  **Generate the Image:** Use the `dot` command to generate an image from the `.dot` file.

    ```bash
    dot -Tpng mt_increment.dot -o mt_increment.png
    ```

This will create a `mt_increment.png` file with the state diagram of the Turing Machine.

Here is an example of the generated diagram for `mt_increment.yaml`:

![Transition Diagram for mt_increment.yaml](https://i.imgur.com/your_diagram_url.png) 
**(Note: You will need to generate your own diagram and replace the URL)**
