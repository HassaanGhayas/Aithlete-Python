import streamlit as st
import google.generativeai as genai
import io
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Set page title and icon
st.set_page_config(
    page_title="Aithlete", page_icon="./assets/dumbell.svg", layout="wide"
)

# Load Gemini API Key from secrets.toml
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Page title with a small description
st.title(":violet[Aithlete] 💪")
st.write("#### Welcome to AiTHLETE – _Your AI-Powered Personal Trainer!_")
st.divider()


# Function to create workout plan from Gemini API
def create_workout_plan(goal, level, commitment, duration, workout_types, equipment):
    prompt = f"""Generate a structured workout plan in JSON format based on these preferences:

    Fitness Goal: {goal}
    Fitness Level: {level}
    Commitment: {commitment}
    Workout Types: {workout_types}
    Available Equipment: {equipment}
    Plan Duration: {duration}

    JSON Structure:
    The response must be a valid JSON object. Do not include any additional text, formatting, or backticks. The JSON should follow this structure:

    {{"Day 1": {{"exercises": [{{"name": "Exercise Name", "duration": "Duration", "instructions": "Instructions"}}, ...]}}, "Day 2": {{"exercises": [...]}}, ...}}

    Each day will have multiple exercises, where:
    - "name" is the exercise name.
    - "duration" specifies the workout time (e.g., "10 mins", "30 secs").
    - "instructions" provide details on execution.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return (
        clean_json(response.text)
        if response
        else st.error("Failed to create Personalized Plan")
    )


# Function to clean JSON response
def clean_json(json_string):
    json_string = json_string.strip().strip("```").strip("json").strip()
    try:
        json.loads(json_string)
        return json_string
    except json.JSONDecodeError:
        print("Invalid JSON")
        return "Invalid JSON"

# Function to add Footer i.e © 2024 Aithlete
def add_footer(canvas):
    width, height = A4
    footer_y = 40  
    canvas.setFillColor(HexColor("#2F3C7E")) 
    canvas.setFont("Helvetica", 10)
    canvas.drawCentredString(
        width / 2, footer_y, "© 2024 Aithlete | Your AI-Powered Workout Planner"
    )
    canvas.setFillColor(HexColor("#000000"))  # Reset text color


def draw_background(canvas):
    width, height = A4
    canvas.setFillColor(HexColor("#FBEAEB")) 
    canvas.rect(0, 0, width, height, fill=1, stroke=0)


def wrap_text(canvas, text, x, y, max_width):
    """Wraps text within the specified max_width."""
    styles = getSampleStyleSheet()
    p = Paragraph(text, styles["Normal"])
    w, h = p.wrapOn(canvas, max_width, 200)  
    p.drawOn(canvas, x, y - h)
    return h 


def generate_workout_pdf(data):
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    canvas.setTitle("Workout Plan")
    width, height = A4
    MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM = 50, 50, 80, 50
    CONTENT_WIDTH = width - MARGIN_LEFT - MARGIN_RIGHT
    CONTENT_HEIGHT = height - MARGIN_TOP - MARGIN_BOTTOM

    # First Page
    draw_background(canvas)
    canvas.setFillColor(HexColor("#2F3C7E")) 
    canvas.setFont("Helvetica-Bold", 60)
    canvas.drawCentredString(width / 2, height - MARGIN_TOP - 40, "Aithlete")
    canvas.setFont("Helvetica", 14)
    canvas.setFillColor(HexColor("#333333")) 
    canvas.drawCentredString(
        width / 2, height - MARGIN_TOP - 80, "Your AI-Powered Workout Planner"
    )
    canvas.showPage()

    draw_background(canvas)
    add_footer(canvas) 

    # Title Section
    canvas.setFont("Helvetica-Bold", 24)
    canvas.setFillColor(HexColor("#2F3C7E"))
    canvas.drawCentredString(
        width / 2, height - MARGIN_TOP, '"Consistency Beats Intensity"'
    )

    # Set correct y_position only once
    y_position = height - MARGIN_TOP - 40

    # Try-Catch block for error handling
    try:
        workout_data = json.loads(data) if isinstance(data, str) else data
        for day, content in workout_data.items():
            if y_position < MARGIN_BOTTOM + 50:  # Ensure proper spacing
                canvas.showPage()
                draw_background(canvas)
                add_footer(canvas)
                y_position = height - MARGIN_TOP
            else: 
                y_position -= 20

            # Add Day Title
            canvas.setFont("Helvetica-Bold", 18)
            canvas.setFillColor(HexColor("#2F3C7E"))
            canvas.drawString(MARGIN_LEFT, y_position, f"~ {day}")
            y_position -= 20  # Space for exercises

            # Add Exercises (Bulleted List)
            for exercise in content["exercises"]:
                if y_position < MARGIN_BOTTOM + 50:
                    canvas.showPage()
                    draw_background(canvas)
                    add_footer(canvas)
                    y_position = height - MARGIN_TOP

                canvas.setFillColor(HexColor("#333333"))
                canvas.setFont("Helvetica-Bold", 14)  # Larger font for exercise name
                canvas.drawString(
                    MARGIN_LEFT + 20, y_position, f"- Name: {exercise['name']}"
                )
                y_position -= 15

                canvas.setFont(
                    "Helvetica", 12
                )  # Smaller font for duration & instructions
                canvas.drawString(
                    MARGIN_LEFT + 40,
                    y_position,
                    f"- Duration: {exercise.get('duration', 'N/A')}",
                )
                y_position -= 15
                y_position -= wrap_text(
                    canvas,
                    f"- Instructions: {exercise.get('instructions', 'No instructions provided.')}",
                    MARGIN_LEFT + 40,
                    y_position,
                    CONTENT_WIDTH - 80,
                )
                y_position -= 25  # More space before the next exercise

        canvas.save()
        buffer.seek(0)
        return buffer
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON data provided to generate_workout_pdf")
        return None
    except Exception as e:
        print(f"⚠️ An error occurred during PDF generation: {e}")
        return None


# User input form
with st.form("workout_plan_form"):
    st.subheader("🏋️‍♂️ Customize Your Workout Plan")
    fitness_goal = st.selectbox(
        "🔹Fitness Goal", ["General Fitness", "Muscle Gain", "Fat loss"]
    )
    fitness_level = st.pills(
        "🔹Your Current Fitness Level", ["Beginner", "Intermediate", "Advanced"]
    )
    commitment = st.select_slider("🔹Commitment", ["15 Mins", "30 Mins", "45 Mins"])
    workout_types = st.multiselect(
        "🔹Preferred Workout Types", ["Strength Training", "Yoga", "Cardio", "HIIT"]
    )
    equipment = st.segmented_control(
        "🔹Available Equipment",
        ["Bodyweight Only", "Dumbbells", "Resistance Bands", "Full Gym"],
    )
    plan_duration = st.pills("🔹Plan Duration (might not work)", ["7 Days", "14 Days", "30 Days"])
    submit = st.form_submit_button("Generate Plan 📜")

# Submit Functionality
if submit:
    if not (
        fitness_goal
        and fitness_level
        and commitment
        and workout_types
        and equipment
        and plan_duration
    ):
        st.error("⚠️ Please fill all fields")
    else:
        st.success("✅ Your personalized workout plan is being generated!")
        workout_plan = create_workout_plan(
            fitness_goal,
            fitness_level,
            commitment,
            plan_duration[0],
            workout_types,
            equipment,
        )
        if workout_plan:
            st.subheader("📋 Your AI-Generated Workout Plan:")
            st.json(workout_plan)
            pdf_buffer = generate_workout_pdf(workout_plan)
            st.download_button(
                "📥 Download Workout Plan as PDF",
                data=pdf_buffer,
                file_name="workout_plan.pdf",
                mime="application/pdf",
            )
