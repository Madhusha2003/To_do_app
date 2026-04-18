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
            {"label": "GROCERY", "pattern": [{"LOWER": "milk"}]},
            {"label": "GROCERY", "pattern": [{"LOWER": "eggs"}]},
            {"label": "GROCERY", "pattern": [{"LOWER": "chicken"}]},
            {"label": "GROCERY", "pattern": [{"LOWER": "bread"}]},
            {"label": "GROCERY", "pattern": [{"LOWER": "apples"}]},
            {"label": "GROCERY", "pattern": [{"LOWER": "coffee"}]}
        ]
        ruler.add_patterns(patterns)
        
        # Save it to the folder so we never have to do this again!
        nlp.to_disk(SMART_MODEL_DIR)
        return nlp

# Use this in your main.py
nlp = get_nlp()