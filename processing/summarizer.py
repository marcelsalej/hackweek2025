import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-pro")

def generate_summary(context: str):
    prompt = f"""
    Summarize the following engineering team activity into Yesterday, Blockers, and Today based on the provided data. Infer the categories from the context.

    Context:
    ---
    {context}
    ---

    Format the output in Markdown:
    **Yesterday:**
    - List of tasks completed or worked on.

    **Today:**
    - List of tasks planned for today.

    **Blockers:**
    - List of any impediments mentioned.
    """
    response = model.generate_content(prompt)
    return response.text