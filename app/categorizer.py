import nltk
import pickle
from pathlib import Path

MODEL_PATH = Path("app/models/classifier.pkl")

# To check if nltk data is available, and download if not
def ensure_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')
        nltk.download('brown')
        nltk.download('punkt')

from textblob.classifiers import NaiveBayesClassifier

# Simple training data: (Task, Category)
# The more examples you add here, the smarter it gets!
train_data = [
    # --- WORK ---
    ('Email team', 'Work'),
    ('Meeting zoom', 'Work'),
    ('Project report', 'Work'),
    ('Office task', 'Work'),
    ('Work on presentation', 'Work'),

    # --- GROCERY (Adding more to balance) ---
    ('Buy milk', 'Grocery'),
    ('Get eggs', 'Grocery'),
    ('Need bread', 'Grocery'),
    ('Grocery shopping list', 'Grocery'),
    ('Buy butter and cheese', 'Grocery'),
    ('Pick up vegetables', 'Grocery'),
    ('Purchase fruit', 'Grocery'),

    # --- HEALTH (Adding more to balance) ---
    ('Take medicine', 'Health'),
    ('Pharmacy meds', 'Health'),
    ('Doctor appointment', 'Health'),
    ('Clinic visit', 'Health'),
    ('Health checkup', 'Health'),
    ('Take vitamins', 'Health'),
    ('Hospital appointment', 'Health'),

    # --- PERSONAL ---
    ('Clean house', 'Personal'),
    ('Laundry day', 'Personal'),
    ('Vacuum floor', 'Personal'),
    ('Pay bills', 'Personal'),
    ('Fix sink', 'Personal')
]

def get_classifier():
    # 1. Check if we already have a saved model
    if MODEL_PATH.exists():
        try:
            with open(MODEL_PATH, "rb") as f:
                print("Loading existing classifier model...")
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading model: {e}. Re-training...")

    # 2. If no model exists, train and save it
    ensure_nltk_data()
    print("Training the brain (this only happens once)...")
    cl = NaiveBayesClassifier(train_data)
    
    # Create directory if it doesn't exist
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(cl, f)
    
    return cl

# Initialize the "Brain"
task_classifier = get_classifier()