import os
import joblib
from pathlib import Path

class TaskCategorizer:
    """Handles task text categorization (Work, Grocery, Health, Personal)."""
    def __init__(self, model_path=None):
        self.model = None
        if model_path and os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"Model loaded successfully from {model_path}")
        else:
            print(f"Warning: Model NOT found at {model_path}")

    def predict(self, text):
        if not self.model: 
            print("Warning: Model not loaded. Returning UNKNOWN.")
            return "UNKNOWN"
        
        # format input text 
        clean_input = text.strip().lower()
        return self.model.predict([clean_input])[0]
        
    # The train method is in train_model/task_categorizer.py for retraining

# Initialize the classifier
MODEL_PATH = Path(__file__).parent / "models" / "task_classifier.pkl"
task_classifier = TaskCategorizer(str(MODEL_PATH))

# Add a wrapper method to keep compatibility with app.py 
# which calls self.task_classifier.classify(lower_text)
# Wait, let's just add classify method to TaskCategorizer
TaskCategorizer.classify = TaskCategorizer.predict