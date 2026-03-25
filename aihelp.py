import os
import json
from dotenv import load_dotenv
from openai import OpenAI, api_key
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")

)
def generate_prompt(entry_txt: str) -> str:
    prompt = f"""
    You are a helpful assistant that helps users reflect on their day and provides insights based on their journal entries.
    You also adapt to the personality of the user based ont their entries and act like a friend towards them
    Analyze this journal entry and return JSON with the following keys:
    - mood: A single word describing the user's overall mood (e.g., happy, sad, anxious).
    - reflection: A brief reflection on the user's day, summarizing key events and emotions.
    - follow_up: A thoughtful follow-up question to encourage deeper reflection.
    Rules:
    mood should be short
    reflection should be 1-2 sentences
    be supportive not clinical
    fdollow_up should be open ended and gentle question
    journal entry: {entry_txt}
    """
    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )
    text = response.output_text.strip()
    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        return {"Mood": "unclear", "reflection": text, "follow_up": "What feels the most important to say next"}

    