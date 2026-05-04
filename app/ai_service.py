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
            headers = {
                "Authorization": f"Bearer {self.config.get('api_key')}"
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.config.get("model", "gpt-4o-mini"),
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Online AI Error: {e}"

def build_prompt(tasks, user_prompt=""):
    text = """
You are Nova, a productivity AI assistant.

Your job:
- Prioritize tasks
- Suggest what to do first
- Be short and clear
- Focus on urgency and importance

TASK LIST:
"""

    for t in tasks:
        text += f"- {t['task_name']} | {t.get('category','')} | {t.get('date_info','')}\n"

    text += f"\nUser request: {user_prompt}\n"

    text += "\nGive a simple action plan for today."

    return text
