import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class TaskCategorizer:
    """Handles task text categorization (Work, Grocery, Health, Personal)."""
    def __init__(self, model_path=None):
        self.model = None
        if model_path and os.path.exists(model_path):
            self.model = joblib.load(model_path)

    def predict(self, text):
        if not self.model: raise ValueError("Model not loaded.")
        
        # format input text 
        clean_input = text.strip().lower()
        return self.model.predict([clean_input])[0]

    @staticmethod
    def train(X, y, save_path=None):
        clean_X = [str(text).strip().lower() for text in X]

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
            ('clf', LogisticRegression(max_iter=1000))      
        ])
        
        pipeline.fit(clean_X, y)
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            joblib.dump(pipeline, save_path)
            print(f"Task category model saved to {save_path}")
        return pipeline


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir) 
    
    # Define paths
    model_path = os.path.join(project_root, "app", "models", "task_classifier.pkl")
    data_dir = os.path.join(project_root, "train_model")
    
    print("--- Task Category AI Tool ---")
    print("1. Train Model")
    print("2. Predict (Task Categorization)")
    choice = input("Select option (1/2): ").strip()

    if choice == '1':
        # Look for the massive CSV file
        data_file = os.path.join(data_dir, "massive_task_data.csv")
        
        # Fallback: check if the file is in the current directory instead
        if not os.path.exists(data_file) and os.path.exists("massive_task_data.csv"):
            data_file = "massive_task_data.csv"
            
        if os.path.exists(data_file):
            df = pd.read_csv(data_file).dropna()
            print(f"Training on {len(df)} records...")
            TaskCategorizer.train(df['Task'].tolist(), df['Category'].tolist(), model_path)
        else:
            print(f"Error: Training data not found. Please ensure 'massive_task_data.csv' is in {data_dir} or the current directory.")

    elif choice == '2':
        try:
            model = TaskCategorizer(model_path)
            print("Type 'exit' to quit.")
            while True:
                text = input("\nEnter task description: ").strip()
                if text.lower() == 'exit': break
                
                prediction = model.predict(text)
                print(f"Category: {prediction}")
        except Exception as e:
            print(f"Error loading model: {e}")
            
    else:
        print("Invalid choice.")
