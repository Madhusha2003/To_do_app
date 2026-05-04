import sys
import os
sys.path.append(os.path.abspath("app"))
from categorizer import task_classifier

test_tasks = [
    "buy some milk",
    "visit the doctor",
    "finish the project report",
    "clean my room",
    "go to the gym",
    "prepare for meeting"
]

for task in test_tasks:
    print(f"Task: {task} -> Category: {task_classifier.classify(task)}")
