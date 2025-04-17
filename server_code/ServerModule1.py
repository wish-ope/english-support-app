import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
import nltk

# Tải WordNet và khởi tạo spaCy
try:
    nltk.download('wordnet', quiet=True)
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("wordnet", after="tagger")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("wordnet", after="tagger")

@anvil.server.callable
def get_word_info(vocab_input):
    if not vocab_input or not vocab_input.strip():
        return "Error: Please enter a valid word."
    
    doc = nlp(vocab_input.strip())
    result = []
    for synset in doc[0]._.wordnet.synsets():
        result.append(f"Definition: {synset.definition()}")
        examples = synset.examples()
        result.append(f"Total Example: {len(examples)}")
        if examples:
            result.append(f"Example: {examples[0]}")
        else:
            result.append(f"Example: No examples available")
        for lemma in synset.lemma_names():
            result.append(f"Synonym: {lemma}")
        result.append("")
    
    if not result:
        return f"No synsets found for the word '{vocab_input}'."
    
    return "\n".join(result)