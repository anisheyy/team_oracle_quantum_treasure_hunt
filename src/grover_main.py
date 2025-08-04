from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

n = 4 
target = input("Enter the 4-digit PIN to search(in Binary form)):")

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

for _ in range(2):
    apply_oracle(qc, target)
    diffuser(qc)


qc.measure(range(n), range(n))


sim = AerSimulator()
result = sim.run(qc, shots=1024).result()
counts = result.get_counts()

plot_histogram(counts)
plt.show()
