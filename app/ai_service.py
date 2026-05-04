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
    text = "You are a productivity assistant.\n\nTasks:\n"
    for t in tasks:
        if isinstance(t, dict):
            title = t.get("task_name", "")
            category = t.get("category", "")
            text += f"- {title} (category: {category})\n"
        else:
            text += f"- {t.task_name} (category: {t.category})\n"
    
    text += f"\n{user_prompt}"
    return text
