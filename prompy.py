import random
prompts = [
    "What made you smile today?",
    "Describe a dream you had recently.",
    "What would you tell your younger self?",
    "What’s one goal you want to achieve this month?",
    "Write about a place that makes you feel safe."
    "How are you feeling today?"
]
def random_prompt():
    random_choice = random.choice(prompts)
    return random_choice
