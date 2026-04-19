import json
from pathlib import Path

DATA_FILE = Path("data/tasks.json")

def load_tasks():
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading tasks: {e}")
        return []

def save_tasks(tasks):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
    except Exception as e:
        print(f"Error saving tasks: {e}")

def delete_task(task_name):
    tasks = load_tasks()
    for task in tasks:
        if task["task_name"] == task_name:
            tasks.remove(task)
            save_tasks(tasks)
            return True
    return False
