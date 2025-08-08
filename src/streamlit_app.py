import streamlit as st
import json
from quantum_levels import build_grover_circuit

# Load level data
with open("assets/level_clues.json", "r") as f:
    levels = json.load(f)

st.set_page_config(page_title="Quantum Treasure Hunt", layout="centered")
st.title("Quantum Treasure Hunt")

st.markdown("Solve each level by figuring out the correct 4-bit PIN using clues and Grover's Algorithm!")

# Choose level
level_options = [f"Level {lvl['level']}" for lvl in levels]
selected = st.selectbox("Choose your level", level_options)
current_level = next(lvl for lvl in levels if f"Level {lvl['level']}" == selected)

# Show clue
st.markdown(f"###Clue: {current_level['clue']}")

# User's guess
user_guess = st.text_input("Enter your 4-bit guess (e.g., 0110):")

# Validate guess
if st.button(" Run Grover’s Algorithm"):

    if not user_guess or len(user_guess) != 4 or any(c not in '01' for c in user_guess):
        st.error("Please enter a valid 4-bit binary string (like 0110).")
    else:
        with st.spinner("Running quantum circuit..."):
            result = build_grover_circuit(current_level["target"])

        st.success("Quantum Simulation Complete!")
        st.bar_chart(result)

        most_probable = max(result, key=result.get)

        if user_guess == most_probable:
            st.balloons()
            st.success(f"Correct! Your guess `{user_guess}` matches the quantum result!")
        else:
            st.warning(f"Oops! Your guess was `{user_guess}` but Grover found `{most_probable}`.")
