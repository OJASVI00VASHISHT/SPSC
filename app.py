# app.py
import streamlit as st
import random
import matplotlib.pyplot as plt
from collections import Counter
from db_utils import init_db, add_move, get_user_history

init_db()

st.title("🤖 AI vs You: Rock Paper Scissors with Memory")

username = st.text_input("Enter your name to begin:", value="guest")

if username:
    choices = ["Rock", "Paper", "Scissors"]
    counter_moves = {"Rock": "Paper", "Paper": "Scissors", "Scissors": "Rock"}
    user_choice = None

    st.markdown("### Choose Your Move:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🪨 Rock"):
            user_choice = "Rock"
    with col2:
        if st.button("📄 Paper"):
            user_choice = "Paper"
    with col3:
        if st.button("✂️ Scissors"):
            user_choice = "Scissors"

    if user_choice:
        history = get_user_history(username)

        def predict_user_move(history):
            if not history or len(history) < 3:
                return random.choice(choices)
            
            # Get all user moves
            user_moves = [move[0] for move in history]
            
            # Pattern detection for repeated moves
            last_three = user_moves[-3:]
            if len(set(last_three)) == 1:  # All same moves
                return counter_moves[last_three[0]]
            
            # Check for simple patterns (like Rock-Paper-Scissors repeating)
            if len(user_moves) >= 3:
                pattern = user_moves[-3:]
                if pattern == ["Rock", "Paper", "Scissors"]:
                    return "Rock"  # Predicts next in sequence would be Rock again
                if pattern == ["Paper", "Scissors", "Rock"]:
                    return "Paper"
                if pattern == ["Scissors", "Rock", "Paper"]:
                    return "Scissors"
            
            # Frequency analysis with different window sizes
            for window in [5, 10, len(user_moves)]:
                if len(user_moves) >= window:
                    window_moves = user_moves[-window:]
                    freq = Counter(window_moves)
                    most_common = freq.most_common(1)[0][0]
                    # Add some randomness to not be completely predictable
                    if random.random() < 0.8:  # 80% chance to counter most common
                        return counter_moves[most_common]
            
            # Fallback to random if no clear pattern
            return random.choice(choices)

        ai_choice = predict_user_move(history)

        if user_choice == ai_choice:
            result = "Draw"
        elif (
            (user_choice == "Rock" and ai_choice == "Scissors") or
            (user_choice == "Paper" and ai_choice == "Rock") or
            (user_choice == "Scissors" and ai_choice == "Paper")
        ):
            result = "Win"
        else:
            result = "Loss"

        add_move(username, user_choice, ai_choice, result)

        st.write(f"🧠 AI chose: **{ai_choice}**")
        st.subheader(f"🔔 Result: **{result}**")

        full_history = get_user_history(username)
        if full_history:
            user_moves = [row[0] for row in full_history]
            ai_moves = [row[1] for row in full_history]
            results = [row[2] for row in full_history]

            win_count = results.count("Win")
            loss_count = results.count("Loss")
            draw_count = results.count("Draw")

            st.markdown("### 📈 Your Game Stats")
            st.write(f"✅ Wins: {win_count}")
            st.write(f"❌ Losses: {loss_count}")
            st.write(f"➖ Draws: {draw_count}")

            move_counts = {move: user_moves.count(move) for move in choices}
            fig, ax = plt.subplots()
            ax.pie(move_counts.values(), labels=move_counts.keys(), autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

            st.markdown("### 🧠 AI's Move History")
            st.write(ai_moves)
        else:
            st.write("No game history yet. Play more games to see statistics!")