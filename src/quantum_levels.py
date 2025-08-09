import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

def generate_target(rule):
    """Generates a random 4-bit binary string based on a clue rule."""
    pins = []

    if rule == "symmetric":
        for a in ['0', '1']:
            for b in ['0', '1']:
                pins.append(a + b + a + b)

    elif rule == "start_end_1":
        for b in ['0', '1']:
            for c in ['0', '1']:
                pins.append("1" + b + c + "1")

    elif rule == "half_half":
        pins = [p for p in [format(i, '04b') for i in range(16)] if p.count('1') == 2]

    elif rule == "one_one":
        pins = [p for p in [format(i, '04b') for i in range(16)] if p.count('1') == 1]

    elif rule == "alternating":
        pins = ["1010", "0101"]

    return random.choice(pins)

def build_grover_circuit(target):
    n = 4
    qc = QuantumCircuit(n, n)

    qc.h(range(n))

    def apply_oracle(qc, target):
        for i, bit in enumerate(reversed(target)):
            if bit == '0':
                qc.x(i)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        for i, bit in enumerate(reversed(target)):
            if bit == '0':
                qc.x(i)

    def diffuser(qc):
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        qc.x(range(n))
        qc.h(range(n))

    apply_oracle(qc, target)
    diffuser(qc)

    for _ in range(1):
        apply_oracle(qc, target)
        diffuser(qc)

    qc.measure(range(n), range(n))

    sim = AerSimulator()
    result = sim.run(qc, shots=1024).result()
    counts = result.get_counts()
    return counts
