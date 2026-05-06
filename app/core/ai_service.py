import requests
import json
from datetime import datetime

class AIService:
    def __init__(self, config):
        self.config = config

    def ask(self, prompt):
        mode = self.config.get("mode", "online")
        print(f"\n--- AI REQUEST ({mode.upper()}) ---")
        print(f"PROMPT SENT:\n{prompt}")
        print("-" * 30)

        if mode == "local":
            response = self.ask_local(prompt)
        else:
            response = self.ask_online(prompt)

        print(f"RESPONSE RECEIVED:\n{response}")
        print("--- END AI REQUEST ---\n")
        return response

    def ask_local(self, prompt):
        try:
            model = self.config.get("model", "qwen2.5")
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            return response.json().get("response", "Error: No response from local model.")
        except Exception as e:
            return f"Local AI Error: {e}"

    def ask_online(self, prompt):
        try:
            api_key = self.config.get("api_key")
            model = self.config.get("model") or "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )

            if response.status_code != 200:
                return f"Gemini API Error ({response.status_code}): {response.text}"

            response_json = response.json()
            if "candidates" in response_json:
                return response_json["candidates"][0]["content"]["parts"][0]["text"]
            return "Gemini Error: No candidates in response."

        except Exception as e:
            return f"Online AI Error: {str(e)}"


# ──────────────────────────────────────────────────────────
# PROMPT BUILDERS
# ──────────────────────────────────────────────────────────

def build_chat_prompt(tasks, mode="online", user_prompt="", rag_context=""):
    now = datetime.now()
    task_list = "\n".join(
        f"- [{t.get('priority','?')}] {t['task_name']} ({t.get('category','')})"
        for t in tasks
    ) or "None"

    context_block = f"\nRELEVANT DOCUMENTS:\n{rag_context}\n" if rag_context.strip() else ""

    if mode == "local":
        return (
            f"You are Nova, an AI assistant.\n"
            f"Current Date: {now.strftime('%A, %B %d, %Y')}\n\n"
            f"--- START OF KNOWLEDGE BASE CONTEXT ---\n"
            f"{rag_context if rag_context.strip() else 'No relevant document found.'}\n"
            f"--- END OF KNOWLEDGE BASE CONTEXT ---\n\n"
            f"--- START OF USER TASK LIST ---\n"
            f"{task_list}\n"
            f"--- END OF USER TASK LIST ---\n\n"
            f"USER QUESTION: {user_prompt}\n\n"
            f"INSTRUCTION: Answer using the content above. Use markdown (bold, lists) to make it readable. Be brief but helpful.\n"
            f"Nova:"
        )
    else:
        return (
            f"You are Nova, a helpful productivity assistant.\n"
            f"Today's Date: {now.strftime('%A, %B %d, %Y')}\n"
            f"{context_block}"
            f"\nCURRENT TASKS:\n{task_list}\n"
            f"\nUser Question: {user_prompt}\n"
            f"Nova (Use markdown for formatting. Be brief and use provided info):"
        )

def build_task_prompt(text, mode="online", rag_context=""):
    now = datetime.now()
    context_block = f"\nCONTEXT:\n{rag_context}\n" if rag_context.strip() else ""

    if mode == "local":
        return (
            f"Task: \"{text}\"\n"
            f"Today: {now.strftime('%b %d, %Y')}\n"
            f"{context_block}\n"
            f"INSTRUCTION: Extract task details into JSON.\n"
            f"Valid Categories: WORK, PERSONAL, GROCERY, HEALTH, TRAVEL, SHOPPING, FINANCE, STUDY, REMINDER\n"
            f"Valid Priorities: HIGH, MEDIUM, LOW\n"
            f"\nEXAMPLE:\n"
            f"Input: \"Buy milk tomorrow 5pm\"\n"
            f"Output: {{\n"
            f'  "category": "GROCERY",\n'
            f'  "task_name": "Buy milk",\n'
            f'  "date_info": "{now.strftime("%b %d, %Y")}",\n'
            f'  "time_info": "05:00 PM",\n'
            f'  "priority": "MEDIUM"\n'
            f"}}\n"
            f"\nRequired JSON Format:\n"
            f"{{\n"
            f'  "category": "ONE_OF_THE_LIST_ABOVE",\n'
            f'  "task_name": "CLEANED_TASK_DESCRIPTION",\n'
            f'  "date_info": "MMM DD, YYYY",\n'
            f'  "time_info": "HH:MM AM/PM",\n'
            f'  "priority": "ONE_OF_THE_PRIORITIES_ABOVE"\n'
            f"}}\n"
            f"OUTPUT ONLY THE JSON. NO OTHER TEXT."
        )
    else:
        return (
            f"Extract task details from: \"{text}\"\n"
            f"Current Date: {now.strftime('%b %d, %Y')}\n"
            f"{context_block}"
            f"\nOutput ONLY JSON:\n"
            f"{{\n"
            f'  "category": "WORK/PERSONAL/GROCERY/HEALTH/TRAVEL/SHOPPING/FINANCE/STUDY/REMINDER",\n'
            f'  "task_name": "clean name",\n'
            f'  "date_info": "MMM DD, YYYY",\n'
            f'  "time_info": "HH:MM AM/PM",\n'
            f'  "priority": "HIGH/MEDIUM/LOW"\n'
            f"}}"
        )
