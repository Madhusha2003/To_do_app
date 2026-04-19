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

    # =========================
    # 🧑‍💻 WORK (25)
    # =========================
    ('email', 'Work'),
    ('meeting', 'Work'),
    ('report', 'Work'),
    ('code', 'Work'),
    ('project', 'Work'),

    ('send email', 'Work'),
    ('team meeting', 'Work'),
    ('write report', 'Work'),
    ('fix bug', 'Work'),
    ('review code', 'Work'),

    ('finish assignment', 'Work'),
    ('prepare presentation', 'Work'),
    ('update project file', 'Work'),
    ('attend online meeting', 'Work'),
    ('debug application error', 'Work'),

    ('send email to manager', 'Work'),
    ('complete project documentation', 'Work'),
    ('work on client report', 'Work'),
    ('join zoom meeting with team', 'Work'),
    ('push code to github repository', 'Work'),

    ('fix bugs and deploy application', 'Work'),
    ('prepare slides for presentation tomorrow', 'Work'),
    ('complete final year project report', 'Work'),
    ('attend client meeting and take notes', 'Work'),
    ('review pull request and merge code', 'Work'),


    # =========================
    # 🛒 GROCERY (25)
    # =========================
    ('milk', 'Grocery'),
    ('eggs', 'Grocery'),
    ('bread', 'Grocery'),
    ('rice', 'Grocery'),
    ('fruits', 'Grocery'),

    ('buy milk', 'Grocery'),
    ('get eggs', 'Grocery'),
    ('buy bread', 'Grocery'),
    ('pick vegetables', 'Grocery'),
    ('buy rice packet', 'Grocery'),

    ('buy milk and bread', 'Grocery'),
    ('get fruits from shop', 'Grocery'),
    ('purchase vegetables', 'Grocery'),
    ('buy snacks for home', 'Grocery'),
    ('shop for groceries', 'Grocery'),

    ('buy milk eggs and bread', 'Grocery'),
    ('get vegetables for dinner', 'Grocery'),
    ('purchase fruits and snacks', 'Grocery'),
    ('buy groceries for the week', 'Grocery'),
    ('shop at supermarket for food items', 'Grocery'),

    ('buy milk eggs bread and cheese', 'Grocery'),
    ('get groceries for family dinner tonight', 'Grocery'),
    ('purchase vegetables and fruits for cooking', 'Grocery'),
    ('buy food items from supermarket after work', 'Grocery'),
    ('pick up groceries including milk and snacks', 'Grocery'),


    # =========================
    # 🏥 HEALTH (25)
    # =========================
    ('doctor', 'Health'),
    ('medicine', 'Health'),
    ('hospital', 'Health'),
    ('gym', 'Health'),
    ('health', 'Health'),

    ('take medicine', 'Health'),
    ('visit doctor', 'Health'),
    ('go hospital', 'Health'),
    ('morning workout', 'Health'),
    ('take vitamins', 'Health'),

    ('doctor appointment', 'Health'),
    ('take daily medicine', 'Health'),
    ('go to the gym', 'Health'),
    ('health checkup', 'Health'),
    ('visit clinic today', 'Health'),

    ('schedule doctor appointment', 'Health'),
    ('take medicine after meal', 'Health'),
    ('go for morning workout session', 'Health'),
    ('complete health checkup at clinic', 'Health'),
    ('buy medicine from pharmacy', 'Health'),

    ('take medicine and rest at home', 'Health'),
    ('visit doctor for regular checkup', 'Health'),
    ('go to gym and do exercise', 'Health'),
    ('schedule appointment with specialist doctor', 'Health'),
    ('take vitamins and drink water regularly', 'Health'),


    # =========================
    # 🏠 PERSONAL (25)
    # =========================
    ('clean', 'Personal'),
    ('laundry', 'Personal'),
    ('bills', 'Personal'),
    ('home', 'Personal'),
    ('room', 'Personal'),

    ('clean room', 'Personal'),
    ('do laundry', 'Personal'),
    ('pay bills', 'Personal'),
    ('wash clothes', 'Personal'),
    ('organize desk', 'Personal'),

    ('clean the house', 'Personal'),
    ('do laundry today', 'Personal'),
    ('pay electricity bills', 'Personal'),
    ('tidy up room', 'Personal'),
    ('clean kitchen', 'Personal'),

    ('organize my study desk', 'Personal'),
    ('do laundry and wash clothes', 'Personal'),
    ('clean house before guests arrive', 'Personal'),
    ('pay water and electricity bills online', 'Personal'),
    ('vacuum and clean living room', 'Personal'),

    ('clean the house and wash clothes today', 'Personal'),
    ('organize room and arrange study materials', 'Personal'),
    ('pay all pending bills before deadline', 'Personal'),
    ('do laundry and clean kitchen properly', 'Personal'),
    ('deep clean the house this weekend', 'Personal'),

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