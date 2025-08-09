import streamlit as st
import json
from qiskit_aer import AerSimulator
from quantum_levels import generate_target, build_grover_circuit
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
import io
from quantum_levels import generate_target, build_grover_circuit


st.set_page_config(page_title="Quantum Treasure Hunt", layout="centered")
st.title("Quantum Treasure Hunt")
st.caption("by Team Oracle – Uunchai '25")

with st.expander("What is Grover's Algorithm?"):
    st.markdown("""
    Imagine you’re looking for a treasure in **1 out of N boxes**.  
    - **Classically**: You check each box one by one → takes about `N/2` tries.  
    - **Grover’s Algorithm**: Uses quantum superposition & interference → finds the right box in only about `√N` tries**!  
    
    Here, our *treasure* is a secret 4-bit PIN (like `0110`).  
    Grover’s algorithm *amplifies* the probability of the correct PIN so it shows up most often when we measure.
    """)

with open("assets/level_clues.json", "r") as f:
    levels = json.load(f)

level_options = [f"Level {lvl['level']}" for lvl in levels]
selected_level_str = st.selectbox("Choose your level", level_options)
current_level = next(lvl for lvl in levels if f"Level {lvl['level']}" == selected_level_str)

target_pin = generate_target(current_level["rule"])

st.markdown(f"### Clue: {current_level['clue']}")

user_guess = st.text_input("Enter your 4-bit guess (e.g., 0110):", max_chars=4)
show_amplitudes = st.checkbox("Show amplitude evolution (for the quantum nerds)")

def amplitudes_visualisation(statevector, label):
    st.markdown(f"**{label}**")
    amps = statevector.data
    n = statevector.num_qubits
    amp_table = {
        f"|{format(i, f'0{n}b')}⟩": f"{round(amp.real, 4)} + {round(amp.imag, 4)}i"
        if round(amp.imag, 4) != 0 else f"{round(amp.real, 4)}"
        for i, amp in enumerate(amps)
    }
    st.json(amp_table)

def build_grover_circuit_verbose(target, show_amps=False):
    from qiskit import QuantumCircuit
    n = 4
    qc = QuantumCircuit(n, n)

    qc.h(range(n))
    if show_amps:
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
    if show_amps:
        state = Statevector.from_instruction(qc)
        amplitudes_visualisation(state, "Step 2: After Oracle")

    diffuser(qc)
    if show_amps:
        state = Statevector.from_instruction(qc)
        amplitudes_visualisation(state, "Step 3: After Diffusion")

    # One more Grover iteration
    apply_oracle(qc, target)
    diffuser(qc)

    qc.measure(range(n), range(n))

    return qc

if st.button("Run Grover’s Algorithm"):
    if not user_guess or len(user_guess) != 4 or any(c not in '01' for c in user_guess):
        st.error("Please enter a valid 4-bit binary string (like 0110).")
    else:
        with st.spinner("Running quantum circuit..."):
            qc = build_grover_circuit_verbose(target_pin, show_amps=show_amplitudes)
            sim = AerSimulator()
            result = sim.run(qc, shots=1024).result().get_counts()

        st.success("Quantum Simulation Complete!")

        fig = plot_histogram(result)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.image(buf, caption="Measurement Outcome", use_container_width=True)

        most_probable = max(result, key=result.get)

        if user_guess == most_probable:
            st.balloons()
            st.success(f"Correct! Your guess `{user_guess}` matches the quantum result!")
        else:
            st.warning(f"Oops! Your guess was `{user_guess}` but Grover found `{most_probable}`.")

        with st.expander("How to interpret this result"):
            st.markdown("""
            The taller the bar in the chart, the higher the probability of measuring that PIN.  
            Grover’s Algorithm *amplifies* the correct answer so it becomes the tallest bar,  
            meaning it's the one you'll most likely measure!
            """)

st.markdown("---")
st.caption("Built with ❤️ using Qiskit + Streamlit | Team Oracle")
