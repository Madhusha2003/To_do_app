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
            model = self.config.get("model", "gemini-1.5-flash")
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
            response_json = response.json()
            
            if "candidates" in response_json:
                return response_json["candidates"][0]["content"]["parts"][0]["text"]
            else:
                error_msg = response_json.get("error", {}).get("message", "Unknown error")
                return f"Gemini Error: {error_msg}"
                
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
