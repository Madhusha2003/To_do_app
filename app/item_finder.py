import spacy 
from pathlib import Path

# Path of customized AI brain
SMART_MODEL_DIR = Path("app/models/smart_nlp_model")

def get_nlp():
    if SMART_MODEL_DIR.exists():
        # Load your already-customized model from the folder
        print("Loading customized spaCy model...")
        return spacy.load(SMART_MODEL_DIR)
    else:
        # First time setup
        print("Creating customized spaCy model (first time only)...")
        # Disable unneeded parts to save RAM and speed up
        nlp = spacy.load("en_core_web_sm", disable=["parser", "attribute_ruler", "lemmatizer"])
        
        # Add your custom grocery rules
        config = {"overwrite_ents": True}
        ruler = nlp.add_pipe("entity_ruler", config=config)
        patterns = [

            # ================= GROCERY =================
            {"label": "GROCERY", "pattern": [{"LEMMA": "milk"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "eggs"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "bread"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "rice"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "chicken"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "fish"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "onion"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "tomato"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "apple"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "banana"}]},
            {"label": "GROCERY", "pattern": [{"LEMMA": "coffee"}]},

            # ================= FINANCE =================
            {"label": "FINANCE", "pattern": [{"LEMMA": "pay"}]},
            {"label": "FINANCE", "pattern": [{"LEMMA": "bill"}]},
            {"label": "FINANCE", "pattern": [{"LEMMA": "loan"}]},
            {"label": "FINANCE", "pattern": [{"LEMMA": "transfer"}]},
            {"label": "FINANCE", "pattern": [{"LEMMA": "salary"}]},
            {"label": "FINANCE", "pattern": [{"LEMMA": "budget"}]},

            # ================= STUDY =================
            {"label": "STUDY", "pattern": [{"LEMMA": "study"}]},
            {"label": "STUDY", "pattern": [{"LEMMA": "revise"}]},
            {"label": "STUDY", "pattern": [{"LEMMA": "assignment"}]},
            {"label": "STUDY", "pattern": [{"LEMMA": "exam"}]},
            {"label": "STUDY", "pattern": [{"LEMMA": "homework"}]},
            {"label": "STUDY", "pattern": [{"LEMMA": "notes"}]},

            # ================= REMINDER =================
            {"label": "REMINDER", "pattern": [{"LEMMA": "remind"}]},
            {"label": "REMINDER", "pattern": [{"LEMMA": "reminder"}]},
            {"label": "REMINDER", "pattern": [{"LEMMA": "notify"}]},
            {"label": "REMINDER", "pattern": [{"LEMMA": "alert"}]},
            {"label": "REMINDER", "pattern": [{"LEMMA": "alarm"}]},

            # ================= SHOPPING / GENERAL BUY =================
            {"label": "SHOPPING", "pattern": [{"LEMMA": "buy"}]},
            {"label": "SHOPPING", "pattern": [{"LEMMA": "purchase"}]},
            {"label": "SHOPPING", "pattern": [{"LEMMA": "order"}]},

            # ================= HEALTH =================
            {"label": "HEALTH", "pattern": [{"LEMMA": "medicine"}]},
            {"label": "HEALTH", "pattern": [{"LEMMA": "doctor"}]},
            {"label": "HEALTH", "pattern": [{"LEMMA": "hospital"}]},
            {"label": "HEALTH", "pattern": [{"LEMMA": "fever"}]},
            {"label": "HEALTH", "pattern": [{"LEMMA": "pain"}]},

            # ================= TRAVEL =================
            {"label": "TRAVEL", "pattern": [{"LEMMA": "ticket"}]},
            {"label": "TRAVEL", "pattern": [{"LEMMA": "flight"}]},
            {"label": "TRAVEL", "pattern": [{"LEMMA": "hotel"}]},
            {"label": "TRAVEL", "pattern": [{"LEMMA": "travel"}]},
        ]
        ruler.add_patterns(patterns)
        
        # Save it to the folder so we never have to do this again!
        nlp.to_disk(SMART_MODEL_DIR)
        return nlp

# Use this in your main.py
nlp = get_nlp()