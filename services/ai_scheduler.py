import google.generativeai as genai
from config.settings import GEMENI_API_KEY
import json
import re


genai.configure(api_key=GEMENI_API_KEY)

def parse_gemini_response(response_text):
    """
    Extracts the first JSON array from Gemini response text.
    Cleans code fences and extra whitespace.
    """
    # Remove ```json or ``` wrapping
    cleaned = re.sub(r"```json|```", "", response_text, flags=re.IGNORECASE).strip()

    # Extract first JSON array
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
    else:
        print("No JSON array found in response.")
        return []
    
def generate_study_schedule(free_slots, duration_minutes, break_minutes, topics, num_days):
    free_str = "\n".join([f"{s[0]} to {s[1]}" for s in free_slots])
    topics_str = "\n".join([f"{t['name']} (difficulty {t['difficulty']}, deadline {t['deadline']})" for t in topics])
    """
    Generate a study schedule using AI based on topics and constraints.
    Args:
        topics (list): List of study topics.
        constraints (dict): Scheduling constraints (dates, hours, etc).
    Returns:
        pd.DataFrame: DataFrame with scheduled sessions.
    """
    prompt = f"""
            You are a study schedule planner that uses evidence-based learning strategies.
            Generate a JSON study plan for the given topics and timeframe.

            Guidelines:
            1. Use **spaced repetition**: review key topics multiple times with increasing intervals.
            2. Avoid scheduling long blocks of study one after another — include short breaks {break_minutes} and longer breaks after 2–3 sessions.
            3. Consider **fatigue and focus capacity**: no more than 90 minutes of study without a break.
            4. Mix subjects to improve learning (interleaving).
            5. don't schedule the breaks but put the time gap between breaks and long breaks.
            6. Ensure the schedule is realistic and sustainable, not overwhelming.
            7. Output only valid JSON with this structure:
            [
                {{"topic": "Math", "start": "2025-08-21T09:00", "end": "2025-08-21T09:50"}}
            ]
            I have the following free time slots available:
            {free_str} 

            Topics:
            {topics_str}

            I want each session to be {duration_minutes} minutes long, with {break_minutes} minute breaks in between.

            Now generate the study schedule for {num_days}.
            """


    model= genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    print("=== Gemini raw response ===")
    print(response.text)

    # Use the helper to parse safely
    schedule = parse_gemini_response(response.text)

    if not schedule:
        print("No sessions to add.")
    else:
        print(f"{len(schedule)} sessions parsed successfully.")
        return schedule
    
     
