from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
import numpy as np


def amplitudes_visualisation(statevector):
    amplitudes = statevector.data
    n = statevector.num_qubits
    output = []
    for i, amp in enumerate(amplitudes):
        binary = format(i, f'0{n}b')
        real = round(amp.real, 4)
        imag = round(amp.imag, 4)
        amp_str = f"{real}" if imag == 0 else f"{real} + {imag}i"
        output.append((binary, amp_str))
    return output


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

    apply_oracle(qc, target)

    def diffuser(qc):
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        qc.x(range(n))
        qc.h(range(n))

    diffuser(qc)

    # Run extra Grover iterations if needed (usually 1 or 2 for 16 states)
    for _ in range(1):
        apply_oracle(qc, target)
        diffuser(qc)

    qc.measure(range(n), range(n))

    sim = AerSimulator()
    result = sim.run(qc, shots=1024).result()
    counts = result.get_counts()

    return counts
