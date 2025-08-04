from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def amplitudes_visualisation(statevector, label):
    print(f"\n {label}")
    amplitudes = statevector.data
    n = statevector.num_qubits
    for i, amp in enumerate(amplitudes):
        binary = format(i, f'0{n}b')
        real = round(amp.real, 4)
        imag = round(amp.imag, 4)
        amp_str = f"{real}" if imag == 0 else f"{real} + {imag}i"
        print(f"|{binary}⟩: {amp_str}")

def build_grover_circuit(target):
    n = 4                               #number of qubits
    qc = QuantumCircuit(n, n)

    qc.h(range(n))
    state = Statevector.from_instruction(qc)
    amplitudes_visualisation(state, "After Superposition")

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
    state = Statevector.from_instruction(qc)
    amplitudes_visualisation(state, "After Oracle (marked state phase-flipped)")

    def diffuser(qc):
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        qc.x(range(n))
        qc.h(range(n))
    
    diffuser(qc)
    state = Statevector.from_instruction(qc)
    amplitudes_visualisation(state, "After Diffusion (marked state amplified)")

    for _ in range(2):
        apply_oracle(qc, target)
        diffuser(qc)

    qc.measure(range(n), range(n))

    sim = AerSimulator()
    result = sim.run(qc, shots=1024).result()
    counts = result.get_counts()

    plot_histogram(counts)
    plt.show()

    return counts


if __name__ == "__main__":
    target = input("Enter the 4-bit PIN to search (in binary form): ")
    build_grover_circuit(target)


