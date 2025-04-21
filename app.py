# app.py

import streamlit as st
import random
import matplotlib.pyplot as plt
from db_utils import init_db, add_move, get_user_history

init_db()

st.title("🤖 AI vs You: Rock Paper Scissors with Memory")

username = st.text_input("Enter your name to begin:", value="guest")

if username:
    choices = ["Rock", "Paper", "Scissors"]
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

        def predict_user_move(history, window_size=5):
            if not history:
                return random.choice(choices)
            
            # Look at last `window_size` moves
            recent_moves = [row[0] for row in history[-window_size:]]
            
            if not recent_moves:
                return random.choice(choices)
            
            # Count frequency in the window
            move_counts = {move: recent_moves.count(move) for move in choices}
            predicted_move = max(move_counts, key=move_counts.get)

            # AI counters the predicted move
            counter_moves = {"Rock": "Paper", "Paper": "Scissors", "Scissors": "Rock"}
            return counter_moves[predicted_move]

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