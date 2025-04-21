# app.py
import streamlit as st
import random
import matplotlib.pyplot as plt
from collections import Counter, deque
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
            if not history:
                return random.choice(choices)
            
            user_moves = [move[0] for move in history]
            last_move = user_moves[-1]
            
            # 1. Immediate punishment for repeating same move
            if len(user_moves) >= 2 and user_moves[-1] == user_moves[-2]:
                return counter_moves[last_move]
            
            # 2. Detect longer streaks (3+ repeats)
            streak_length = 1
            for i in range(2, min(5, len(user_moves)) + 1):
                if user_moves[-i] == last_move:
                    streak_length += 1
                else:
                    break
            
            if streak_length >= 3:
                return counter_moves[last_move]
            
            # 3. Frequency analysis with weighted randomness
            move_counts = Counter(user_moves)
            total = sum(move_counts.values())
            probabilities = {
                move: (count/total)*0.7 + 0.1  # 70% weight to history, 10% base chance
                for move, count in move_counts.items()
            }
            
            # Add missing moves with base probability
            for move in choices:
                if move not in probabilities:
                    probabilities[move] = 0.1
            
            # Normalize probabilities
            total_prob = sum(probabilities.values())
            probabilities = {k: v/total_prob for k, v in probabilities.items()}
            
            # Choose counter to predicted move
            predicted = random.choices(
                list(probabilities.keys()),
                weights=list(probabilities.values()),
                k=1
            )[0]
            
            return counter_moves[predicted]

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