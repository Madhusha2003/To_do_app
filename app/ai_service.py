import requests
import json

class AIService:
    def __init__(self, config):
        self.config = config

    def ask(self, prompt):
        if self.config.get("mode") == "local":
            return self.ask_local(prompt)
        else:
            return self.ask_online(prompt)

    def ask_local(self, prompt):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.config.get("model", "qwen2.5"),
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json().get("response", "Error: No response from local model.")
        except Exception as e:
            return f"Local AI Error: {e}"

    def ask_online(self, prompt):
        try:
            api_key = self.config.get("api_key")
            # Ensure model name is not empty
            model = self.config.get("model") or "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                try:
                    err_data = response.json()
                    err_msg = err_data.get("error", {}).get("message", response.text)
                    return f"Gemini API Error ({response.status_code}): {err_msg}"
                except:
                    return f"Gemini API Error ({response.status_code}): {response.text[:100]}"

            response_json = response.json()
            
            if "candidates" in response_json:
                return response_json["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"Gemini Error: No candidates in response."
                
        except Exception as e:
            return f"Online AI Error: {str(e)}"

def build_chat_prompt(tasks, mode="online", user_prompt=""):
    if mode == "local":
        # More concise prompt for local models
        text = "You are Nova, a helpful productivity assistant. Be brief and direct.\n\nTASKS:\n"
        for t in tasks:
            text += f"- {t['task_name']} ({t.get('category','')}) {t.get('date_info','')}\n"
        text += f"\nUser: {user_prompt}\nPlan:"
        return text
    else:
        # Richer prompt for online models like Gemini
        text = """
You are Nova, a premium productivity AI assistant.

Your mission:
- Analyze the user's task list
- Prioritize based on urgency and importance
- Provide a clear, actionable plan
- Keep the tone professional but encouraging

TASK LIST:
"""
        for t in tasks:
            text += f"- {t['task_name']} | {t.get('category','')} | {t.get('date_info','')}\n"

        text += f"\nUser Request: {user_prompt}\n"
        text += "\nGive a simple action plan for today."
        return text

def build_task_prompt(text, mode="online"):
    if mode == "local":
        # Improved low-parameter prompt with stronger examples
        return f"""
You are a task classifier.

Your job:
1. Understand the task meaning
2. Choose the BEST category
3. Clean the task name

Categories:
- GROCERY = food, supermarket, household essentials
- PERSONAL = personal tasks, calls, appointments
- WORK = job, office, projects
- HEALTH = exercise, doctor, medicine
- TRAVEL = transport, trips, tickets
- SHOPPING = buying clothes, gadgets, general shopping
- FINANCE = bills, banking, payments
- STUDY = school, learning, homework
- REMINDER = general reminders

Examples:
"go shopping" -> SHOPPING
"buy groceries" -> GROCERY
"pay electricity bill" -> FINANCE
"study math" -> STUDY
"gym workout" -> HEALTH
"book flight ticket" -> TRAVEL

Task:
"{text}"

Rules:
- Focus on meaning
- "shopping" means SHOPPING unless groceries/food
- "study" only for education
- Output ONLY JSON
- No extra text

JSON:
{{"category":"CATEGORY","task_name":"cleaned task"}}
"""
    else:
        # Full extraction for online model
        return f"""
You are Nova, an AI assistant. The user wants to add a task to their to-do list.
You must determine the best category for this task, extract the actual task description, and parse any date or time mentioned.
Valid categories: GROCERY, PERSONAL, WORK, HEALTH, TRAVEL, SHOPPING, FINANCE, STUDY, REMINDER.
Decide date base on today , tommorrow , next monday etc. If no date is mentioned, then the task is for today.

Task input: "{text}"

Output ONLY this JSON format and nothing else:
{{
  "category": "CATEGORY_NAME",
  "task_name": "Task without date/time words",
  "date_info": "MMM DD, YYYY" (or empty string if none),
  "time_info": "HH:MM AM/PM" (or empty string if none)
}}
"""
