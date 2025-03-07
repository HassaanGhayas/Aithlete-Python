import streamlit as st
import google.generativeai as genai

# Setting Title and Icon
st.set_page_config(page_title="Fitbot", page_icon="./assets/chat.svg", layout='wide')

# Load API Key from secrets
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Function for Question Processing
def ask_fitness_bot(user_query):
    prompt = f"""
    You are an AI fitness expert named Aithlete. You provide expert advice on:
    - Strength training
    - Weight loss
    - Muscle gain
    - Nutrition and meal planning
    - Recovery and stretching
    - Workout schedules and routines
    
    Please provide detailed, practical, and **evidence-based** fitness guidance.
    
    User Question: {user_query}
    """
    model = genai.GenerativeModel("gemini-1.5-pro")  # Use "gemini-1.5-flash" for faster responses
    response = model.generate_content(prompt)
    
    return response.text if response else "⚠️ Sorry, I couldn't generate a response."

# Streamlit UI
st.title(":orange[Aithlete:] Your AI Fitness Trainer")
st.write("_Get expert fitness advice instantly!_")

# User Question to be specific
user_input = st.text_area("💬 Ask me anything about fitness:", placeholder="Example: How can I build muscle fast?")
if st.button("Ask Aithlete"):
    if user_input.strip():
        st.subheader("🤖 Aithlete's Advice:")
        response = ask_fitness_bot(user_input)
        st.write(response)
    else:
        st.warning("⚠️ Please enter a question.")
