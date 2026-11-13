import streamlit as st
import time

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

st.title("AI Escape Room 🔐")
# Store the time when the player escapes
if "end_time" not in st.session_state:
    st.session_state.end_time = None

# Calculate elapsed time
if st.session_state.end_time is None:
    elapsed_time = int(time.time() - st.session_state.start_time)
else:
    elapsed_time = int(
        st.session_state.end_time - st.session_state.start_time
    )

# Display game timer
st.write(f"⏱️ Time Elapsed: {elapsed_time} seconds")
st.write("Welcome to the Mystery Room!")
st.write("Solve both puzzles to escape!")

# Store puzzle progress
if "puzzle1_solved" not in st.session_state:
    st.session_state.puzzle1_solved = False

if "puzzle2_solved" not in st.session_state:
    st.session_state.puzzle2_solved = False

# Calculate progress
completed = 0

if st.session_state.puzzle1_solved:
    completed += 1

if st.session_state.puzzle2_solved:
    completed += 1

progress = completed / 2

st.write("### Your Escape Progress")
st.progress(progress)
st.write(f"{int(progress * 100)}% completed")

st.divider()

# Puzzle 1
st.subheader("🧩 Puzzle 1: The Secret Number")

st.write(
    "I am a three-digit number. "
    "My digits add up to 9. "
    "My first digit is 2, my second digit is 3. "
    "What number am I?"
)

answer1 = st.text_input(
    "Enter the secret number:",
    disabled=st.session_state.puzzle1_solved
)

if not st.session_state.puzzle1_solved:
    if st.button("Unlock First Door"):
        if answer1.strip() == "234":
            st.session_state.puzzle1_solved = True
            st.rerun()
        else:
            st.error("Wrong answer! Try again.")
else:
    st.success("First door unlocked!")

# Puzzle 2
if st.session_state.puzzle1_solved:

    st.divider()
    st.subheader("🧩 Puzzle 2: The Secret Word")

    st.write(
        "I have keys but no locks. "
        "I have space but no room. "
        "You can enter, but cannot go outside. "
        "What am I?"
    )

    answer2 = st.text_input(
        "Enter the secret word:",
        disabled=st.session_state.puzzle2_solved
    )

    if not st.session_state.puzzle2_solved:
        if st.button("Unlock Final Door"):
            if answer2.strip().lower() == "keyboard":
                st.session_state.puzzle2_solved = True
                st.rerun()
            else:
                st.error("Wrong answer! Try again.")
    else:
        st.success("🎉 Congratulations! You escaped!")
        st.balloons()

# Restart Game button
st.divider()

if st.button("🔄 Restart Game"):
    st.session_state.puzzle1_solved = False
    st.session_state.puzzle2_solved = False
    st.rerun()        