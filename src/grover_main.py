import streamlit as st
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import io

# --- Page Setup ---
st.set_page_config(page_title="Quantum Treasure Hunt", layout="centered")
st.title("Quantum Treasure Hunt")
st.caption("by Team Oracle - Uunchai '25")

with st.expander("What is Grover's Algorithm?"):
    st.markdown("""
    Grover's Algorithm helps us find the right answer faster than classical guessing.
    Instead of checking every PIN one by one (like a brute-force attacker), Grover’s Algorithm
    boosts the chance of measuring the correct one in just ~√N steps!
    """)

st.markdown("---")
st.subheader("Enter a secret 4-bit binary PIN to search")
pin = st.text_input("Example: 1010", max_chars=4)
show_amplitudes = st.checkbox("Show amplitude evolution")
run_button = st.button("Run Grover’s Algorithm")

# --- Amplitude Logger ---
def amplitudes_visualisation(statevector, label):
    st.markdown(f"**{label}**")
    amps = statevector.data
    n = statevector.num_qubits
    amp_table = {
        f"|{format(i, f'0{n}b')}⟩": f"{round(amp.real, 4)} + {round(amp.imag, 4)}i" if round(amp.imag, 4) != 0 else f"{round(amp.real, 4)}"
        for i, amp in enumerate(amps)
    }
    st.json(amp_table)

# --- Grover's Circuit ---
def build_grover_circuit(target):
    n = 4
    qc = QuantumCircuit(n, n)

    qc.h(range(n))
    if show_amplitudes:
        state = Statevector.from_instruction(qc)
        amplitudes_visualisation(state, "Step 1: After Superposition")

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
    if show_amplitudes:
        state = Statevector.from_instruction(qc)
        amplitudes_visualisation(state, "Step 2: After Oracle")

    diffuser(qc)
    if show_amplitudes:
        state = Statevector.from_instruction(qc)
        amplitudes_visualisation(state, "Step 3: After Diffusion")

    for _ in range(2):
        apply_oracle(qc, target)
        diffuser(qc)

    qc.measure(range(n), range(n))

    sim = AerSimulator()
    result = sim.run(qc, shots=1024).result()
    counts = result.get_counts()
    return counts

# --- Run + Plot ---
if run_button and pin:
    if len(pin) == 4 and set(pin).issubset({'0', '1'}):
        with st.spinner("Crunching qubits"):
            counts = build_grover_circuit(pin)
            st.success("Done! Here's your result:")
            fig = plot_histogram(counts)
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.image(buf, caption="🔬 Measurement Outcome", use_container_width=True)
            most_likely = max(counts, key=counts.get)
            st.markdown(f"**Most likely result: `{most_likely}`**")
    else:
        st.error("Please enter a valid 4-bit binary number (like 0110).")

st.markdown("---")
st.caption("Built with ❤️ using Qiskit + Streamlit")
