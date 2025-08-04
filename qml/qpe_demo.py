from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np

t_qubits = 1           
c_qubits = 3           
while True:
    try:
        phi = float(input("Enter a phase(between 0 and 1): "))
        if 0 <= phi < 1:
            break
        else:
            print("Please enter a value between 0 and 1.")
    except ValueError:
        print("Please enter a valid number.")
          
qc = QuantumCircuit(c_qubits + t_qubits, c_qubits)

qc.h(range(c_qubits))

qc.x(c_qubits) 

def controlled_unitary(qc, c_qubit, t_qubit, power):
    angle = 2 * np.pi * phi * (2 ** power)
    qc.cp(angle, c_qubit, t_qubit) 

for i in range(c_qubits):
    controlled_unitary(qc, i, c_qubits, c_qubits - i - 1)

def inverse_qft(qc, n):
    for j in range(n//2):
        qc.swap(j, n - j - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)

inverse_qft(qc, c_qubits)

qc.measure(range(c_qubits), range(c_qubits))

sim = AerSimulator()
result = sim.run(qc, shots=1024).result()
counts = result.get_counts()

plot_histogram(counts)
plt.title(f"Estimated phase for = {phi}")
plt.show()
